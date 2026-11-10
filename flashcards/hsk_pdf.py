"""Layout-aware parser for the MandarinBean "New HSK Word List" PDFs.

The PDFs render a four-column table (No | Chinese | Pinyin | English). Reading
the page as a flat stream of text lines is unreliable: a cell can wrap onto a
second visual line, and two cells that sit close together are sometimes emitted
as a single line. Both cases silently desynchronise a line-counting parser.

Instead we work from word coordinates: words are grouped into visual lines,
each word is assigned to a column by its horizontal position, and a line
without a number in the first column is treated as a continuation of the
record above it.
"""

import re

import fitz

# Words whose top edges are within this many points belong to the same line.
ROW_TOLERANCE = 4.0
# Ignore the centred page number printed at the bottom of every page.
FOOTER_MARGIN = 55.0
# Horizontal gap that separates two cells rather than two words inside a cell.
CELL_GAP = 10.0

ID_RE = re.compile(r"^\d{1,4}$")

COLUMNS = ("chinese", "pinyin", "english")


class PdfLayoutError(RuntimeError):
    """Raised when the PDF does not look like a four-column word list."""


def _visual_lines(page):
    """Group a page's words into visual lines, left to right, top to bottom.

    Returns a list of lines, each a list of ``(x0, x1, text)`` tuples.
    """
    limit = page.rect.height - FOOTER_MARGIN
    rows = []
    for x0, y0, x1, y1, text, *_ in page.get_text("words"):
        if y0 >= limit or not text.strip():
            continue
        for row in rows:
            if abs(row[0] - y0) <= ROW_TOLERANCE:
                row[1].append((x0, x1, text))
                break
        else:
            rows.append((y0, [(x0, x1, text)]))
    rows.sort(key=lambda row: row[0])
    for _, words in rows:
        words.sort(key=lambda word: word[0])
    return [words for _, words in rows]


def _split_by_gaps(words):
    """Split one visual line into cells wherever a wide horizontal gap occurs."""
    groups, current = [], [words[0]]
    for previous, word in zip(words, words[1:]):
        if word[0] - previous[1] > CELL_GAP:
            groups.append(current)
            current = []
        current.append(word)
    groups.append(current)
    return groups


def _column_boundaries(doc):
    """Derive the three x-boundaries that separate the four columns.

    Only lines that split cleanly into four cells are used, which is the large
    majority of them; the boundaries are then placed midway between the extent
    of one column and the start of the next.
    """
    lefts = [[] for _ in range(4)]
    rights = [[] for _ in range(4)]
    for page in doc:
        for words in _visual_lines(page):
            if not ID_RE.match(words[0][2]):
                continue
            groups = _split_by_gaps(words)
            if len(groups) != 4:
                continue
            for index, group in enumerate(groups):
                lefts[index].append(min(word[0] for word in group))
                rights[index].append(max(word[1] for word in group))

    if not all(lefts):
        raise PdfLayoutError("could not find four-column rows in the PDF")

    boundaries = []
    for index in range(3):
        edge = max(rights[index])
        start = min(lefts[index + 1])
        if edge > start:
            raise PdfLayoutError(
                f"columns {index} and {index + 1} overlap "
                f"({edge:.1f} > {start:.1f}); the layout is not a clean table"
            )
        boundaries.append((edge + start) / 2)
    return boundaries


def _column_of(x0, x1, boundaries):
    middle = (x0 + x1) / 2
    for index, boundary in enumerate(boundaries):
        if middle < boundary:
            return index
    return len(boundaries)


def _clean(text):
    return re.sub(r"\s+", " ", text).strip()


def _assemble(record):
    """Turn collected tokens into a finished word.

    Chinese is joined without spaces; pinyin and English keep single spaces.
    A lone tone-marked vowel is a font artefact of the previous syllable
    (e.g. "yu" + "è" is really "yuè"), so it is glued back on.
    """
    pinyin_parts = []
    for token in record["pinyin"]:
        if pinyin_parts and len(token) == 1 and token in "āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ":
            pinyin_parts[-1] += token
        else:
            pinyin_parts.append(token)

    return {
        "number": record["number"],
        "chinese": _clean("".join(record["chinese"])),
        "pinyin": _clean(" ".join(pinyin_parts)),
        "english": _clean(" ".join(record["english"])),
    }


def parse_word_list(pdf_path):
    """Parse a New HSK word-list PDF into a list of word dictionaries.

    Each entry has ``number``, ``chinese``, ``pinyin`` and ``english`` keys.
    """
    doc = fitz.open(pdf_path)
    try:
        boundaries = _column_boundaries(doc)
        records, current = [], None
        for page in doc:
            for words in _visual_lines(page):
                cells = {name: [] for name in COLUMNS}
                number = []
                for x0, x1, text in words:
                    column = _column_of(x0, x1, boundaries)
                    if column == 0:
                        number.append(text)
                    else:
                        cells[COLUMNS[column - 1]].append(text)

                label = "".join(number).strip()
                if ID_RE.match(label):
                    current = {"number": int(label), **{name: [] for name in COLUMNS}}
                    records.append(current)
                elif current is None or label:
                    # Column headings, cover text, or stray marks in the No column.
                    continue

                for name in COLUMNS:
                    current[name].extend(cells[name])
    finally:
        doc.close()

    return [_assemble(record) for record in records]
