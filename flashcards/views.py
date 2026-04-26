from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from .models import Word, UserWord, UserProfile, Story, SavedWord, Dialogue
from datetime import date
import json
import re
import fitz
import os

def ensure_user_words(user):
    """Create missing UserWord rows for all available words."""
    total_words = Word.objects.count()
    current_user_words = UserWord.objects.filter(user=user).count()
    if current_user_words >= total_words:
        return

    existing_word_ids = set(UserWord.objects.filter(user=user).values_list('word_id', flat=True))
    to_create = [
        UserWord(user=user, word=word)
        for word in Word.objects.exclude(id__in=existing_word_ids)
    ]
    if to_create:
        UserWord.objects.bulk_create(to_create)

# For this demo we'll use a dummy user if not logged in just so it works without auth setup immediately
def get_user(request):
    if request.user.is_authenticated:
        ensure_user_words(request.user)
        return request.user
    from django.contrib.auth.models import User
    user, created = User.objects.get_or_create(username='guest')
    ensure_user_words(user)
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
    
    user_words = UserWord.objects.filter(user=user)
    
    total_words = Word.objects.count()
    if total_words == 0:
        return render(request, 'flashcards/dashboard.html', {
            'error': 'No words loaded yet.',
            'profile': profile
        })

    # Calculate overall statistics
    total_mastered = user_words.filter(status='MASTERED').count()
    total_learning = user_words.filter(status='LEARNING').count()
    total_due = user_words.filter(next_review_date__lte=timezone.now(), status__in=['LEARNING', 'REVIEW']).count()
    total_new = user_words.filter(status='NEW').count()
    
    # Get recent activity (last 7 days)
    from datetime import timedelta
    week_ago = timezone.now() - timedelta(days=7)
    recent_reviews = user_words.filter(
        last_reviewed__gte=week_ago,
        last_reviewed__isnull=False
    ).count()
    
    # Calculate accuracy
    total_reviewed = user_words.filter(times_reviewed__gt=0).count()
    if total_reviewed > 0:
        avg_accuracy = sum(uw.calculate_retention_rate() for uw in user_words.filter(times_reviewed__gt=0)) / total_reviewed
    else:
        avg_accuracy = 0
    
    levels = []
    for level in range(1, 5):
        level_words = user_words.filter(word__hsk_level=level)
        if level_words.exists():
            levels.append({
                'level': level,
                'total': level_words.count(),
                'mastered': level_words.filter(status='MASTERED').count(),
                'learning': level_words.filter(status='LEARNING').count(),
                'review_due': level_words.filter(next_review_date__lte=timezone.now()).count()
            })
    
    context = {
        'total_words': total_words,
        'levels': levels,
        'profile': profile,
        'stats': {
            'total_mastered': total_mastered,
            'total_learning': total_learning,
            'total_due': total_due,
            'total_new': total_new,
            'recent_reviews': recent_reviews,
            'avg_accuracy': round(avg_accuracy, 1),
            'goal_progress': profile.get_goal_progress(),
        }
    }
    return render(request, 'flashcards/dashboard.html', context)

def init_user_words(request):
    """Utility to initialize UserWord models for all existing Words for the user."""
    user = get_user(request)
    words = Word.objects.all()
    existing_user_words = UserWord.objects.filter(user=user).values_list('word_id', flat=True)
    
    new_user_words = []
    for word in words:
        if word.id not in existing_user_words:
            new_user_words.append(UserWord(user=user, word=word))
            
    if new_user_words:
        UserWord.objects.bulk_create(new_user_words)
        
    return redirect('dashboard')

def study_levels(request):
    """Force users to pick an HSK level before studying."""
    user = get_user(request)

    level_stats = []
    for lvl in range(1, 5):
        total = Word.objects.filter(hsk_level=lvl).count()
        mastered = UserWord.objects.filter(user=user, word__hsk_level=lvl, status="MASTERED").count()
        learning = UserWord.objects.filter(user=user, word__hsk_level=lvl, status__in=["LEARNING", "REVIEW"]).count()
        new = UserWord.objects.filter(user=user, word__hsk_level=lvl, status="NEW").count()
        level_stats.append(
            {
                "level": lvl,
                "total": total,
                "mastered": mastered,
                "learning": learning,
                "new": new,
            }
        )

    return render(request, "flashcards/study_levels.html", {"level_stats": level_stats})

def study_session(request, level=None):
    user = get_user(request)
    profile = get_or_create_profile(user)

    if level is None:
        return redirect("study_levels")
    
    base_query = UserWord.objects.filter(user=user)
    if level:
        base_query = base_query.filter(word__hsk_level=level)
        
    # Get a word that needs review (prioritize forgotten/hard words)
    due_word = base_query.filter(
        next_review_date__lte=timezone.now(),
        status__in=['LEARNING', 'REVIEW']
    ).exclude(status='MASTERED').order_by('next_review_date', '-times_incorrect').first()
    
    # If no review words, get a new word
    if not due_word:
        due_word = base_query.filter(status='NEW').first()
    
    # Update session tracking
    if due_word:
        due_word.studied_in_session = False
        due_word.session_correct = None
        due_word.save()
    
    context = {
        'card': due_word,
        'level': level,
        'profile': profile,
        'words_studied_today': profile.words_studied_today,
        'daily_goal': profile.daily_goal,
        'stats': {
            'goal_progress': profile.get_goal_progress(),
        },
    }
    return render(request, 'flashcards/study.html', context)

def review_action(request, word_id, action):
    user = get_user(request)
    profile = get_or_create_profile(user)
    
    try:
        user_word = UserWord.objects.get(user=user, id=word_id)
        
        # Track if this is first time learning
        if user_word.first_learned is None and action == 'remembered':
            user_word.first_learned = timezone.now()
        
        if action == 'remembered':
            user_word.mark_remembered()
            profile.words_studied_today += 1
            profile.update_streak()
        elif action == 'forgotten':
            user_word.mark_forgotten()
            profile.words_studied_today += 1
            profile.update_streak()
        elif action == 'hard':
            user_word.mark_hard()
            profile.words_studied_today += 1
            profile.update_streak()
            
        profile.save()
        
    except UserWord.DoesNotExist:
        pass
        
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('study_session')

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

def study_hard_words(request):
    user = get_user(request)
    hard_word = UserWord.objects.filter(user=user, difficulty='hard').order_by('next_review_date').first()
    return render(request, 'flashcards/study.html', {'card': hard_word, 'level': None, 'difficulty_mode': 'hard'})

def study_easy_words(request):
    user = get_user(request)
    easy_word = UserWord.objects.filter(user=user, difficulty='easy').order_by('next_review_date').first()
    return render(request, 'flashcards/study.html', {'card': easy_word, 'level': None, 'difficulty_mode': 'easy'})

def hard_words(request):
    user = get_user(request)
    hard_words_list = UserWord.objects.filter(user=user, difficulty='hard').select_related('word')
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
    
    # Get words grouped by status
    new_count = user_words.filter(status='NEW').count()
    learning_count = user_words.filter(status='LEARNING').count()
    review_count = user_words.filter(status='REVIEW').count()
    mastered_count = user_words.filter(status='MASTERED').count()
    
    # Get difficulty distribution
    hard_count = user_words.filter(difficulty='hard').count()
    normal_count = user_words.filter(difficulty='normal').count()
    easy_count = user_words.filter(difficulty='easy').count()
    
    # Get retention rate distribution
    high_retention = user_words.filter(times_reviewed__gt=0).filter(
        times_correct__gte=models.F('times_reviewed') * 0.8
    ).count()
    
    # Get today's activity
    today = date.today()
    today_reviews = user_words.filter(
        last_reviewed__date=today,
        last_reviewed__isnull=False
    ).count()
    
    context = {
        'profile': profile,
        'stats': {
            'new_count': new_count,
            'learning_count': learning_count,
            'review_count': review_count,
            'mastered_count': mastered_count,
            'hard_count': hard_count,
            'normal_count': normal_count,
            'easy_count': easy_count,
            'high_retention': high_retention,
            'today_reviews': today_reviews,
        }
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


@ensure_csrf_cookie
def story_detail(request, pk):
    """Read a single story with optional pinyin visibility."""
    story = get_object_or_404(Story, pk=pk)
    show_pinyin = request.GET.get("show_pinyin", "1") == "1"

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

    chinese_lines = [
        tokenize_line(line) for line in story.chinese_text.splitlines() if line.strip()
    ]

    return render(
        request,
        "flashcards/story_detail.html",
        {
            "story": story,
            "show_pinyin": show_pinyin,
            "chinese_lines": chinese_lines,
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
    """GET /api/study/<level>/next/ -> next due card for that level."""
    user = get_user(request)
    profile = get_or_create_profile(user)

    base_query = UserWord.objects.filter(user=user, word__hsk_level=level)
    due_word = base_query.filter(
        next_review_date__lte=timezone.now(),
        status__in=["LEARNING", "REVIEW"],
    ).exclude(status="MASTERED").order_by("next_review_date", "-times_incorrect").first()

    if not due_word:
        due_word = base_query.filter(status="NEW").first()

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
                "next_review_date": due_word.next_review_date.isoformat() if due_word.next_review_date else None,
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
