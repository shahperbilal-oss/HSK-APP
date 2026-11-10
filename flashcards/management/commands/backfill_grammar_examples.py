from django.core.management.base import BaseCommand

from flashcards.models import GrammarPoint


class Command(BaseCommand):
    """Repair grammar points that predate flashcards/grammar_data.py.

    An earlier version padded every point up to five examples with generic
    filler sentences such as "This grammar point is very commonly used", which
    taught the learner nothing. Padding has been removed: a point now keeps
    only its real examples, and `import_grammar` is the place to add more.
    """

    help = (
        "Repair legacy grammar points: normalise their examples and fill in a "
        "missing detailed explanation. Does not invent example sentences."
    )

    def handle(self, *args, **options):
        updated = 0
        unchanged = 0

        for gp in GrammarPoint.objects.filter(level__in=[1, 2, 3, 4]).order_by("level", "title"):
            changed = False

            if not (gp.detailed_explanation or "").strip():
                base = (gp.explanation or "").strip()
                gp.detailed_explanation = (
                    f"{base}\n\n"
                    "Usage notes:\n"
                    "- Learn the sentence order before adding extra words.\n"
                    "- Practice with short daily examples and then extend naturally.\n"
                    "- Pay attention to context, tone, and common collocations."
                ).strip()
                changed = True

            examples = list(gp.examples or [])
            normalized = []
            for ex in examples:
                if isinstance(ex, dict):
                    cn = (ex.get("cn") or "").strip()
                    py = (ex.get("pinyin") or "").strip()
                    en = (ex.get("en") or "").strip()
                    if cn and en:
                        normalized.append({"cn": cn, "pinyin": py, "en": en})

            if gp.example_cn.strip() and gp.example_en.strip():
                legacy = {
                    "cn": gp.example_cn.strip(),
                    "pinyin": (gp.example_pinyin or "").strip(),
                    "en": gp.example_en.strip(),
                }
                if legacy not in normalized:
                    normalized.insert(0, legacy)

            normalized = normalized[:5]
            if gp.examples != normalized:
                gp.examples = normalized
                changed = True

            if changed:
                gp.save(update_fields=["detailed_explanation", "examples"])
                updated += 1
            else:
                unchanged += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Backfill complete. Updated {updated} grammar points, unchanged {unchanged}."
            )
        )
