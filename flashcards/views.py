from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, Q, Sum
from django.utils import timezone
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.http import url_has_allowed_host_and_scheme
from . import pinyin_text, scheduler, study_queue
from .models import Word, UserWord, UserProfile, Review, Story, SavedWord, Dialogue
from .study_queue import ensure_user_words
from collections import Counter
from datetime import timedelta
import json
import re
import fitz
import os

#: Words counted as hard: the label the scheduler derived, or the learner's pin.
HARD_WORDS = Q(difficulty='hard') | Q(flagged=True)
#: Statuses for a word that has been started but is not yet on a long interval.
IN_PROGRESS = (scheduler.LEARNING, scheduler.RELEARNING)


# For this demo we'll use a dummy user if not logged in just so it works without auth setup immediately
def get_user(request):
    """Return the acting user.

    Deliberately does not sync UserWord rows — that ran on every request and
    cost two counts a page. Views that need the rows call ensure_user_words().
    """
    if request.user.is_authenticated:
        return request.user
    from django.contrib.auth.models import User
    user, created = User.objects.get_or_create(username='guest')
    return user

def get_or_create_profile(user):
    """Get or create user profile for tracking"""
    profile, created = UserProfile.objects.get_or_create(user=user)
    if created:
        profile.reset_daily_goal()
    return profile

def dashboard(request):
    user = get_user(request)
    profile = get_or_create_profile(user)
    
    # Reset daily goal if new day
    profile.reset_daily_goal()
    
    total_words = Word.objects.count()
    if total_words == 0:
        return render(request, 'flashcards/dashboard.html', {
            'error': 'No words loaded yet.',
            'profile': profile
        })

    ensure_user_words(user)
    user_words = UserWord.objects.filter(user=user)
    now = timezone.now()
    due = Q(next_review_date__lte=now) & ~Q(status=scheduler.NEW)

    # One pass over the table rather than a query per counter.
    totals = user_words.aggregate(
        mastered=Count('id', filter=Q(status=scheduler.MASTERED)),
        learning=Count('id', filter=Q(status__in=IN_PROGRESS)),
        new=Count('id', filter=Q(status=scheduler.NEW)),
        due=Count('id', filter=due),
        recent=Count('id', filter=Q(last_reviewed__gte=now - timedelta(days=7))),
        answers=Sum('times_reviewed'),
        correct=Sum('times_correct'),
    )

    # Accuracy over every answer given, rather than the mean of each word's
    # percentage — that weighted a word answered once like one answered fifty
    # times.
    answers = totals['answers'] or 0
    avg_accuracy = round((totals['correct'] or 0) / answers * 100, 1) if answers else 0

    by_level = {
        row['word__hsk_level']: row
        for row in user_words.values('word__hsk_level').annotate(
            total=Count('id'),
            mastered=Count('id', filter=Q(status=scheduler.MASTERED)),
            learning=Count('id', filter=Q(status__in=IN_PROGRESS)),
            review_due=Count('id', filter=due),
        )
    }
    levels = [
        {
            'level': level,
            'total': by_level[level]['total'],
            'mastered': by_level[level]['mastered'],
            'learning': by_level[level]['learning'],
            'review_due': by_level[level]['review_due'],
        }
        for level in range(1, 5)
        if level in by_level
    ]

    context = {
        'total_words': total_words,
        'levels': levels,
        'profile': profile,
        'stats': {
            'total_mastered': totals['mastered'],
            'total_learning': totals['learning'],
            'total_due': totals['due'],
            'total_new': totals['new'],
            'recent_reviews': totals['recent'],
            'avg_accuracy': avg_accuracy,
            'goal_progress': profile.get_goal_progress(),
        }
    }
    return render(request, 'flashcards/dashboard.html', context)

def init_user_words(request):
    """Utility to initialize UserWord models for all existing Words for the user."""
    ensure_user_words(get_user(request))
    return redirect('dashboard')

def study_levels(request):
    """Force users to pick an HSK level before studying."""
    user = get_user(request)
    ensure_user_words(user)
    study_queue.reset(request)  # A new level needs a new queue.

    now = timezone.now()
    by_level = {
        row['word__hsk_level']: row
        for row in UserWord.objects.filter(user=user).values('word__hsk_level').annotate(
            total=Count('id'),
            mastered=Count('id', filter=Q(status=scheduler.MASTERED)),
            learning=Count('id', filter=Q(status__in=IN_PROGRESS + (scheduler.REVIEW,))),
            new=Count('id', filter=Q(status=scheduler.NEW)),
            due=Count('id', filter=Q(next_review_date__lte=now) & ~Q(status=scheduler.NEW)),
        )
    }
    empty = {'total': 0, 'mastered': 0, 'learning': 0, 'new': 0, 'due': 0}
    level_stats = [dict(empty, **by_level.get(level, {}), level=level) for level in range(1, 5)]

    return render(request, "flashcards/study_levels.html", {"level_stats": level_stats})

def study_session(request, level=None):
    user = get_user(request)
    profile = get_or_create_profile(user)
    profile.reset_daily_goal()

    if level is None:
        return redirect("study_levels")

    card = study_queue.next_card(request, user, profile, level)

    context = {
        'card': card,
        'level': level,
        'profile': profile,
        'words_studied_today': profile.words_studied_today,
        'daily_goal': profile.daily_goal,
        'new_cards_remaining': profile.new_cards_remaining(),
        'stats': {
            'goal_progress': profile.get_goal_progress(),
        },
    }
    return render(request, 'flashcards/study.html', context)

@require_POST
def review_action(request, word_id, action):
    """Grade a card. POST only — these links used to be plain <a href>, so any
    prefetcher or crawler could silently grade a learner's whole deck."""
    user = get_user(request)
    profile = get_or_create_profile(user)
    profile.reset_daily_goal()

    user_word = UserWord.objects.filter(user=user, id=word_id).select_related('word').first()
    if user_word is None:
        return _back_to_study(request)

    if action == 'flag':
        user_word.flagged = not user_word.flagged
        user_word.save(update_fields=['flagged'])
        return _back_to_study(request)

    rating = scheduler.RATING_BY_NAME.get(action)
    if rating is None:
        return _back_to_study(request)

    was_new = user_word.status == scheduler.NEW
    duration_ms = _positive_int(request.POST.get('duration_ms'))

    user_word.grade(rating, duration_ms=duration_ms)

    profile.words_studied_today += 1
    if was_new:
        profile.new_cards_today += 1
    profile.save(update_fields=['words_studied_today', 'new_cards_today'])
    profile.update_streak()

    study_queue.advance(request, user_word)
    return _back_to_study(request)


def _back_to_study(request):
    """Redirect to the next card on the page the answer came from.

    The old flow bounced off HTTP_REFERER, which browsers are free to strip and
    which cannot be trusted as a redirect target.
    """
    target = request.POST.get('return_to')
    if target and url_has_allowed_host_and_scheme(target, allowed_hosts=None):
        return redirect(target)

    state = request.session.get(study_queue.SESSION_KEY) or {}
    level = state.get('level')
    if level:
        return redirect('study_session_level', level=level)
    return redirect('study_levels')


def _positive_int(value):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None

def word_list(request):
    user = get_user(request)
    level = request.GET.get("level")
    words = Word.objects.all().order_by('hsk_level', 'id')
    if level and level.isdigit():
        words = words.filter(hsk_level=int(level))
    
    # Get user's progress for each word
    user_word_map = {uw.word_id: uw for uw in UserWord.objects.filter(user=user)}
    
    word_data = []
    for word in words:
        user_word = user_word_map.get(word.id)
        word_data.append({
            'word': word,
            'user_word': user_word,
        })
    
    return render(
        request,
        'flashcards/word_list.html',
        {'word_data': word_data, 'selected_level': level},
    )

# Grammar views
def grammar_list(request, level=None):
    from .models import GrammarPoint
    if level:
        grammar_points = GrammarPoint.objects.filter(level=level).order_by('title')
    else:
        grammar_points = GrammarPoint.objects.all().order_by('level', 'title')
    return render(request, 'flashcards/grammar_list.html', {'grammar_points': grammar_points, 'level': level})

def grammar_detail(request, pk):
    from .models import GrammarPoint
    grammar = get_object_or_404(GrammarPoint, pk=pk)
    return render(request, 'flashcards/grammar_detail.html', {'grammar': grammar})

def _difficulty_session(request, filters, mode):
    """Show the most overdue card matching a difficulty filter."""
    user = get_user(request)
    profile = get_or_create_profile(user)
    card = (
        UserWord.objects.filter(user=user)
        .filter(filters)
        .select_related('word')
        .order_by('next_review_date')
        .first()
    )
    return render(request, 'flashcards/study.html', {
        'card': card,
        'level': None,
        'profile': profile,
        'difficulty_mode': mode,
    })

def study_hard_words(request):
    return _difficulty_session(request, HARD_WORDS, 'hard')

def study_easy_words(request):
    return _difficulty_session(request, Q(difficulty='easy'), 'easy')

def hard_words(request):
    user = get_user(request)
    hard_words_list = UserWord.objects.filter(user=user).filter(HARD_WORDS).select_related('word')
    return render(request, 'flashcards/hard_words.html', {'user_words': hard_words_list, 'difficulty_label': 'Hard'})

def easy_words(request):
    user = get_user(request)
    easy_words_list = UserWord.objects.filter(user=user, difficulty='easy').select_related('word')
    return render(request, 'flashcards/hard_words.html', {'user_words': easy_words_list, 'difficulty_label': 'Easy'})

def stats_view(request):
    """Detailed statistics view"""
    user = get_user(request)
    profile = get_or_create_profile(user)

    user_words = UserWord.objects.filter(user=user)
    today = scheduler.study_day()

    counts = user_words.aggregate(
        new_count=Count('id', filter=Q(status=scheduler.NEW)),
        learning_count=Count('id', filter=Q(status__in=IN_PROGRESS)),
        review_count=Count('id', filter=Q(status=scheduler.REVIEW)),
        mastered_count=Count('id', filter=Q(status=scheduler.MASTERED)),
        hard_count=Count('id', filter=HARD_WORDS),
        easy_count=Count('id', filter=Q(difficulty='easy')),
        normal_count=Count('id', filter=Q(difficulty='normal') & Q(flagged=False)),
        # Words recalled at least 80% of the time. This used to reference an
        # unimported `models.F`, so the page raised NameError on every visit.
        high_retention=Count(
            'id', filter=Q(times_reviewed__gt=0) & Q(times_correct__gte=F('times_reviewed') * 0.8)
        ),
        answers=Sum('times_reviewed'),
        correct=Sum('times_correct'),
        lapses=Sum('lapses'),
    )

    answers = counts['answers'] or 0
    retention = round((counts['correct'] or 0) / answers * 100, 1) if answers else 0

    # Reviews are logged individually now, so "today" means answers given
    # today rather than cards whose last answer happened to be today.
    reviews_today = Review.objects.filter(
        user_word__user=user, reviewed_at__gte=scheduler.day_starts_at(today)
    ).count()

    # A fortnight of upcoming load, so a backlog is visible before it lands.
    upcoming = (
        user_words.filter(
            next_review_date__gte=scheduler.day_starts_at(today),
            next_review_date__lt=scheduler.day_starts_at(today + timedelta(days=14)),
        )
        .exclude(status=scheduler.NEW)
        .values_list('next_review_date', flat=True)
    )
    per_day = Counter(scheduler.study_day(moment) for moment in upcoming)
    forecast = [
        {'day': today + timedelta(days=offset), 'count': per_day.get(today + timedelta(days=offset), 0)}
        for offset in range(14)
    ]

    context = {
        'profile': profile,
        'forecast': forecast,
        # Bars are drawn as a share of the busiest day; never divide by zero.
        'forecast_peak': max([day['count'] for day in forecast] + [1]),
        'stats': dict(
            counts,
            today_reviews=reviews_today,
            total_answers=answers,
            retention=retention,
        ),
    }
    return render(request, 'flashcards/stats.html', context)


# Book & Reading Views
def book_list(request):
    """List all HSK books"""
    from .models import Book
    books = Book.objects.all().order_by('hsk_level', 'title')
    return render(request, 'flashcards/book_list.html', {'books': books})


def chapter_list(request, book_id):
    """List chapters in a specific book"""
    from .models import Book, Chapter
    book = get_object_or_404(Book, pk=book_id)
    chapters = Chapter.objects.filter(book=book).order_by('chapter_number')
    return render(request, 'flashcards/chapter_list.html', {'book': book, 'chapters': chapters})


def read_segment(request, segment_id):
    """Read a text segment with TTS support"""
    from .models import TextSegment, Chapter, Book
    segment = get_object_or_404(TextSegment, pk=segment_id)
    chapter = segment.chapter
    book = chapter.book
    
    # Get navigation
    prev_segment = TextSegment.objects.filter(chapter=chapter, order__lt=segment.order).order_by('-order').first()
    next_segment = TextSegment.objects.filter(chapter=chapter, order__gt=segment.order).order_by('order').first()
    
    # If no prev/next in same chapter, check adjacent chapters
    if not prev_segment:
        prev_chapter = Chapter.objects.filter(book=book, chapter_number__lt=chapter.chapter_number).order_by('-chapter_number').first()
        if prev_chapter:
            prev_segment = TextSegment.objects.filter(chapter=prev_chapter).order_by('-order').first()
    
    if not next_segment:
        next_chapter = Chapter.objects.filter(book=book, chapter_number__gt=chapter.chapter_number).order_by('chapter_number').first()
        if next_chapter:
            next_segment = TextSegment.objects.filter(chapter=next_chapter).order_by('order').first()
    
    context = {
        'segment': segment,
        'chapter': chapter,
        'book': book,
        'prev_segment': prev_segment,
        'next_segment': next_segment,
    }
    return render(request, 'flashcards/read_segment.html', context)


def text_to_speech(request):
    """API endpoint for TTS - returns text info for browser TTS"""
    from django.http import JsonResponse
    from .models import TextSegment
    
    segment_id = request.GET.get('segment_id')
    text = request.GET.get('text', '')
    
    if segment_id:
        segment = get_object_or_404(TextSegment, pk=segment_id)
        return JsonResponse({
            'chinese': segment.chinese_text,
            'pinyin': segment.pinyin,
            'english': segment.english_translation,
            'lang': 'zh-CN'
        })
    elif text:
        return JsonResponse({
            'text': text,
            'lang': 'zh-CN'
        })
    
    return JsonResponse({'error': 'No text provided'}, status=400)


def story_store(request, level=None):
    """Story store page grouped by HSK levels."""
    stories = Story.objects.all().order_by("level", "title")
    if level:
        stories = stories.filter(level=level)

    grouped = []
    for lvl in range(1, 5):
        level_stories = stories.filter(level=lvl)
        if level is None or lvl == level:
            grouped.append(
                {
                    "level": lvl,
                    "stories": level_stories,
                }
            )

    return render(
        request,
        "flashcards/story_store.html",
        {"grouped_stories": grouped, "selected_level": level},
    )


def _story_paragraphs(story):
    """Line a story's Chinese, pinyin and English up paragraph by paragraph.

    Some stories store their pinyin as one unbroken blob, which cannot be put
    beside anything. Those are romanised from the Chinese instead, which is
    reliable precisely because it is derived from the column it sits next to.
    """
    chinese = [line.strip() for line in story.chinese_text.splitlines() if line.strip()]
    english = [line.strip() for line in (story.english_translation or "").splitlines() if line.strip()]
    pinyin = [line.strip() for line in (story.pinyin_text or "").splitlines() if line.strip()]

    if len(pinyin) != len(chinese):
        pinyin = _derive_pinyin(story, chinese)

    # Translations occasionally merge or split a paragraph; pad rather than
    # crash, so a story with an uneven English column still reads.
    return [
        {
            "chinese": paragraph,
            "pinyin": pinyin[index] if index < len(pinyin) else "",
            "english": english[index] if index < len(english) else "",
        }
        for index, paragraph in enumerate(chinese)
    ]


def _derive_pinyin(story, chinese):
    """Romanise each Chinese paragraph so the columns stay in step."""
    extra = {
        (item.get("chinese") or "").strip(): (item.get("pinyin") or "").strip()
        for item in story.vocabulary or []
    }
    try:
        lookup = pinyin_text.build_lookup(extra)
        romanised = pinyin_text.to_pinyin("\n".join(chinese), lookup)
    except pinyin_text.PinyinUnavailable:
        # Showing the other two columns beats failing the whole page.
        return []
    # Split without dropping blanks: positions have to match the input.
    return [line.strip() for line in romanised.split("\n")]


@ensure_csrf_cookie
def story_detail(request, pk):
    """Read a single story, side by side or stacked."""
    story = get_object_or_404(Story, pk=pk)
    show_pinyin = request.GET.get("show_pinyin", "1") == "1"
    layout = "stacked" if request.GET.get("layout") == "stacked" else "columns"

    # Build word lookup from global HSK words + story-specific vocabulary.
    word_lookup = {}
    for chinese, pinyin, english in Word.objects.exclude(chinese="").values_list("chinese", "pinyin", "english"):
        word_lookup[chinese] = {
            "pinyin": (pinyin or "").strip(),
            "english": (english or "").strip(),
        }
    for v in story.vocabulary or []:
        key = (v.get("chinese") or "").strip()
        if key:
            word_lookup[key] = {
                "pinyin": (v.get("pinyin") or "").strip(),
                "english": (v.get("english") or "").strip(),
            }

    max_word_len = max((len(k) for k in word_lookup.keys()), default=1)
    max_word_len = min(max_word_len, 8)

    def tokenize_chinese_run(run):
        tokens = []
        i = 0
        n = len(run)
        while i < n:
            matched = None
            upper = min(max_word_len, n - i)
            for size in range(upper, 0, -1):
                cand = run[i:i + size]
                if cand in word_lookup:
                    matched = cand
                    break
            if matched:
                tokens.append(matched)
                i += len(matched)
            else:
                tokens.append(run[i])
                i += 1
        return tokens

    def tokenize_line(line):
        pieces = []
        for token in re.findall(r"[\u4e00-\u9fff]+|[A-Za-z]+(?:'[A-Za-z]+)?|[0-9]+|[^\w\s]", line):
            if re.fullmatch(r"[\u4e00-\u9fff]+", token):
                pieces.extend(tokenize_chinese_run(token))
            else:
                pieces.append(token)
        return pieces

    rows = _story_paragraphs(story)
    for row in rows:
        row["tokens"] = tokenize_line(row["chinese"])

    return render(
        request,
        "flashcards/story_detail.html",
        {
            "story": story,
            "show_pinyin": show_pinyin,
            "layout": layout,
            "rows": rows,
            "vocab_lookup_json": json.dumps(word_lookup, ensure_ascii=False),
        },
    )


@csrf_exempt
def save_story_word(request, story_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    user = get_user(request)
    story = get_object_or_404(Story, pk=story_id)
    payload = json.loads(request.body or "{}")
    word = (payload.get("word") or "").strip()
    pinyin = (payload.get("pinyin") or "").strip()
    english = (payload.get("english") or "").strip()

    if not word:
        return JsonResponse({"error": "Word is required"}, status=400)

    _, created = SavedWord.objects.update_or_create(
        user=user,
        word=word,
        defaults={"story": story, "pinyin": pinyin, "english": english},
    )
    return JsonResponse({"saved": True, "created": created, "word": word})


def saved_words(request):
    user = get_user(request)
    words = SavedWord.objects.filter(user=user).select_related("story")
    return render(request, "flashcards/saved_words.html", {"saved_words": words})


def export_saved_words_pdf(request):
    user = get_user(request)
    words = SavedWord.objects.filter(user=user).order_by("-created_at")

    doc = fitz.open()

    # Prefer CJK-capable fonts on Windows so Chinese renders in exported PDF.
    candidate_fonts = [
        "C:/Windows/Fonts/msyh.ttc",      # Microsoft YaHei
        "C:/Windows/Fonts/msyhbd.ttc",    # Microsoft YaHei Bold
        "C:/Windows/Fonts/simhei.ttf",    # SimHei
        "C:/Windows/Fonts/simsun.ttc",    # SimSun
        "C:/Windows/Fonts/arialuni.ttf",  # Arial Unicode (if present)
    ]
    font_path = next((p for p in candidate_fonts if os.path.exists(p)), None)

    page = doc.new_page()
    page_width = page.rect.width
    margin = 40
    table_left = margin
    table_top = 92
    table_width = page_width - (margin * 2)
    row_height = 28
    y = 50

    # Title
    title = f"Saved Words - {user.username}"
    if font_path:
        page.insert_text((margin, y), title, fontsize=18, fontname="F0", fontfile=font_path)
    else:
        page.insert_text((margin, y), title, fontsize=18)

    y += 20
    subtitle = f"Total words: {words.count()}"
    if font_path:
        page.insert_text((margin, y), subtitle, fontsize=10, color=(0.35, 0.35, 0.35), fontname="F0", fontfile=font_path)
    else:
        page.insert_text((margin, y), subtitle, fontsize=10, color=(0.35, 0.35, 0.35))

    # Table columns: Chinese | Pinyin | English | Source | Saved On
    col_fracs = [0.16, 0.18, 0.38, 0.16, 0.12]
    col_x = [table_left]
    for frac in col_fracs:
        col_x.append(col_x[-1] + table_width * frac)

    headers = ["Chinese", "Pinyin", "English", "Source", "Saved On"]

    def draw_header(current_page, top_y):
        current_page.draw_rect(fitz.Rect(table_left, top_y, table_left + table_width, top_y + row_height), color=(0.45, 0.45, 0.45), fill=(0.93, 0.93, 0.96), width=1)
        for i, header in enumerate(headers):
            cell = fitz.Rect(col_x[i] + 4, top_y + 6, col_x[i + 1] - 4, top_y + row_height - 4)
            if font_path:
                current_page.insert_textbox(cell, header, fontsize=10, color=(0.15, 0.15, 0.2), fontname="F0", fontfile=font_path, align=fitz.TEXT_ALIGN_LEFT)
            else:
                current_page.insert_textbox(cell, header, fontsize=10, color=(0.15, 0.15, 0.2), align=fitz.TEXT_ALIGN_LEFT)

        # Vertical separators
        for x in col_x[1:-1]:
            current_page.draw_line((x, top_y), (x, top_y + row_height), color=(0.45, 0.45, 0.45), width=1)

    def draw_row(current_page, top_y, values):
        # Auto-expand row for long English text.
        eng_text = values[2] or "-"
        approx_lines = max(1, len(eng_text) // 56 + 1)
        dynamic_height = max(row_height, 18 + approx_lines * 12)

        current_page.draw_rect(
            fitz.Rect(table_left, top_y, table_left + table_width, top_y + dynamic_height),
            color=(0.78, 0.78, 0.82),
            width=0.8,
        )

        for i, value in enumerate(values):
            text = value if value else "-"
            cell = fitz.Rect(col_x[i] + 4, top_y + 5, col_x[i + 1] - 4, top_y + dynamic_height - 4)
            if font_path:
                current_page.insert_textbox(cell, text, fontsize=9.5, color=(0.1, 0.1, 0.1), fontname="F0", fontfile=font_path, align=fitz.TEXT_ALIGN_LEFT)
            else:
                current_page.insert_textbox(cell, text, fontsize=9.5, color=(0.1, 0.1, 0.1), align=fitz.TEXT_ALIGN_LEFT)

        for x in col_x[1:-1]:
            current_page.draw_line((x, top_y), (x, top_y + dynamic_height), color=(0.78, 0.78, 0.82), width=0.8)

        return dynamic_height

    current_y = table_top
    draw_header(page, current_y)
    current_y += row_height

    for item in words:
        values = [
            item.word,
            item.pinyin,
            item.english,
            item.story.title if item.story else "-",
            item.created_at.strftime("%Y-%m-%d"),
        ]
        # New page if needed.
        projected_height = max(row_height, 18 + (max(1, len((item.english or "")) // 56 + 1) * 12))
        if current_y + projected_height > page.rect.height - margin:
            page = doc.new_page()
            current_y = margin
            draw_header(page, current_y)
            current_y += row_height

        used_h = draw_row(page, current_y, values)
        current_y += used_h

    pdf_bytes = doc.tobytes()
    doc.close()

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="saved_words.pdf"'
    return response


def export_hard_words_pdf(request):
    user = get_user(request)
    hard_words = (
        UserWord.objects.filter(user=user)
        .filter(HARD_WORDS)
        .select_related("word")
        .order_by("word__hsk_level", "word__chinese")
    )

    doc = fitz.open()

    candidate_fonts = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/msyhbd.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/arialuni.ttf",
    ]
    font_path = next((p for p in candidate_fonts if os.path.exists(p)), None)

    page = doc.new_page()
    page_width = page.rect.width
    margin = 40
    table_left = margin
    table_top = 92
    table_width = page_width - (margin * 2)
    row_height = 28
    y = 50

    title = f"Hard Words - {user.username}"
    if font_path:
        page.insert_text((margin, y), title, fontsize=18, fontname="F0", fontfile=font_path)
    else:
        page.insert_text((margin, y), title, fontsize=18)

    y += 20
    subtitle = f"Total hard words: {hard_words.count()}"
    if font_path:
        page.insert_text((margin, y), subtitle, fontsize=10, color=(0.35, 0.35, 0.35), fontname="F0", fontfile=font_path)
    else:
        page.insert_text((margin, y), subtitle, fontsize=10, color=(0.35, 0.35, 0.35))

    # Table columns: Level | Chinese | Pinyin | English | Status
    col_fracs = [0.12, 0.16, 0.18, 0.42, 0.12]
    col_x = [table_left]
    for frac in col_fracs:
        col_x.append(col_x[-1] + table_width * frac)

    headers = ["Level", "Chinese", "Pinyin", "English", "Status"]

    def draw_header(current_page, top_y):
        current_page.draw_rect(
            fitz.Rect(table_left, top_y, table_left + table_width, top_y + row_height),
            color=(0.45, 0.45, 0.45),
            fill=(0.93, 0.93, 0.96),
            width=1,
        )
        for i, header in enumerate(headers):
            cell = fitz.Rect(col_x[i] + 4, top_y + 6, col_x[i + 1] - 4, top_y + row_height - 4)
            if font_path:
                current_page.insert_textbox(cell, header, fontsize=10, color=(0.15, 0.15, 0.2), fontname="F0", fontfile=font_path, align=fitz.TEXT_ALIGN_LEFT)
            else:
                current_page.insert_textbox(cell, header, fontsize=10, color=(0.15, 0.15, 0.2), align=fitz.TEXT_ALIGN_LEFT)

        for x in col_x[1:-1]:
            current_page.draw_line((x, top_y), (x, top_y + row_height), color=(0.45, 0.45, 0.45), width=1)

    def draw_row(current_page, top_y, values):
        eng_text = values[3] or "-"
        approx_lines = max(1, len(eng_text) // 56 + 1)
        dynamic_height = max(row_height, 18 + approx_lines * 12)

        current_page.draw_rect(
            fitz.Rect(table_left, top_y, table_left + table_width, top_y + dynamic_height),
            color=(0.78, 0.78, 0.82),
            width=0.8,
        )

        for i, value in enumerate(values):
            text = value if value else "-"
            cell = fitz.Rect(col_x[i] + 4, top_y + 5, col_x[i + 1] - 4, top_y + dynamic_height - 4)
            if font_path:
                current_page.insert_textbox(cell, text, fontsize=9.5, color=(0.1, 0.1, 0.1), fontname="F0", fontfile=font_path, align=fitz.TEXT_ALIGN_LEFT)
            else:
                current_page.insert_textbox(cell, text, fontsize=9.5, color=(0.1, 0.1, 0.1), align=fitz.TEXT_ALIGN_LEFT)

        for x in col_x[1:-1]:
            current_page.draw_line((x, top_y), (x, top_y + dynamic_height), color=(0.78, 0.78, 0.82), width=0.8)

        return dynamic_height

    current_y = table_top
    draw_header(page, current_y)
    current_y += row_height

    for item in hard_words:
        values = [
            f"HSK {item.word.hsk_level}",
            item.word.chinese,
            item.word.pinyin,
            item.word.english,
            item.status,
        ]

        projected_height = max(row_height, 18 + (max(1, len((item.word.english or "")) // 56 + 1) * 12))
        if current_y + projected_height > page.rect.height - margin:
            page = doc.new_page()
            current_y = margin
            draw_header(page, current_y)
            current_y += row_height

        used_h = draw_row(page, current_y, values)
        current_y += used_h

    pdf_bytes = doc.tobytes()
    doc.close()

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="hard_words.pdf"'
    return response


def dialogue_list(request, category=None):
    dialogues = Dialogue.objects.all().order_by("category", "level", "title")
    if category:
        dialogues = dialogues.filter(category=category)

    category_labels = dict(Dialogue.CATEGORY_CHOICES)
    grouped = []
    for key, label in Dialogue.CATEGORY_CHOICES:
        if category and key != category:
            continue
        grouped.append(
            {
                "key": key,
                "label": label,
                "items": dialogues.filter(category=key),
            }
        )

    return render(
        request,
        "flashcards/dialogue_list.html",
        {
            "grouped_dialogues": grouped,
            "selected_category": category,
            "category_labels": category_labels,
        },
    )


def dialogue_detail(request, pk):
    dialogue = get_object_or_404(Dialogue, pk=pk)
    show_pinyin = request.GET.get("show_pinyin", "1") == "1"
    return render(
        request,
        "flashcards/dialogue_detail.html",
        {"dialogue": dialogue, "show_pinyin": show_pinyin},
    )


# -----------------------
# JSON API (no DRF)
# -----------------------

def api_words(request):
    """GET /api/words/?level=1..4"""
    level = request.GET.get("level")
    qs = Word.objects.all().order_by("hsk_level", "id")
    if level and level.isdigit():
        qs = qs.filter(hsk_level=int(level))

    data = [
        {
            "id": w.id,
            "hsk_level": w.hsk_level,
            "chinese": w.chinese,
            "pinyin": w.pinyin,
            "english": w.english,
            "example_sentences": w.example_sentences,
        }
        for w in qs[:5000]
    ]
    return JsonResponse({"count": len(data), "results": data})


def api_study_next(request, level: int):
    """GET /api/study/<level>/next/ -> next card for that level."""
    user = get_user(request)
    profile = get_or_create_profile(user)
    profile.reset_daily_goal()

    # Same queue the HTML session serves, so the two stay in step.
    due_word = study_queue.next_card(request, user, profile, level)
    if not due_word:
        return JsonResponse({"card": None})

    w = due_word.word
    example = None
    if isinstance(w.example_sentences, list) and w.example_sentences:
        example = w.example_sentences[0]

    return JsonResponse(
        {
            "card": {
                "id": due_word.id,
                "status": due_word.status,
                "difficulty": due_word.difficulty,
                "flagged": due_word.flagged,
                "interval": due_word.interval,
                "ease_factor": round(due_word.ease_factor, 2),
                "lapses": due_word.lapses,
                "next_review_date": due_word.next_review_date.isoformat() if due_word.next_review_date else None,
                "previews": {
                    scheduler.RATING_NAMES[rating]: label
                    for rating, label in due_word.preview_intervals().items()
                },
                "word": {
                    "id": w.id,
                    "hsk_level": w.hsk_level,
                    "chinese": w.chinese,
                    "pinyin": w.pinyin,
                    "english": w.english,
                    "simple_example": example,
                },
            },
            "profile": {
                "daily_goal": profile.daily_goal,
                "words_studied_today": profile.words_studied_today,
                "goal_progress": profile.get_goal_progress(),
                "new_cards_remaining": profile.new_cards_remaining(),
            },
        }
    )


def api_stories(request):
    """GET /api/stories/?level=1..4"""
    level = request.GET.get("level")
    qs = Story.objects.all().order_by("level", "title")
    if level and level.isdigit():
        qs = qs.filter(level=int(level))

    data = [
        {
            "id": s.id,
            "level": s.level,
            "title": s.title,
            "vocabulary": s.vocabulary,
            "grammar_points": s.grammar_points,
        }
        for s in qs
    ]
    return JsonResponse({"count": len(data), "results": data})


def api_story_detail(request, pk: int):
    """GET /api/stories/<id>/"""
    s = get_object_or_404(Story, pk=pk)
    return JsonResponse(
        {
            "id": s.id,
            "level": s.level,
            "title": s.title,
            "chinese_text": s.chinese_text,
            "pinyin_text": s.pinyin_text,
            "english_translation": s.english_translation,
            "vocabulary": s.vocabulary,
            "grammar_points": s.grammar_points,
        }
    )


def api_dialogues(request):
    """GET /api/dialogues/?category=gym|class|home|friends|import_export"""
    category = request.GET.get("category")
    qs = Dialogue.objects.all().order_by("category", "level", "title")
    if category:
        qs = qs.filter(category=category)

    data = [
        {"id": d.id, "title": d.title, "category": d.category, "level": d.level}
        for d in qs
    ]
    return JsonResponse({"count": len(data), "results": data})


def api_dialogue_detail(request, pk: int):
    """GET /api/dialogues/<id>/"""
    d = get_object_or_404(Dialogue, pk=pk)
    return JsonResponse(
        {"id": d.id, "title": d.title, "category": d.category, "level": d.level, "lines": d.lines}
    )


@csrf_exempt
def api_saved_words(request):
    """
    GET  /api/saved-words/ -> list
    POST /api/saved-words/ -> save {word,pinyin,english,story_id?}
    """
    user = get_user(request)

    if request.method == "GET":
        items = SavedWord.objects.filter(user=user).select_related("story")
        data = [
            {
                "id": it.id,
                "word": it.word,
                "pinyin": it.pinyin,
                "english": it.english,
                "story": {"id": it.story.id, "title": it.story.title} if it.story else None,
                "created_at": it.created_at.isoformat() if it.created_at else None,
            }
            for it in items
        ]
        return JsonResponse({"count": len(data), "results": data})

    if request.method == "POST":
        payload = json.loads(request.body or "{}")
        word = (payload.get("word") or "").strip()
        if not word:
            return JsonResponse({"error": "word is required"}, status=400)

        story_id = payload.get("story_id")
        story = Story.objects.filter(id=story_id).first() if story_id else None
        pinyin = (payload.get("pinyin") or "").strip()
        english = (payload.get("english") or "").strip()

        _, created = SavedWord.objects.update_or_create(
            user=user,
            word=word,
            defaults={"story": story, "pinyin": pinyin, "english": english},
        )
        return JsonResponse({"saved": True, "created": created, "word": word})

    return JsonResponse({"error": "Method not allowed"}, status=405)
