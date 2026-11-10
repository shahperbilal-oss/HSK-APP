import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hsk_project.settings')
django.setup()
from flashcards.models import Word
words = list(Word.objects.filter(hsk_level=1).values('chinese','pinyin','english'))
with open('hsk1_words.txt', 'w', encoding='utf-8') as f:
    for w in words:
        f.write(f'{w["chinese"]}|{w["pinyin"]}|{w["english"]}\n')
print('Done -', len(words), 'words')
