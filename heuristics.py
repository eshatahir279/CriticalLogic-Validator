"""CriticalLogic-Validator: Local Algorithmic Heuristics Module.

Performs deterministic rule-based analysis prior to LLM evaluation:
- Passive voice detection with auxiliary verbs + past participles
- Academic transition density scanning
- Sentence length variance & complexity analysis
- Readability metrics (Flesch Reading Ease, Flesch-Kincaid Grade)
- Structural Clarity Score (0-100 composite index)
"""

from __future__ import annotations

import math
import re
from typing import Any, Dict, List, Set, Tuple

from preprocessing import (
    clean_and_normalize_text,
    tokenize_paragraphs,
    tokenize_sentences,
    tokenize_words,
)

# Auxiliary verb lemmas and conjugations
AUXILIARY_VERBS: Set[str] = {
    "is",
    "was",
    "were",
    "been",
    "be",
    "are",
    "am",
    "being",
    "get",
    "got",
    "gets",
    "getting",
}

# Common irregular past participles common in academic writing
IRREGULAR_PAST_PARTICIPLES: Set[str] = {
    "arisen", "awoken", "borne", "beaten", "become", "begun", "bent", "bound",
    "bitten", "blown", "broken", "brought", "built", "burnt", "bought", "caught",
    "chosen", "clung", "come", "cost", "crept", "cut", "dealt", "dug", "done",
    "drawn", "dreamt", "driven", "drunk", "eaten", "fallen", "fed", "felt",
    "fought", "found", "fled", "flung", "flown", "forbidden", "forgotten",
    "forgiven", "frozen", "gotten", "given", "gone", "grown", "hung", "heard",
    "hidden", "hit", "held", "hurt", "kept", "knelt", "known", "laid", "led",
    "learnt", "left", "lent", "let", "lain", "lit", "lost", "made", "meant",
    "met", "paid", "proven", "put", "read", "ridden", "rung", "risen", "run",
    "said", "seen", "sought", "sold", "sent", "set", "shaken", "shone", "shot",
    "shown", "shut", "sung", "sunk", "sat", "slept", "slid", "spoken", "spent",
    "split", "spread", "sprung", "stood", "stolen", "stuck", "stung", "struck",
    "strung", "sworn", "swept", "swum", "swung", "taken", "taught", "torn",
    "told", "thought", "thrown", "understood", "undertaken", "upset", "woken",
    "worn", "won", "wound", "written"
}

# Words ending in -ed that are common adjectives/nouns, not passive participles
ADJECTIVE_EXCLUSIONS: Set[str] = {
    "red", "bed", "led", "shed", "fed", "speed", "seed", "need", "reed",
    "weed", "bleed", "breed", "creed", "freed", "greed", "tired", "naked",
    "wicked", "sacred", "beloved", "crooked", "ragged", "aged"
}

# Academic transition words and phrases categorized
TRANSITION_CATEGORIES: Dict[str, List[str]] = {
    "additive": [
        "furthermore", "moreover", "in addition", "additionally",
        "likewise", "similarly", "not only", "what is more", "further"
    ],
    "adversative": [
        "however", "nevertheless", "nonetheless", "on the contrary",
        "in contrast", "conversely", "despite this", "in spite of",
        "on the other hand", "whereas", "although", "even though",
        "notwithstanding", "yet"
    ],
    "causal": [
        "therefore", "consequently", "thus", "hence", "as a result",
        "accordingly", "for this reason", "thereby", "subsequently",
        "it follows that"
    ],
    "sequential": [
        "firstly", "secondly", "thirdly", "finally", "subsequently",
        "initially", "eventually", "in conclusion", "to summarize",
        "overall", "in summary"
    ],
}


def count_syllables_word(word: str) -> int:
    """Estimate the number of syllables in an English word using regex heuristics."""
    word = word.lower().strip()
    if not word:
        return 0
    if len(word) <= 3:
        return 1

    # Strip non-alphanumeric
    word = re.sub(r"[^a-z]", "", word)
    if not word:
        return 1

    # Remove silent 'e' at the end (unless ends with -le with preceding consonant)
    if word.endswith("e") and not (word.endswith("le") and len(word) > 2 and word[-3] not in "aeiouy"):
        word = word[:-1]

    # Count vowel sequences
    vowel_runs = re.findall(r"[aeiouy]+", word)
    count = len(vowel_runs)

    return max(1, count)


def detect_passive_voice(text: str) -> Dict[str, Any]:
    """Detect passive voice occurrences across sentences.

    Flags auxiliary verbs ('is', 'was', 'were', etc.) paired with past
    participles within 1-3 intervening tokens (e.g. 'was meticulously
    analyzed'). Returns flagged sentences, matched tokens, and percentages.
    """
    sentences = tokenize_sentences(text)
    flagged_sentences = []
    total_passive_count = 0

    # Build regex pattern for passive construction:
    # (auxiliary) + optional 1-3 intervening adverbs + (participle in -ed or irregular)
    aux_pattern = r"\b(" + "|".join(re.escape(aux) for aux in AUXILIARY_VERBS) + r")\b"
    adv_pattern = r"(?:\s+[a-zA-Z]+(?:ly|wards|wise|often|never|always|well|much|also|even|clearly|already|widely))?"
    adv_chain = adv_pattern + adv_pattern + adv_pattern

    for idx, sentence in enumerate(sentences):
        sentence_matches = []
        words = tokenize_words(sentence)
        lower_sentence = sentence.lower()

        # Token-based scanner
        for i, word in enumerate(words):
            if word.lower() in AUXILIARY_VERBS:
                # Look ahead 1 to 4 tokens for past participle
                for offset in range(1, 5):
                    if i + offset < len(words):
                        target = words[i + offset].lower()
                        # Check past participle match
                        is_participle = False
                        if target in IRREGULAR_PAST_PARTICIPLES:
                            is_participle = True
                        elif target.endswith("ed") and target not in ADJECTIVE_EXCLUSIONS and len(target) > 3:
                            is_participle = True

                        if is_participle:
                            matched_span = " ".join(words[i : i + offset + 1])
                            sentence_matches.append({
                                "auxiliary": word,
                                "participle": words[i + offset],
                                "phrase": matched_span,
                            })
                            break

        if sentence_matches:
            flagged_sentences.append({
                "index": idx + 1,
                "sentence": sentence,
                "matches": sentence_matches,
                "match_count": len(sentence_matches),
            })
            total_passive_count += len(sentence_matches)

    total_sentences = len(sentences)
    passive_sentence_count = len(flagged_sentences)
    passive_ratio = (
        round((passive_sentence_count / total_sentences) * 100, 1)
        if total_sentences > 0
        else 0.0
    )

    return {
        "total_passive_matches": total_passive_count,
        "passive_sentence_count": passive_sentence_count,
        "total_sentences": total_sentences,
        "passive_percentage": passive_ratio,
        "flagged_sentences": flagged_sentences,
    }


def scan_transition_density(text: str) -> Dict[str, Any]:
    """Scan and compute academic transition word density and category distribution."""
    normalized = clean_and_normalize_text(text).lower()
    words = tokenize_words(text)
    total_words = len(words)

    found_transitions = []
    category_counts = {cat: 0 for cat in TRANSITION_CATEGORIES}

    for category, phrases in TRANSITION_CATEGORIES.items():
        for phrase in phrases:
            # Word boundary regex search for phrase
            pattern = r"\b" + re.escape(phrase) + r"\b"
            matches = list(re.finditer(pattern, normalized))
            if matches:
                count = len(matches)
                category_counts[category] += count
                found_transitions.append({
                    "phrase": phrase,
                    "category": category,
                    "count": count,
                })

    total_transitions = sum(category_counts.values())
    # Density as transitions per 100 words
    density_per_100_words = (
        round((total_transitions / total_words) * 100, 2) if total_words > 0 else 0.0
    )

    return {
        "total_transitions": total_transitions,
        "density_per_100_words": density_per_100_words,
        "category_counts": category_counts,
        "found_transitions": sorted(found_transitions, key=lambda x: x["count"], reverse=True),
    }


def analyze_sentence_complexity(text: str) -> Dict[str, Any]:
    """Analyze sentence length distribution, standard deviation (variance), and

    flag run-on or overly clipped sentences.
    """
    sentences = tokenize_sentences(text)
    if not sentences:
        return {
            "sentence_lengths": [],
            "mean_length": 0.0,
            "variance": 0.0,
            "std_dev": 0.0,
            "run_on_count": 0,
            "choppy_count": 0,
            "run_on_sentences": [],
            "choppy_sentences": [],
        }

    lengths = [len(tokenize_words(s)) for s in sentences]
    mean_length = sum(lengths) / len(lengths)

    # Variance and standard deviation
    squared_diffs = [(l - mean_length) ** 2 for l in lengths]
    variance = sum(squared_diffs) / len(lengths)
    std_dev = math.sqrt(variance)

    run_on_sentences = []
    choppy_sentences = []

    for idx, (sent, length) in enumerate(zip(sentences, lengths)):
        if length > 38:  # Run-on threshold for academic rigor
            run_on_sentences.append({"index": idx + 1, "length": length, "sentence": sent})
        elif length < 6:  # Choppy fragment threshold
            choppy_sentences.append({"index": idx + 1, "length": length, "sentence": sent})

    return {
        "sentence_lengths": lengths,
        "mean_length": round(mean_length, 1),
        "variance": round(variance, 2),
        "std_dev": round(std_dev, 2),
        "run_on_count": len(run_on_sentences),
        "choppy_count": len(choppy_sentences),
        "run_on_sentences": run_on_sentences,
        "choppy_sentences": choppy_sentences,
    }


def compute_readability_scores(text: str) -> Dict[str, Any]:
    """Calculate Flesch Reading Ease and Flesch-Kincaid Grade Level."""
    words = tokenize_words(text)
    sentences = tokenize_sentences(text)

    total_words = len(words)
    total_sentences = len(sentences)
    if total_words == 0 or total_sentences == 0:
        return {
            "flesch_reading_ease": 0.0,
            "flesch_kincaid_grade": 0.0,
            "reading_ease_label": "N/A",
            "grade_level_label": "N/A",
            "syllables_per_word": 0.0,
        }

    total_syllables = sum(count_syllables_word(w) for w in words)
    words_per_sentence = total_words / total_sentences
    syllables_per_word = total_syllables / total_words

    # Flesch Reading Ease
    fre = 206.835 - (1.015 * words_per_sentence) - (84.6 * syllables_per_word)
    fre = max(0.0, min(100.0, fre))

    # Flesch-Kincaid Grade Level
    fkgl = (0.39 * words_per_sentence) + (11.8 * syllables_per_word) - 15.59
    fkgl = max(0.0, fkgl)

    # Qualitative labels
    if fre >= 70:
        fre_label = "Easy / Conversational"
    elif fre >= 50:
        fre_label = "Moderate / Standard Academic"
    elif fre >= 30:
        fre_label = "Difficult / College Level"
    else:
        fre_label = "Very Difficult / Postgraduate Technical"

    if fkgl <= 8:
        fk_label = "Middle School"
    elif fkgl <= 12:
        fk_label = "High School"
    elif fkgl <= 16:
        fk_label = "Undergraduate"
    else:
        fk_label = "Graduate / Professional"

    return {
        "flesch_reading_ease": round(fre, 1),
        "flesch_kincaid_grade": round(fkgl, 1),
        "reading_ease_label": fre_label,
        "grade_level_label": fk_label,
        "syllables_per_word": round(syllables_per_word, 2),
    }


def calculate_structural_clarity_score(text: str) -> Dict[str, Any]:
    """Compute an algorithmic 0-100 Structural Clarity Score based on local

    heuristics:
    - Base score: 100
    - Passive voice penalties (>15% of sentences)
    - Run-on and clipped sentence penalties
    - Transition density assessment (ideal: 1.5 - 4.5 transitions / 100 words)
    - Sentence length variance reward (rewards varied cadence over monotony)
    - Paragraph structural balance (penalizes single massive blocks)
    """
    words = tokenize_words(text)
    sentences = tokenize_sentences(text)
    paragraphs = tokenize_paragraphs(text)

    if len(words) < 20 or len(sentences) == 0:
        return {
            "score": 0,
            "rating": "Insufficient Content",
            "deductions": ["Text is too short to evaluate structure reliably."],
            "strengths": [],
        }

    score = 100.0
    deductions: List[str] = []
    strengths: List[str] = []

    # 1. Passive voice check
    passive_data = detect_passive_voice(text)
    passive_pct = passive_data["passive_percentage"]
    if passive_pct > 30:
        penalty = min(20.0, (passive_pct - 30) * 0.8 + 10.0)
        score -= penalty
        deductions.append(f"Excessive passive voice ({passive_pct}% of sentences). Obscures agency and authorial responsibility.")
    elif passive_pct > 18:
        penalty = 6.0
        score -= penalty
        deductions.append(f"Elevated passive voice ({passive_pct}%). Consider converting key action verbs to active voice.")
    else:
        strengths.append(f"Well-controlled passive voice ({passive_pct}%), maintaining active, direct prose.")

    # 2. Transition density check
    trans_data = scan_transition_density(text)
    density = trans_data["density_per_100_words"]
    if density < 0.8:
        score -= 12.0
        deductions.append(f"Low transition density ({density} per 100 words). Paragraphs may feel disjointed without logical signposts.")
    elif density > 5.5:
        score -= 8.0
        deductions.append(f"Overused transition markers ({density} per 100 words), creating artificial signposting.")
    else:
        strengths.append(f"Optimal academic transition density ({density} markers per 100 words).")

    # 3. Sentence complexity & run-on check
    complexity = analyze_sentence_complexity(text)
    run_on_count = complexity["run_on_count"]
    choppy_count = complexity["choppy_count"]

    if run_on_count > 0:
        run_on_pct = (run_on_count / len(sentences)) * 100
        if run_on_pct > 20:
            score -= 15.0
            deductions.append(f"{run_on_count} excessive run-on sentences (>38 words), hindering reader comprehension.")
        else:
            score -= 6.0
            deductions.append(f"{run_on_count} long sentence(s) exceeding 38 words. Consider splitting clauses.")
    else:
        strengths.append("No exhausting run-on sentences detected; clauses remain manageable.")

    if choppy_count > len(sentences) * 0.25:
        score -= 8.0
        deductions.append(f"{choppy_count} very short sentences (<6 words), which may cause a fragmented reading rhythm.")

    # 4. Variance check (Rhythmic diversity)
    std_dev = complexity["std_dev"]
    if std_dev < 3.5 and len(sentences) > 4:
        score -= 6.0
        deductions.append("Low sentence length variance; phrasing risks sounding monotonous.")
    elif std_dev >= 5.0:
        strengths.append(f"Healthy sentence length standard deviation (σ={std_dev}), creating natural rhythmic cadence.")

    # 5. Paragraph structure
    if len(paragraphs) == 1 and len(words) > 180:
        score -= 10.0
        deductions.append("Single monolithic paragraph. Break arguments into distinct conceptual sections.")
    elif len(paragraphs) > 1:
        strengths.append(f"Divided into {len(paragraphs)} logical paragraph blocks.")

    final_score = int(max(10, min(100, round(score))))

    if final_score >= 85:
        rating = "Exceptional Structure"
    elif final_score >= 70:
        rating = "Proficient / Minor Issues"
    elif final_score >= 55:
        rating = "Moderate / Needs Revision"
    else:
        rating = "Substantial Structural Weakness"

    return {
        "score": final_score,
        "rating": rating,
        "deductions": deductions,
        "strengths": strengths,
    }


def run_full_local_heuristics(text: str) -> Dict[str, Any]:
    """Execute all local heuristic and deterministic evaluations in one call."""
    return {
        "passive_voice": detect_passive_voice(text),
        "transitions": scan_transition_density(text),
        "complexity": analyze_sentence_complexity(text),
        "readability": compute_readability_scores(text),
        "clarity": calculate_structural_clarity_score(text),
    }
