import os
import re
import unittest

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

from flashcards.hsk_pdf import parse_word_list
from flashcards.management.commands.import_hsk import EXPECTED_COUNTS
from flashcards.models import UserWord, Word

PDF_DIR = settings.BASE_DIR
CJK_RE = re.compile(r"[一-鿿]")


def pdf_path(level):
    return os.path.join(PDF_DIR, f"New-HSK-{level}-Word-List.pdf")


def pdfs_available():
    return all(os.path.exists(pdf_path(level)) for level in EXPECTED_COUNTS)


@unittest.skipUnless(pdfs_available(), "New HSK word list PDFs are not present")
class WordListPdfTests(TestCase):
    """The PDFs are the source of truth, so the parser is checked against them."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.parsed = {level: parse_word_list(pdf_path(level)) for level in EXPECTED_COUNTS}

    def test_every_level_yields_the_published_word_count(self):
        for level, expected in EXPECTED_COUNTS.items():
            with self.subTest(level=level):
                self.assertEqual(len(self.parsed[level]), expected)

    def test_entry_numbers_run_from_one_without_gaps_or_repeats(self):
        for level, entries in self.parsed.items():
            with self.subTest(level=level):
                numbers = [entry["number"] for entry in entries]
                self.assertEqual(numbers, list(range(1, len(entries) + 1)))

    def test_no_entry_has_an_empty_field(self):
        for level, entries in self.parsed.items():
            for entry in entries:
                with self.subTest(level=level, number=entry["number"]):
                    self.assertTrue(entry["chinese"])
                    self.assertTrue(entry["pinyin"])
                    self.assertTrue(entry["english"])

    def test_columns_do_not_bleed_into_each_other(self):
        for level, entries in self.parsed.items():
            for entry in entries:
                with self.subTest(level=level, number=entry["number"]):
                    self.assertRegex(entry["chinese"], CJK_RE)
                    self.assertNotRegex(entry["pinyin"], CJK_RE)
                    self.assertNotRegex(entry["english"], CJK_RE)

    def test_wrapped_cells_are_joined_rather_than_truncated(self):
        # This HSK 4 entry wraps onto a second line in the PDF; the old
        # line-by-line parser kept only the first half of it.
        entry = next(e for e in self.parsed[4] if e["chinese"] == "闪")
        self.assertEqual(
            entry["english"],
            "dodge; get out of the way; sprain; flash; sparkle; shine; lightning",
        )

    def test_the_column_heading_row_is_not_read_as_a_word(self):
        for level, entries in self.parsed.items():
            with self.subTest(level=level):
                self.assertNotIn("No", [entry["chinese"] for entry in entries])


@unittest.skipUnless(pdfs_available(), "New HSK word list PDFs are not present")
class ImportHskCommandTests(TestCase):
    def test_import_loads_a_level_in_full(self):
        call_command("import_hsk", "--level", "1", verbosity=0)
        self.assertEqual(Word.objects.filter(hsk_level=1).count(), EXPECTED_COUNTS[1])

    def test_rerunning_the_import_does_not_duplicate_words(self):
        call_command("import_hsk", "--level", "1", verbosity=0)
        call_command("import_hsk", "--level", "1", verbosity=0)
        self.assertEqual(Word.objects.filter(hsk_level=1).count(), EXPECTED_COUNTS[1])

    def test_dry_run_writes_nothing(self):
        call_command("import_hsk", "--level", "1", "--dry-run", verbosity=0)
        self.assertEqual(Word.objects.filter(hsk_level=1).count(), 0)

    def test_correcting_a_word_keeps_the_learners_progress(self):
        # A word imported by the old parser with a truncated pinyin should be
        # corrected in place, not replaced by a second row.
        stale = Word.objects.create(
            hsk_level=1, chinese="电影院", pinyin="diàn yǐng", english="yuàn"
        )
        user = User.objects.create(username="learner")
        progress = UserWord.objects.create(user=user, word=stale, status="MASTERED", reps=7)

        call_command("import_hsk", "--level", "1", verbosity=0)

        stale.refresh_from_db()
        progress.refresh_from_db()
        self.assertEqual(Word.objects.filter(hsk_level=1, chinese="电影院").count(), 1)
        self.assertEqual(stale.pinyin, "diàn yǐng yuàn")
        self.assertEqual(stale.english, "cinema; movie theater")
        self.assertEqual(progress.word_id, stale.pk)
        self.assertEqual(progress.status, "MASTERED")
        self.assertEqual(progress.reps, 7)

    def test_words_with_several_readings_stay_on_separate_rows(self):
        call_command("import_hsk", "--level", "1", verbosity=0)
        readings = Word.objects.filter(hsk_level=1, chinese="还").values_list("pinyin", flat=True)
        self.assertEqual(set(readings), {"hái", "huán"})

    def test_prune_removes_words_that_are_not_in_the_pdf(self):
        Word.objects.create(hsk_level=1, chinese="No", pinyin="Chinese", english="Pinyin")
        call_command("import_hsk", "--level", "1", "--prune", verbosity=0)
        self.assertFalse(Word.objects.filter(hsk_level=1, chinese="No").exists())
        self.assertEqual(Word.objects.filter(hsk_level=1).count(), EXPECTED_COUNTS[1])

    def test_words_outside_the_imported_level_are_left_alone(self):
        keeper = Word.objects.create(
            hsk_level=2, chinese="測試", pinyin="cè shì", english="test"
        )
        call_command("import_hsk", "--level", "1", "--prune", verbosity=0)
        self.assertTrue(Word.objects.filter(pk=keeper.pk).exists())
