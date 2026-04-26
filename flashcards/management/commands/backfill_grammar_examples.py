from django.core.management.base import BaseCommand

from flashcards.models import GrammarPoint


GENERIC_EXAMPLES = [
    {"cn": "这个语法点很常用。", "pinyin": "Zhège yǔfǎ diǎn hěn chángyòng.", "en": "This grammar point is very commonly used."},
    {"cn": "请用这个结构造句。", "pinyin": "Qǐng yòng zhège jiégòu zàojù.", "en": "Please make a sentence using this structure."},
    {"cn": "老师在课上解释了这个语法。", "pinyin": "Lǎoshī zài kè shàng jiěshì le zhège yǔfǎ.", "en": "The teacher explained this grammar in class."},
    {"cn": "我需要多练习这个句型。", "pinyin": "Wǒ xūyào duō liànxí zhège jùxíng.", "en": "I need to practice this sentence pattern more."},
    {"cn": "掌握这个语法以后，表达会更自然。", "pinyin": "Zhǎngwò zhège yǔfǎ yǐhòu, biǎodá huì gèng zìrán.", "en": "After mastering this grammar, expression becomes more natural."},
]


class Command(BaseCommand):
    help = "Backfill HSK 1-4 grammar points with detailed explanations and 5 examples each."

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

            while len(normalized) < 5:
                normalized.append(GENERIC_EXAMPLES[len(normalized)])

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
