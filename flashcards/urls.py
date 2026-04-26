from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('study/', views.study_levels, name='study_levels'),
    path('study/<int:level>/', views.study_session, name='study_session_level'),
    path('study/action/<int:word_id>/<str:action>/', views.review_action, name='review_action'),
    path('words/', views.word_list, name='word_list'),
    path('init_user_words/', views.init_user_words, name='init_user_words'),
    path('words/hard/', views.hard_words, name='hard_words'),
    path('words/easy/', views.easy_words, name='easy_words'),
    path('study/hard/', views.study_hard_words, name='study_hard_words'),
    path('study/easy/', views.study_easy_words, name='study_easy_words'),
    path('grammar/', views.grammar_list, name='grammar_list'),
    path('grammar/level/<int:level>/', views.grammar_list, name='grammar_list_level'),
    path('grammar/<int:pk>/', views.grammar_detail, name='grammar_detail'),
    path('stats/', views.stats_view, name='stats'),
    
    # Book & Reading section URLs
    path('books/', views.book_list, name='book_list'),
    path('book/<int:book_id>/', views.chapter_list, name='chapter_list'),
    path('read/<int:segment_id>/', views.read_segment, name='read_segment'),
    path('api/tts/', views.text_to_speech, name='text_to_speech'),
    path('stories/', views.story_store, name='story_store'),
    path('stories/level/<int:level>/', views.story_store, name='story_store_level'),
    path('stories/<int:pk>/', views.story_detail, name='story_detail'),
    path('stories/<int:story_id>/save-word/', views.save_story_word, name='save_story_word'),
    path('saved-words/', views.saved_words, name='saved_words'),
    path('saved-words/export/pdf/', views.export_saved_words_pdf, name='export_saved_words_pdf'),
    path('dialogues/', views.dialogue_list, name='dialogue_list'),
    path('dialogues/category/<str:category>/', views.dialogue_list, name='dialogue_list_category'),
    path('dialogues/<int:pk>/', views.dialogue_detail, name='dialogue_detail'),

    # JSON API
    path('api/words/', views.api_words, name='api_words'),
    path('api/study/<int:level>/next/', views.api_study_next, name='api_study_next'),
    path('api/stories/', views.api_stories, name='api_stories'),
    path('api/stories/<int:pk>/', views.api_story_detail, name='api_story_detail'),
    path('api/dialogues/', views.api_dialogues, name='api_dialogues'),
    path('api/dialogues/<int:pk>/', views.api_dialogue_detail, name='api_dialogue_detail'),
    path('api/saved-words/', views.api_saved_words, name='api_saved_words'),
]
