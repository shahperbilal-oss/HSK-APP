from django.contrib import admin
from .models import Word, UserWord, UserProfile, Review, GrammarPoint, Book, Chapter, TextSegment, Story, SavedWord, Dialogue

@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('chinese', 'pinyin', 'english', 'hsk_level', 'frequency_rank')
    list_filter = ('hsk_level',)
    search_fields = ('chinese', 'pinyin', 'english')
    ordering = ('hsk_level', 'chinese')
    fieldsets = (
        ('Basic Information', {
            'fields': ('chinese', 'pinyin', 'english', 'hsk_level')
        }),
        ('Character Details', {
            'fields': ('character_breakdown', 'radical', 'stroke_count', 'frequency_rank')
        }),
        ('Learning Content', {
            'fields': ('usage_notes', 'grammar_points', 'example_sentences')
        }),
        ('Related Words', {
            'fields': ('synonyms', 'antonyms')
        }),
    )

@admin.register(UserWord)
class UserWordAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'word', 'status', 'difficulty', 'flagged',
        'interval', 'ease_factor', 'lapses', 'consecutive_correct', 'next_review_date',
    )
    list_filter = ('status', 'difficulty', 'flagged')
    search_fields = ('user__username', 'word__chinese', 'word__pinyin')
    raw_id_fields = ('user', 'word')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'reviewed_at', 'user_word', 'rating',
        'state_before', 'interval_before', 'state_after', 'interval_after', 'elapsed_days',
    )
    list_filter = ('rating', 'state_before', 'state_after')
    search_fields = ('user_word__word__chinese', 'user_word__user__username')
    raw_id_fields = ('user_word',)
    date_hierarchy = 'reviewed_at'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'current_streak', 'longest_streak', 'daily_goal', 'words_studied_today',
        'new_cards_per_day', 'new_cards_today', 'total_words_learned',
    )
    list_filter = ('current_streak',)
    search_fields = ('user__username',)

@admin.register(GrammarPoint)
class GrammarPointAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'example_cn')
    list_filter = ('level',)
    search_fields = ('title', 'explanation', 'example_cn')
    ordering = ('level', 'title')

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'hsk_level', 'get_chapter_count', 'created_at')
    list_filter = ('hsk_level',)
    search_fields = ('title', 'description')
    ordering = ('hsk_level', 'title')

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('title', 'book', 'chapter_number', 'get_segment_count')
    list_filter = ('book',)
    search_fields = ('title', 'summary')
    ordering = ('book', 'chapter_number')

@admin.register(TextSegment)
class TextSegmentAdmin(admin.ModelAdmin):
    list_display = ('order', 'chapter', 'get_chinese_preview', 'has_audio')
    list_filter = ('chapter',)
    search_fields = ('chinese_text', 'pinyin', 'english_translation')
    ordering = ('chapter', 'order')
    filter_horizontal = ('key_words',)
    
    def get_chinese_preview(self, obj):
        preview = obj.chinese_text[:50] + "..." if len(obj.chinese_text) > 50 else obj.chinese_text
        return preview
    get_chinese_preview.short_description = "Chinese Text"
    
    def has_audio(self, obj):
        return "✓" if obj.audio_file else "✗"
    has_audio.short_description = "Audio"


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ("title", "level")
    list_filter = ("level",)
    search_fields = ("title", "chinese_text", "pinyin_text", "english_translation")
    ordering = ("level", "title")


@admin.register(SavedWord)
class SavedWordAdmin(admin.ModelAdmin):
    list_display = ("word", "user", "story", "created_at")
    list_filter = ("user", "story")
    search_fields = ("word", "pinyin", "english", "user__username")
    ordering = ("-created_at",)


@admin.register(Dialogue)
class DialogueAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "level")
    list_filter = ("category", "level")
    search_fields = ("title",)
    ordering = ("category", "level", "title")
