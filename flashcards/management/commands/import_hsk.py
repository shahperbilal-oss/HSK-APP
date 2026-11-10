import os

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from flashcards.hsk_pdf import PdfLayoutError, parse_word_list
from flashcards.models import Word

LEVELS = (1, 2, 3, 4)

# Word counts published for the New HSK (HSK 3.0) levels. Used as a sanity
# check so a silently truncated parse cannot pass unnoticed.
EXPECTED_COUNTS = {1: 500, 2: 772, 3: 973, 4: 1000}


class Command(BaseCommand):
    help = "Import HSK words from the New HSK word list PDFs"
    quiet = False

    def _say(self, message):
        if not self.quiet:
            self.stdout.write(message)

    def add_arguments(self, parser):
        parser.add_argument(
            "--level",
            type=int,
            action="append",
            choices=LEVELS,
            dest="levels",
            help="Import a single level (repeatable). Defaults to all levels.",
        )
        parser.add_argument(
            "--pdf-dir",
            default=None,
            help="Directory holding the New-HSK-<level>-Word-List.pdf files.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what would change without writing to the database.",
        )
        parser.add_argument(
            "--prune",
            action="store_true",
            help="Delete words of the imported levels that are absent from the PDF. "
            "This also deletes any study progress attached to them.",
        )

    def handle(self, *args, **options):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
        base_path = options["pdf_dir"] or project_root
        levels = sorted(set(options["levels"] or LEVELS))
        dry_run = options["dry_run"]
        self.quiet = options["verbosity"] == 0

        totals = {"created": 0, "updated": 0, "unchanged": 0, "pruned": 0}

        for level in levels:
            file_path = os.path.join(base_path, f"New-HSK-{level}-Word-List.pdf")
            if not os.path.exists(file_path):
                self._say(self.style.WARNING(f"File not found: {file_path}"))
                continue

            self._say(f"Parsing HSK Level {level}...")
            try:
                entries = parse_word_list(file_path)
            except PdfLayoutError as exc:
                raise CommandError(f"Could not read {file_path}: {exc}")

            self._check_parse(level, entries)

            with transaction.atomic():
                stats = self._sync_level(level, entries, prune=options["prune"])
                if dry_run:
                    transaction.set_rollback(True)

            for key in totals:
                totals[key] += stats[key]

            self._say(
                self.style.SUCCESS(
                    f"  Level {level}: {len(entries)} words in PDF - "
                    f"{stats['created']} created, {stats['updated']} updated, "
                    f"{stats['unchanged']} unchanged, {stats['pruned']} pruned"
                )
            )

        summary = (
            f"Import complete. Created {totals['created']}, updated {totals['updated']}, "
            f"left {totals['unchanged']} unchanged, pruned {totals['pruned']}."
        )
        if dry_run:
            self._say(self.style.WARNING(f"DRY RUN - nothing was saved. {summary}"))
        else:
            self._say(self.style.SUCCESS(summary))

    def _check_parse(self, level, entries):
        """Warn loudly if the parse does not look complete."""
        numbers = [entry["number"] for entry in entries]
        expected = EXPECTED_COUNTS.get(level)
        if expected and len(entries) != expected:
            self._say(
                self.style.WARNING(
                    f"  Level {level}: parsed {len(entries)} words but expected {expected}."
                )
            )
        gaps = sorted(set(range(1, max(numbers) + 1)) - set(numbers)) if numbers else []
        if gaps:
            self._say(
                self.style.WARNING(f"  Level {level}: missing entry numbers {gaps}")
            )

    def _sync_level(self, level, entries, prune=False):
        """Write parsed entries into the database, preserving study progress.

        Existing rows are matched on the Chinese word first so that a corrected
        pinyin updates the row in place instead of orphaning the learner's
        progress behind a duplicate.
        """
        stats = {"created": 0, "updated": 0, "unchanged": 0, "pruned": 0}

        by_chinese = {}
        for word in Word.objects.filter(hsk_level=level):
            by_chinese.setdefault(word.chinese, []).append(word)
        claimed = set()

        # Pass 1: exact (chinese, pinyin) matches, so a word with several
        # readings keeps each reading on its own row.
        pending = []
        for entry in entries:
            match = next(
                (
                    word
                    for word in by_chinese.get(entry["chinese"], [])
                    if word.pk not in claimed and word.pinyin == entry["pinyin"]
                ),
                None,
            )
            if match is None:
                pending.append(entry)
            else:
                claimed.add(match.pk)
                self._apply(match, entry, stats)

        # Pass 2: same Chinese, changed pinyin - update the row in place.
        for entry in pending:
            match = next(
                (
                    word
                    for word in by_chinese.get(entry["chinese"], [])
                    if word.pk not in claimed
                ),
                None,
            )
            if match is None:
                Word.objects.create(
                    hsk_level=level,
                    chinese=entry["chinese"],
                    pinyin=entry["pinyin"],
                    english=entry["english"],
                )
                stats["created"] += 1
            else:
                claimed.add(match.pk)
                self._apply(match, entry, stats)

        stale = [
            word
            for words in by_chinese.values()
            for word in words
            if word.pk not in claimed
        ]
        if stale:
            label = "Pruning" if prune else "Not in PDF (use --prune to remove)"
            self._say(
                self.style.WARNING(f"  Level {level}: {len(stale)} stale word(s). {label}:")
            )
            for word in stale[:20]:
                self._say(f"    {word.chinese} | {word.pinyin} | {word.english[:40]}")
            if len(stale) > 20:
                self._say(f"    ... and {len(stale) - 20} more")
            if prune:
                Word.objects.filter(pk__in=[word.pk for word in stale]).delete()
                stats["pruned"] = len(stale)

        return stats

    def _apply(self, word, entry, stats):
        changed = [
            field
            for field in ("pinyin", "english")
            if getattr(word, field) != entry[field]
        ]
        if changed:
            word.pinyin = entry["pinyin"]
            word.english = entry["english"]
            word.save(update_fields=changed)
            stats["updated"] += 1
        else:
            stats["unchanged"] += 1
