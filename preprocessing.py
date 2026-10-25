"""CriticalLogic-Validator: Text Preprocessing Module.

Provides deterministic regex-based parsing, sentence tokenization, word/character
counts, and text normalization without requiring heavy external NLP libraries.
Follows PEP 8 guidelines.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List


def clean_and_normalize_text(text: str) -> str:
    """Normalize whitespace, remove non-printable control characters, and

    standardize typography (smart quotes, dashes, ligatures).
    """
    if not text:
        return ""

    # Replace smart quotes and special typographical characters
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2014": " -- ",
        "\u2013": " - ",
        "\u2026": "...",
        "\u00a0": " ",
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)

    # Strip control characters except newline and tab
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # Standardize Windows / Mac newlines to Unix \n
    text = re.sub(r"\r\n|\r", "\n", text)

    # Collapse excessive horizontal spaces and tabs into single spaces (preserve newlines)
    text = re.sub(r"[ \t]+", " ", text)

    # Collapse more than two consecutive newlines into two newlines
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)

    return text.strip()


def tokenize_paragraphs(text: str) -> List[str]:
    """Split text into distinct non-empty paragraphs using regex double-newline

    boundaries.
    """
    normalized = clean_and_normalize_text(text)
    if not normalized:
        return []

    raw_paragraphs = re.split(r"\n\s*\n+", normalized)
    return [p.strip() for p in raw_paragraphs if p.strip()]


# Known academic and English abbreviations that do not terminate sentences
COMMON_ABBREVIATIONS = {
    "e.g.",
    "i.e.",
    "et al.",
    "etc.",
    "vs.",
    "cf.",
    "dr.",
    "prof.",
    "mr.",
    "mrs.",
    "ms.",
    "fig.",
    "figs.",
    "vol.",
    "no.",
    "dept.",
    "univ.",
    "ref.",
    "refs.",
    "eq.",
    "eqs.",
    "al.",
    "inc.",
    "ltd.",
    "co.",
    "approx.",
    "ca.",
}


def tokenize_sentences(text: str) -> List[str]:
    """Tokenize text into sentences using a robust regex pattern that protects

    abbreviations, decimal numbers, and trailing quotation marks.
    """
    normalized = clean_and_normalize_text(text)
    if not normalized:
        return []

    # Flatten single linebreaks within paragraphs to space
    flattened = re.sub(r"(?<!\n)\n(?!\n)", " ", normalized)

    # Regex heuristic: split after .!? followed by whitespace and a capital letter or quote
    # Negative lookbehinds protect decimal numbers (e.g. 3.14) and initials
    raw_splits = re.split(
        r"(?<=[.!?])[\"')\]]?\s+(?=[A-Z0-9\"'(\[])",
        flattened,
    )

    sentences: List[str] = []
    buffer = ""

    for segment in raw_splits:
        candidate = (buffer + " " + segment).strip() if buffer else segment.strip()
        if not candidate:
            continue

        # Check if candidate ends with an abbreviation
        ends_with_abbrev = False
        lower_cand = candidate.lower()
        for abbrev in COMMON_ABBREVIATIONS:
            if lower_cand.endswith(abbrev) or lower_cand.endswith(abbrev + "."):
                ends_with_abbrev = True
                break

        # Check single letter initials like "J. Smith"
        if re.search(r"\b[A-Za-z]\.$", candidate):
            ends_with_abbrev = True

        if ends_with_abbrev:
            buffer = candidate
        else:
            sentences.append(candidate)
            buffer = ""

    if buffer:
        sentences.append(buffer)

    return sentences


def tokenize_words(text_segment: str) -> List[str]:
    """Tokenize a sentence or text into alphanumeric word tokens, stripping

    punctuation while keeping hyphenated compound words intact.
    """
    if not text_segment:
        return []
    # Match words including hyphens between letters like 'peer-reviewed'
    words = re.findall(r"\b[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*\b", text_segment)
    return words


def compute_text_statistics(text: str) -> Dict[str, Any]:
    """Compute deterministic text statistics including character, word,

    sentence, paragraph metrics, and lexical density.
    """
    normalized = clean_and_normalize_text(text)
    if not normalized:
        return {
            "char_count_total": 0,
            "char_count_no_spaces": 0,
            "word_count": 0,
            "sentence_count": 0,
            "paragraph_count": 0,
            "avg_sentence_length_words": 0.0,
            "avg_word_length_chars": 0.0,
            "lexical_density": 0.0,
            "sentence_lengths": [],
            "estimated_reading_time_minutes": 0.0,
        }

    paragraphs = tokenize_paragraphs(normalized)
    sentences = tokenize_sentences(normalized)
    words = tokenize_words(normalized)

    total_chars = len(normalized)
    chars_no_spaces = len(re.sub(r"\s+", "", normalized))
    total_words = len(words)
    total_sentences = max(len(sentences), 1 if total_words > 0 else 0)
    total_paragraphs = max(len(paragraphs), 1 if total_words > 0 else 0)

    sentence_lengths = [len(tokenize_words(s)) for s in sentences] if sentences else []

    avg_sentence_len = round(total_words / total_sentences, 1) if total_sentences > 0 else 0.0
    avg_word_len = (
        round(sum(len(w) for w in words) / total_words, 2) if total_words > 0 else 0.0
    )

    # Lexical density: ratio of unique word types to total words (Type-Token Ratio)
    unique_words = len({w.lower() for w in words})
    lexical_density = (
        round((unique_words / total_words) * 100, 1) if total_words > 0 else 0.0
    )

    # Academic average reading speed: ~200 words per minute
    reading_time = round(total_words / 200, 1)

    return {
        "char_count_total": total_chars,
        "char_count_no_spaces": chars_no_spaces,
        "word_count": total_words,
        "sentence_count": total_sentences,
        "paragraph_count": total_paragraphs,
        "avg_sentence_length_words": avg_sentence_len,
        "avg_word_length_chars": avg_word_len,
        "lexical_density": lexical_density,
        "sentence_lengths": sentence_lengths,
        "estimated_reading_time_minutes": reading_time,
    }
