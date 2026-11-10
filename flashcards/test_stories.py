"""Tests for the story reader, in particular the side-by-side layout.

Putting the three texts in columns only works if they line up, and the stories
in the database do not all agree on how their pinyin is stored.
"""

from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from flashcards import pinyin_text
from flashcards.models import Story
from flashcards.views import _story_paragraphs

CHINESE = "我有一只猫。\n他很可爱。\n我很喜欢他。"
PINYIN = "Wǒ yǒu yì zhī māo.\nTā hěn kě'ài.\nWǒ hěn xǐhuān tā."
ENGLISH = "I have a cat.\nHe is very cute.\nI like him a lot."


def make_story(**overrides):
    fields = {
        "level": 1,
        "title": "我的猫",
        "chinese_text": CHINESE,
        "pinyin_text": PINYIN,
        "english_translation": ENGLISH,
    }
    fields.update(overrides)
    return Story.objects.create(**fields)


class ParagraphAlignmentTests(TestCase):
    def test_matching_texts_line_up_one_row_per_paragraph(self):
        rows = _story_paragraphs(make_story())

        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[1]["chinese"], "他很可爱。")
        self.assertEqual(rows[1]["pinyin"], "Tā hěn kě'ài.")
        self.assertEqual(rows[1]["english"], "He is very cute.")

    def test_blank_lines_between_paragraphs_are_ignored(self):
        story = make_story(
            chinese_text=CHINESE.replace("\n", "\n\n"),
            pinyin_text=PINYIN.replace("\n", "\n\n"),
            english_translation=ENGLISH.replace("\n", "\n\n"),
        )

        self.assertEqual(len(_story_paragraphs(story)), 3)

    def test_pinyin_stored_as_one_blob_is_derived_per_paragraph(self):
        # Half the stories store pinyin as a single unbroken line, which
        # cannot be placed beside anything.
        story = make_story(pinyin_text=PINYIN.replace("\n", " "))

        rows = _story_paragraphs(story)

        self.assertEqual(len(rows), 3)
        self.assertTrue(all(row["pinyin"] for row in rows))
        # Derived from the Chinese it sits next to, so it tracks that column.
        self.assertIn("māo", rows[0]["pinyin"])
        self.assertNotIn("māo", rows[2]["pinyin"])

    def test_missing_pinyin_is_derived_rather_than_left_empty(self):
        rows = _story_paragraphs(make_story(pinyin_text=""))

        self.assertTrue(all(row["pinyin"] for row in rows))

    def test_an_uneven_translation_pads_instead_of_failing(self):
        # Translators merge and split paragraphs; a short English column must
        # not take the page down with it.
        rows = _story_paragraphs(make_story(english_translation="I have a cat."))

        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]["english"], "I have a cat.")
        self.assertEqual(rows[2]["english"], "")

    def test_the_page_still_works_without_pypinyin(self):
        story = make_story(pinyin_text="")

        with patch.object(
            pinyin_text, "to_pinyin", side_effect=pinyin_text.PinyinUnavailable("no pypinyin")
        ):
            rows = _story_paragraphs(story)

        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]["pinyin"], "")
        self.assertEqual(rows[0]["english"], "I have a cat.")


class StoryDetailViewTests(TestCase):
    def setUp(self):
        self.story = make_story()
        self.url = reverse("story_detail", args=[self.story.pk])

    def test_side_by_side_is_the_default_layout(self):
        response = self.client.get(self.url)

        self.assertEqual(response.context["layout"], "columns")
        self.assertContains(response, "story-columns")
        self.assertContains(response, "story-row")

    def test_every_paragraph_becomes_a_row(self):
        response = self.client.get(self.url)

        self.assertEqual(len(response.context["rows"]), 3)
        self.assertContains(response, 'class="story-row"', count=3)

    def test_the_stacked_layout_is_still_available(self):
        response = self.client.get(self.url, {"layout": "stacked"})

        self.assertEqual(response.context["layout"], "stacked")
        self.assertNotContains(response, "story-columns")

    def test_hiding_pinyin_drops_the_middle_column(self):
        response = self.client.get(self.url, {"show_pinyin": "0"})

        self.assertFalse(response.context["show_pinyin"])
        self.assertContains(response, "is-two-column")
        self.assertNotContains(response, "story-cell-py")

    def test_chinese_stays_clickable_in_the_side_by_side_layout(self):
        response = self.client.get(self.url)

        self.assertContains(response, "saveable-word")

    def test_an_unknown_layout_falls_back_to_columns(self):
        response = self.client.get(self.url, {"layout": "nonsense"})

        self.assertEqual(response.context["layout"], "columns")
