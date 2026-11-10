"""Turn Chinese text into readable pinyin.

Story pinyin used to be written by hand, which let it drift out of sync with
the Chinese it was supposed to transcribe. This module derives it instead.

Words are looked up in the project's own HSK vocabulary first - that pinyin
comes straight from the official word lists, so it already has the right
reading for words a general-purpose converter gets wrong. Anything not in the
vocabulary falls back to pypinyin.
"""

import re

CJK = re.compile(r"[一-鿿]")
CJK_RUN = re.compile(r"[一-鿿]+")
MAX_WORD_LEN = 8

# The stories are transcribed with Latin punctuation, which reads better
# alongside romanised syllables.
PUNCTUATION = {
    "，": ",", "。": ".", "、": ",", "；": ";", "：": ":",
    "？": "?", "！": "!", "（": "(", "）": ")",
    "“": '"', "”": '"', "‘": "'", "’": "'",
    "《": '"', "》": '"', "—": "-", "…": "...",
}
NO_SPACE_BEFORE = set(",.;:?!)\"'") | {"..."}
SENTENCE_END = set(".?!")


class PinyinUnavailable(RuntimeError):
    """Raised when pypinyin is needed but not installed."""


def _fallback(text):
    try:
        from pypinyin import Style, pinyin as _pinyin
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise PinyinUnavailable(
            "pypinyin is required to romanise words outside the HSK vocabulary. "
            "Install it with: pip install pypinyin"
        ) from exc
    return [group[0] for group in _pinyin(text, style=Style.TONE)]


def build_lookup(extra=None):
    """Map Chinese words to pinyin, preferring the project's own word list."""
    from flashcards.models import Word

    lookup = {}
    for chinese, pinyin in Word.objects.values_list("chinese", "pinyin"):
        chinese = (chinese or "").strip()
        pinyin = (pinyin or "").strip()
        if not chinese or not pinyin:
            continue
        # Some entries list variants, e.g. 妈妈｜妈 with pinyin "mā ma ｜ mā".
        # Split them so both forms are usable.
        forms = [part.strip() for part in chinese.split("｜")]
        readings = [part.strip() for part in pinyin.split("｜")]
        if len(forms) != len(readings):
            forms, readings = [chinese], [pinyin]
        for form, reading in zip(forms, readings):
            # Word-list entries also carry annotations such as 下（名、动）;
            # only plain Chinese words are safe to match against running text.
            if not form or not reading or not all(CJK.fullmatch(ch) for ch in form):
                continue
            lookup.setdefault(form, reading)

    for word, pinyin in (extra or {}).items():
        word = (word or "").strip()
        pinyin = (pinyin or "").strip()
        if word and pinyin:
            lookup[word] = pinyin
    return lookup


def _segment(run, lookup):
    """Split a run of Chinese into the longest known words available."""
    tokens = []
    index = 0
    while index < len(run):
        for size in range(min(MAX_WORD_LEN, len(run) - index), 0, -1):
            candidate = run[index:index + size]
            if size > 1 and candidate in lookup:
                tokens.append(candidate)
                index += size
                break
        else:
            tokens.append(run[index])
            index += 1
    return tokens


def _join(pieces):
    out = ""
    for piece in pieces:
        if not piece:
            continue
        if out and not (piece in NO_SPACE_BEFORE or out.endswith(("(", '"', "'"))):
            out += " "
        out += piece
    return out


def _capitalise(line):
    result = []
    start_of_sentence = True
    for char in line:
        if start_of_sentence and char.isalpha():
            result.append(char.upper())
            start_of_sentence = False
        else:
            result.append(char)
            if char in SENTENCE_END:
                start_of_sentence = True
    return "".join(result)


def to_pinyin(text, lookup):
    """Romanise ``text``, keeping its line and paragraph structure."""
    lines = []
    for line in text.split("\n"):
        if not line.strip():
            lines.append("")
            continue

        pieces = []
        position = 0
        for match in CJK_RUN.finditer(line):
            pieces.extend(PUNCTUATION.get(ch, ch) for ch in line[position:match.start()] if ch.strip())
            for token in _segment(match.group(), lookup):
                if token in lookup:
                    pieces.append(lookup[token])
                else:
                    pieces.extend(_fallback(token))
            position = match.end()
        pieces.extend(PUNCTUATION.get(ch, ch) for ch in line[position:] if ch.strip())

        lines.append(_capitalise(_join(pieces)))
    return "\n".join(lines)
