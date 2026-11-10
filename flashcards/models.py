from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from . import scheduler

# Grammar point model for HSK grammar section
class GrammarPoint(models.Model):
    HSK_LEVELS = [
        (1, "HSK 1"),
        (2, "HSK 2"),
        (3, "HSK 3"),
        (4, "HSK 4"),
    ]
    level = models.IntegerField(choices=HSK_LEVELS)
    title = models.CharField(max_length=200)
    explanation = models.TextField()
    detailed_explanation = models.TextField(blank=True)
    example_cn = models.TextField(blank=True)
    example_pinyin = models.TextField(blank=True)
    example_en = models.TextField(blank=True)
    examples = models.JSONField(
        blank=True,
        default=list,
        help_text="List of examples, each with cn/pinyin/en keys",
    )
    
    def __str__(self):
        return f"HSK {self.level}: {self.title}"

class Word(models.Model):
    hsk_level = models.IntegerField()
    chinese = models.CharField(max_length=100)
    pinyin = models.CharField(max_length=100)
    english = models.TextField()
    
    # Enhanced learning fields
    character_breakdown = models.TextField(blank=True, help_text="Breakdown of individual characters and their meanings")
    usage_notes = models.TextField(blank=True, help_text="Detailed usage notes and context")
    grammar_points = models.TextField(blank=True, help_text="Grammar points related to this word")
    example_sentences = models.JSONField(blank=True, default=list, help_text="List of example sentences with pinyin and translation")
    synonyms = models.TextField(blank=True, help_text="Comma-separated list of synonyms")
    antonyms = models.TextField(blank=True, help_text="Comma-separated list of antonyms")
    radical = models.CharField(max_length=50, blank=True, help_text="Primary radical of the character(s)")
    stroke_count = models.IntegerField(null=True, blank=True, help_text="Total stroke count")
    frequency_rank = models.IntegerField(null=True, blank=True, help_text="Frequency rank in common usage")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["hsk_level", "chinese", "pinyin"],
                name="unique_word_per_level_chinese_pinyin",
            )
        ]
    
    def __str__(self):
        return f"{self.chinese} (HSK {self.hsk_level})"

class UserWord(models.Model):
    STATUS_CHOICES = [
        (scheduler.NEW, "New"),
        (scheduler.LEARNING, "Learning"),
        (scheduler.RELEARNING, "Relearning"),
        (scheduler.REVIEW, "Review"),
        (scheduler.MASTERED, "Mastered"),
    ]
    DIFFICULTY_CHOICES = [
        ("normal", "Normal"),
        ("hard", "Hard"),
        ("easy", "Easy"),
    ]

    # A word is labelled hard once it has lapsed this often, or once it is
    # being recalled less often than this share of the time.
    HARD_LAPSES = 3
    HARD_RETENTION = 60
    EASY_RETENTION = 90

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=scheduler.NEW)

    # Derived from the card's whole history by refresh_difficulty(); never set
    # directly by a single answer.
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default="normal")
    # The learner's own pin, kept separate from the derived label above so that
    # grading a word can never silently un-pin it.
    flagged = models.BooleanField(default=False, help_text="Pinned to the hard list by the learner")

    # Scheduling state (see flashcards/scheduler.py)
    next_review_date = models.DateTimeField(default=timezone.now)
    ease_factor = models.FloatField(default=scheduler.INITIAL_EASE)
    interval = models.IntegerField(default=0, help_text="Current interval in days")
    reps = models.IntegerField(default=0, help_text="Successful repetitions")
    lapses = models.IntegerField(default=0, help_text="Times this card has been forgotten after graduating")
    learning_step = models.IntegerField(default=0, help_text="Index into the (re)learning steps")

    # Statistics
    consecutive_correct = models.IntegerField(default=0)
    times_reviewed = models.IntegerField(default=0)
    times_correct = models.IntegerField(default=0)
    times_incorrect = models.IntegerField(default=0)
    last_reviewed = models.DateTimeField(null=True, blank=True)
    first_learned = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "word")
        indexes = [
            models.Index(fields=["user", "next_review_date"]),
            models.Index(fields=["user", "status"]),
        ]

    def calculate_retention_rate(self):
        """Return the share of reviews recalled, as a percentage."""
        if self.times_reviewed == 0:
            return 0
        return round((self.times_correct / self.times_reviewed) * 100, 1)

    def get_accuracy_emoji(self):
        """Return an emoji based on accuracy"""
        rate = self.calculate_retention_rate()
        if rate >= 90:
            return "🌟"
        elif rate >= 70:
            return "✅"
        elif rate >= 50:
            return "⚠️"
        else:
            return "📚"

    # --- Scheduling ---------------------------------------------------------

    def as_scheduler_card(self):
        """Return this row's scheduling state as a plain scheduler.Card."""
        return scheduler.Card(
            status=self.status,
            step=self.learning_step,
            ease=self.ease_factor,
            interval=self.interval,
            reps=self.reps,
            lapses=self.lapses,
            due=self.next_review_date,
        )

    def apply_scheduler_card(self, card):
        """Copy scheduling state back off a scheduler.Card."""
        self.status = card.status
        self.learning_step = card.step
        self.ease_factor = card.ease
        self.interval = card.interval
        self.reps = card.reps
        self.lapses = card.lapses
        self.next_review_date = card.due

    def refresh_difficulty(self):
        """Recompute the difficulty label from the card's whole history.

        Deriving it matters: setting the label from the last answer alone let a
        single lucky recall relabel a word that had been failed ten times.
        """
        retention = self.calculate_retention_rate()
        if self.lapses >= self.HARD_LAPSES or (
            self.times_reviewed >= 3 and retention < self.HARD_RETENTION
        ):
            self.difficulty = "hard"
        elif self.reps >= 3 and self.lapses == 0 and retention >= self.EASY_RETENTION:
            self.difficulty = "easy"
        else:
            self.difficulty = "normal"

    def grade(self, rating, now=None, duration_ms=None):
        """Record an answer, reschedule the card, and log the review.

        Returns the resulting scheduler.Card.
        """
        now = now or timezone.now()
        before = self.as_scheduler_card()
        after = scheduler.review(before, rating, now=now)

        self.times_reviewed += 1
        if rating == scheduler.AGAIN:
            self.times_incorrect += 1
            self.consecutive_correct = 0
        else:
            # Hard is a passing grade: the word was recalled, just not easily.
            self.times_correct += 1
            self.consecutive_correct += 1
        self.last_reviewed = now
        if self.first_learned is None:
            self.first_learned = now

        elapsed_days = (
            (scheduler.study_day(now) - scheduler.study_day(before.due)).days if before.due else 0
        )

        self.apply_scheduler_card(after)
        self.refresh_difficulty()
        self.save()

        Review.objects.create(
            user_word=self,
            reviewed_at=now,
            rating=rating,
            state_before=before.status,
            interval_before=before.interval,
            ease_before=before.ease,
            elapsed_days=elapsed_days,
            state_after=after.status,
            interval_after=after.interval,
            ease_after=after.ease,
            duration_ms=duration_ms,
        )
        return after

    def preview_intervals(self):
        """Return {rating: label} describing what each button would schedule."""
        return scheduler.next_intervals(self.as_scheduler_card())

    #: Grade buttons, in the order they are shown, with the CSS accent to use.
    GRADE_BUTTONS = (
        (scheduler.AGAIN, "Again", "#ef4444"),
        (scheduler.HARD, "Hard", "#f59e0b"),
        (scheduler.GOOD, "Good", "#10b981"),
        (scheduler.EASY, "Easy", "#38bdf8"),
    )

    def grade_options(self):
        """Return the study screen's grade buttons with their scheduled delays.

        Showing what each button costs is the point of a four-grade scale: it
        is what lets someone pick Hard over Again without guessing.
        """
        previews = self.preview_intervals()
        return [
            {
                "action": scheduler.RATING_NAMES[rating],
                "label": label,
                "colour": colour,
                "preview": previews[rating],
            }
            for rating, label, colour in self.GRADE_BUTTONS
        ]

    def is_due(self, now=None):
        return self.next_review_date <= (now or timezone.now())

    def __str__(self):
        return f"{self.user.username} - {self.word.chinese} - {self.status}"


class Review(models.Model):
    """One graded answer.

    Aggregate counters on UserWord cannot say when a card was answered or what
    state it was in at the time, so they cannot support undo, a real retention
    curve, or the parameter fitting that FSRS needs. This table can.
    """

    RATING_CHOICES = [
        (scheduler.AGAIN, "Again"),
        (scheduler.HARD, "Hard"),
        (scheduler.GOOD, "Good"),
        (scheduler.EASY, "Easy"),
    ]

    user_word = models.ForeignKey(UserWord, on_delete=models.CASCADE, related_name="reviews")
    reviewed_at = models.DateTimeField(default=timezone.now)
    rating = models.IntegerField(choices=RATING_CHOICES)

    # State going in, which is what any later analysis has to condition on.
    state_before = models.CharField(max_length=20)
    interval_before = models.IntegerField()
    ease_before = models.FloatField()
    elapsed_days = models.IntegerField(
        help_text="Days between the scheduled due date and the answer; negative if answered early"
    )

    # State coming out.
    state_after = models.CharField(max_length=20)
    interval_after = models.IntegerField()
    ease_after = models.FloatField()

    duration_ms = models.IntegerField(null=True, blank=True, help_text="Time spent on the card")

    class Meta:
        ordering = ["-reviewed_at"]
        indexes = [
            models.Index(fields=["user_word", "-reviewed_at"]),
            models.Index(fields=["reviewed_at"]),
        ]

    def __str__(self):
        return f"{self.user_word.word.chinese} {self.get_rating_display()} @ {self.reviewed_at:%Y-%m-%d}"


class UserProfile(models.Model):
    """Extended user profile for learning analytics"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Streak tracking
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_study_date = models.DateField(null=True, blank=True)
    
    # Daily goals
    daily_goal = models.IntegerField(default=20)  # Words per day
    words_studied_today = models.IntegerField(default=0)
    last_reset_date = models.DateField(null=True, blank=True)

    # Pacing. Without a cap on unseen words a learner can burn through hundreds
    # in one sitting and then face an unmanageable backlog a week later.
    new_cards_per_day = models.IntegerField(default=10)
    new_cards_today = models.IntegerField(default=0)
    
    # Overall statistics
    total_words_learned = models.IntegerField(default=0)
    total_study_time_minutes = models.IntegerField(default=0)
    join_date = models.DateTimeField(auto_now_add=True)
    
    # Preferences
    preferred_audio = models.BooleanField(default=True)
    show_pinyin_on_front = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def update_streak(self):
        """Extend the streak if this is the first study of a new day."""
        today = scheduler.study_day()

        if self.last_study_date == today:
            return  # Already counted today.
        if self.last_study_date == today - timedelta(days=1):
            self.current_streak += 1
        else:
            self.current_streak = 1

        self.longest_streak = max(self.longest_streak, self.current_streak)
        self.last_study_date = today
        self.save(update_fields=["current_streak", "longest_streak", "last_study_date"])

    def reset_daily_goal(self):
        """Clear the per-day counters when the study day rolls over."""
        today = scheduler.study_day()
        if self.last_reset_date != today:
            self.words_studied_today = 0
            self.new_cards_today = 0
            self.last_reset_date = today
            self.save(update_fields=["words_studied_today", "new_cards_today", "last_reset_date"])

    def get_goal_progress(self):
        """Get daily goal progress as percentage"""
        if self.daily_goal == 0:
            return 0
        return min(100, round((self.words_studied_today / self.daily_goal) * 100))

    def new_cards_remaining(self):
        """How many unseen words may still be introduced today."""
        return max(0, self.new_cards_per_day - self.new_cards_today)
    
    @classmethod
    def get_or_create_profile(cls, user):
        """Get or create a user profile"""
        profile, created = cls.objects.get_or_create(user=user)
        if created:
            profile.reset_daily_goal()
        return profile


class Book(models.Model):
    """HSK Standard Course Books (1-6)"""
    LEVEL_CHOICES = [(i, f"HSK {i}") for i in range(1, 7)]
    
    title = models.CharField(max_length=100)
    hsk_level = models.IntegerField(choices=LEVEL_CHOICES)
    description = models.TextField(blank=True, help_text="Description of the book content")
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['hsk_level', 'title']
        verbose_name_plural = "Books"
    
    def __str__(self):
        return f"{self.title} (HSK {self.hsk_level})"
    
    def get_chapter_count(self):
        return self.chapters.count()
    
    def get_segment_count(self):
        total = 0
        for chapter in self.chapters.all():
            total += chapter.segments.count()
        return total


class Chapter(models.Model):
    """Chapters within a Book"""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='chapters')
    chapter_number = models.IntegerField(help_text="Chapter number (e.g., 1, 2, 3)")
    title = models.CharField(max_length=200)
    summary = models.TextField(blank=True, help_text="Brief summary of what this chapter covers")
    
    class Meta:
        ordering = ['book', 'chapter_number']
        unique_together = ['book', 'chapter_number']
        verbose_name_plural = "Chapters"
    
    def __str__(self):
        return f"Chapter {self.chapter_number}: {self.title}"
    
    def get_segment_count(self):
        return self.segments.count()


class TextSegment(models.Model):
    """Individual sentences or paragraphs within a Chapter with TTS support"""
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='segments')
    order = models.IntegerField(help_text="Order of appearance in the chapter")
    
    chinese_text = models.TextField(help_text="Chinese characters (Simplified)")
    pinyin = models.TextField(help_text="Pinyin with tone marks")
    english_translation = models.TextField(help_text="English translation")
    
    # Optional audio file if pre-recorded (otherwise uses browser TTS)
    audio_file = models.FileField(upload_to='chapter_audio/', blank=True, null=True)
    
    # Word associations (optional - links to vocabulary in this segment)
    key_words = models.ManyToManyField('Word', blank=True, help_text="Key vocabulary words in this segment")
    
    class Meta:
        ordering = ['chapter', 'order']
        verbose_name_plural = "Text Segments"
    
    def __str__(self):
        preview = self.chinese_text[:30] + "..." if len(self.chinese_text) > 30 else self.chinese_text
        return f"Segment {self.order}: {preview}"


class Story(models.Model):
    """Short stories categorized by HSK level."""
    HSK_LEVELS = [
        (1, "HSK 1"),
        (2, "HSK 2"),
        (3, "HSK 3"),
        (4, "HSK 4"),
    ]

    level = models.IntegerField(choices=HSK_LEVELS)
    title = models.CharField(max_length=200)
    chinese_text = models.TextField()
    pinyin_text = models.TextField(blank=True)
    english_translation = models.TextField(blank=True)
    vocabulary = models.JSONField(
        blank=True,
        default=list,
        help_text="List of vocabulary items with chinese, pinyin, and english.",
    )
    grammar_points = models.JSONField(
        blank=True,
        default=list,
        help_text="List of grammar point labels used in this story.",
    )

    class Meta:
        ordering = ["level", "title"]

    def __str__(self):
        return f"HSK {self.level}: {self.title}"


class SavedWord(models.Model):
    """Words saved by users from stories or other pages."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_words")
    story = models.ForeignKey(Story, on_delete=models.SET_NULL, null=True, blank=True, related_name="saved_words")
    word = models.CharField(max_length=100)
    pinyin = models.CharField(max_length=120, blank=True)
    english = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "word"], name="unique_saved_word_per_user")
        ]

    def __str__(self):
        return f"{self.user.username}: {self.word}"


class Dialogue(models.Model):
    """Practical dialogues categorized by scenario and HSK level."""
    CATEGORY_CHOICES = [
        ("gym", "Gym"),
        ("class", "Class"),
        ("home", "Home"),
        ("friends", "With Friends"),
        ("import_export", "Import / Export Business"),
    ]
    HSK_LEVELS = [
        (1, "HSK 1"),
        (2, "HSK 2"),
        (3, "HSK 3"),
        (4, "HSK 4"),
    ]

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    level = models.IntegerField(choices=HSK_LEVELS)
    lines = models.JSONField(
        default=list,
        help_text="List of dialogue lines, each with speaker/cn/pinyin/en keys.",
    )

    class Meta:
        ordering = ["category", "level", "title"]

    def __str__(self):
        return f"{self.get_category_display()} - {self.title}"
