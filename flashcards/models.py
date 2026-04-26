from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import math

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
        ("NEW", "New"),
        ("LEARNING", "Learning"),
        ("REVIEW", "Review"),
        ("MASTERED", "Mastered")
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="NEW")
    DIFFICULTY_CHOICES = [
        ("normal", "Normal"),
        ("hard", "Hard"),
        ("easy", "Easy"),
    ]
    
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default="normal")
    # Enhanced SRS tracking
    consecutive_correct = models.IntegerField(default=0)
    next_review_date = models.DateTimeField(default=timezone.now)
    
    # Advanced SRS parameters
    ease_factor = models.FloatField(default=2.5)  # SM-2 ease factor
    interval = models.IntegerField(default=0)  # Current interval in days
    reps = models.IntegerField(default=0)  # Number of successful repetitions
    
    # Statistics tracking
    times_reviewed = models.IntegerField(default=0)
    times_correct = models.IntegerField(default=0)
    times_incorrect = models.IntegerField(default=0)
    last_reviewed = models.DateTimeField(null=True, blank=True)
    first_learned = models.DateTimeField(null=True, blank=True)
    
    # Session tracking
    studied_in_session = models.BooleanField(default=False)
    session_correct = models.BooleanField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "word")

    def calculate_retention_rate(self):
        """Calculate the retention rate as a percentage"""
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

    def mark_remembered(self):
        """Mark word as remembered using improved SM-2 algorithm"""
        from django.utils import timezone
        from datetime import timedelta
        
        self.times_reviewed += 1
        self.times_correct += 1
        self.last_reviewed = timezone.now()
        self.studied_in_session = True
        self.session_correct = True
        
        # Update reps and interval using SM-2 algorithm
        self.reps += 1
        
        if self.reps == 1:
            self.interval = 1
        elif self.reps == 2:
            self.interval = 6
        else:
            self.interval = round(self.interval * self.ease_factor)
        
        # Ensure minimum interval of 1 day
        self.interval = max(1, self.interval)
        
        self.next_review_date = timezone.now() + timedelta(days=self.interval)
        
        # Update status based on progress
        if self.reps >= 5 and self.interval >= 21:
            self.status = "MASTERED"
        else:
            self.status = "REVIEW"
        
        self.difficulty = "easy"
        self.save()

    def mark_forgotten(self):
        """Mark word as forgotten - reset progress"""
        from django.utils import timezone
        
        self.times_reviewed += 1
        self.times_incorrect += 1
        self.last_reviewed = timezone.now()
        self.studied_in_session = True
        self.session_correct = False
        
        # Reset SM-2 parameters
        self.reps = 0
        self.interval = 0
        self.consecutive_correct = 0
        self.ease_factor = max(1.3, self.ease_factor - 0.2)  # Decrease ease factor
        
        self.next_review_date = timezone.now()  # Review immediately
        self.status = "LEARNING"
        self.difficulty = "hard"
        self.save()

    def mark_hard(self):
        """Mark word as hard - review soon with adjusted ease"""
        from django.utils import timezone
        from datetime import timedelta
        
        self.times_reviewed += 1
        self.times_incorrect += 1
        self.last_reviewed = timezone.now()
        self.studied_in_session = True
        self.session_correct = False
        
        # Adjust ease factor down but don't reset completely
        self.ease_factor = max(1.3, self.ease_factor - 0.15)
        
        # Set interval to 1 day for quick review
        self.interval = 1
        self.next_review_date = timezone.now() + timedelta(days=1)
        self.status = "REVIEW"
        self.difficulty = "hard"
        self.save()

    def __str__(self):
        return f"{self.user.username} - {self.word.chinese} - {self.status}"


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
        """Update streak based on last study date"""
        from datetime import date, timedelta
        
        today = date.today()
        
        if self.last_study_date is None:
            self.current_streak = 1
        elif self.last_study_date == today:
            pass  # Already studied today
        elif self.last_study_date == today - timedelta(days=1):
            self.current_streak += 1
        else:
            self.current_streak = 1  # Reset streak
        
        self.longest_streak = max(self.longest_streak, self.current_streak)
        self.last_study_date = today
        self.save()
    
    def reset_daily_goal(self):
        """Reset daily goal counter if it's a new day"""
        from datetime import date
        
        today = date.today()
        if self.last_reset_date != today:
            self.words_studied_today = 0
            self.last_reset_date = today
            self.save()
    
    def get_goal_progress(self):
        """Get daily goal progress as percentage"""
        if self.daily_goal == 0:
            return 0
        return min(100, round((self.words_studied_today / self.daily_goal) * 100))
    
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
