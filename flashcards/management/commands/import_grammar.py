from django.core.management.base import BaseCommand
from django.db import transaction

from flashcards.grammar_data import ALL_GRAMMAR_POINTS
from flashcards.models import GrammarPoint


class Command(BaseCommand):
    help = (
        "Import the canonical HSK 1-4 grammar points from flashcards/grammar_data.py. "
        "Use --prune to drop points that are no longer part of that list."
    )
    quiet = False

    def _say(self, message):
        if not self.quiet:
            self.stdout.write(message)

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what would change without writing to the database.",
        )
        parser.add_argument(
            "--prune",
            action="store_true",
            help="Delete grammar points that are not in the canonical list, "
            "including entries left at an invalid level.",
        )

    def handle(self, *args, **options):
        self.quiet = options["verbosity"] == 0
        created = updated = unchanged = pruned = 0

        with transaction.atomic():
            keep = set()
            for item in ALL_GRAMMAR_POINTS:
                first = item["examples"][0]
                point, is_created = GrammarPoint.objects.get_or_create(
                    level=item["level"],
                    title=item["title"],
                    defaults={"explanation": "", "detailed_explanation": ""},
                )
                keep.add(point.pk)

                fields = {
                    "explanation": item["explanation"],
                    "detailed_explanation": item["detailed_explanation"],
                    "example_cn": first["cn"],
                    "example_pinyin": first["pinyin"],
                    "example_en": first["en"],
                    "examples": item["examples"],
                }
                changed = [
                    name for name, value in fields.items() if getattr(point, name) != value
                ]
                if is_created:
                    for name, value in fields.items():
                        setattr(point, name, value)
                    point.save()
                    created += 1
                elif changed:
                    for name in changed:
                        setattr(point, name, fields[name])
                    point.save(update_fields=changed)
                    updated += 1
                else:
                    unchanged += 1

            stale = GrammarPoint.objects.exclude(pk__in=keep)
            stale_count = stale.count()
            if stale_count:
                by_level = {}
                for level, title in stale.values_list("level", "title"):
                    by_level.setdefault(level, set()).add(title)
                label = "Pruning" if options["prune"] else "Not in the canonical list (use --prune)"
                self._say(self.style.WARNING(f"{stale_count} stale grammar point(s). {label}:"))
                for level in sorted(by_level):
                    titles = sorted(by_level[level])
                    preview = ", ".join(titles[:6]) + (" ..." if len(titles) > 6 else "")
                    self._say(f"  level {level}: {len(titles)} distinct title(s) - {preview}")
                if options["prune"]:
                    stale.delete()
                    pruned = stale_count

            if options["dry_run"]:
                transaction.set_rollback(True)

        summary = (
            f"Grammar import complete. Created {created}, updated {updated}, "
            f"left {unchanged} unchanged, pruned {pruned}. "
            f"Canonical list holds {len(ALL_GRAMMAR_POINTS)} points."
        )
        if options["dry_run"]:
            self._say(self.style.WARNING(f"DRY RUN - nothing was saved. {summary}"))
        else:
            self._say(self.style.SUCCESS(summary))
