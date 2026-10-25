from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

CRITICAL_LOGIC_PROMPT_TEMPLATE = """You are an elite academic peer reviewer, logic professor, and grant committee chairperson.
You have been provided with an academic paper, research proposal, or motivation letter for an in-depth critical audit.

Prior to your review, a deterministic local heuristic engine evaluated the document:
--- LOCAL DETERMINISTIC METRICS ---
- Word Count: 
{word_count}
- Sentence Count: 
{sentence_count}
- Paragraph Count: 
{paragraph_count}
- Passive Voice Sentences: 
{passive_sentence_count} ({passive_percentage}% of sentences)
- Academic Transition Density: 
{transition_density} markers per 100 words (Total: {total_transitions})
- Sentence Length Std Dev (Variance): 
{sentence_std_dev} (Mean length: {sentence_mean_length} words)
- Flesch Reading Ease: 
{reading_ease} ({reading_ease_label})
- Flesch-Kincaid Grade Level: 
{grade_level} ({grade_level_label})
- Structural Clarity Score: 
{clarity_score}/100 ({clarity_rating})
- Local Deductions: 
{clarity_deductions}
-----------------------------------

--- DOCUMENT FOR AUDIT ---
{document_text}
--------------------------

Conduct a deep, rigorous logical and rhetorical critique. You must output your evaluation strictly formatted into the following three distinct sections:

# SECTION 1: LOGICAL FALLACIES & UNBACKED CLAIMS
Analyze every paragraph for formal and informal reasoning flaws.
For each issue found (or state "None identified" if exceptionally sound), provide:
- **Flaw Category:** (e.g., Non Sequitur, Hasty Generalization, Begging the Question, Appeal to Unqualified Authority, False Dilemma, Circular Reasoning, Weak Analogy, Unsupported Assertion).
- **Exact Quote / Excerpt:** The specific phrase or sentence.
- **Why It Fails:** Rigorous philosophical and methodological explanation of why this inference is invalid or unsubstantiated.
- **Rigor Remedy:** How the author can ground this claim empirically, provide caveats, or reconstruct the syllogism.

# SECTION 2: ARGUMENT STRENGTH ASSESSMENT (1-10 SCALE)
Provide an overall quantitative rating from 1 to 10 with clear categorical criteria:
- **Overall Argument Score:** [X/10] (where 1 = Unsubstantiated Opinion, 5 = Plausible but Vulnerable, 8 = Strong Academic Rigor, 10 = Airtight Publication-Ready Dialectic).
- **Sub-dimension Scores (1-10):**
  * Premise Soundness: [X/10]
  * Evidence & Warrant Grounding: [X/10]
  * Rhetorical & Inferential Coherence: [X/10]
  * Fallacy Absence: [X/10]
- **Core Syllogism Analysis:** Identify the explicit or implicit Major Premise, Minor Premise, and Conclusion of the document. Point out the weakest link in this chain.
- **Academic Authority & Voice:** Evaluate whether the tone projects authoritative scholarly objectivity or slips into hyperbolic, speculative marketing prose.

# SECTION 3: STRATEGIC ESSAY & PROPOSAL REVISION PLAN
Provide a ranked, high-impact revision roadmap:
1. **Critical Priority (Immediate Fixes):** Flaws that would cause outright desk-rejection or grant denial.
2. **Structural & Flow Refinement:** Reorganization of paragraphs or topic sentences to enhance dialectical flow.
3. **Passive-to-Active & Precision Rewrites:** 2-3 specific before/after sentence rewrites transforming weak passive constructions or vague claims into crisp, active academic prose.
4. **Actionable Checklist for Submission:** 4-5 bulleted concrete checks prior to final submission.
"""


def build_audit_prompt(document_text: str, heuristics_data: Dict[str, Any]) -> str:
    stats = heuristics_data.get("stats", {})
    passive = heuristics_data.get("passive_voice", {})
    trans = heuristics_data.get("transitions", {})
    complexity = heuristics_data.get("complexity", {})
    readability = heuristics_data.get("readability", {})
    clarity = heuristics_data.get("clarity", {})

    deductions_list = clarity.get("deductions", [])
    deductions_str = "; ".join(deductions_list) if deductions_list else "None detected"

    return CRITICAL_LOGIC_PROMPT_TEMPLATE.format(
        word_count=stats.get("word_count", 0),
        sentence_count=stats.get("sentence_count", 0),
        paragraph_count=stats.get("paragraph_count", 0),
        passive_sentence_count=passive.get("passive_sentence_count", 0),
        passive_percentage=passive.get("passive_percentage", 0.0),
        transition_density=trans.get("density_per_100_words", 0.0),
        total_transitions=trans.get("total_transitions", 0),
        sentence_std_dev=complexity.get("std_dev", 0.0),
        sentence_mean_length=complexity.get("mean_length", 0.0),
        reading_ease=readability.get("flesch_reading_ease", 0.0),
        reading_ease_label=readability.get("reading_ease_label", "N/A"),
        grade_level=readability.get("flesch_kincaid_grade", 0.0),
        grade_level_label=readability.get("grade_level_label", "N/A"),
        clarity_score=clarity.get("score", 0),
        clarity_rating=clarity.get("rating", "N/A"),
        clarity_deductions=deductions_str,
        document_text=document_text.strip(),
    )


def run_gemini_audit(
    document_text: str,
    heuristics_data: Dict[str, Any],
    api_key: Optional[str] = None,
    model_name: str = "gemini-2.5-flash",
) -> Dict[str, Any]:
    key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("API_KEY")
    if not key:
        return {
            "success": False,
            "error": "Missing GEMINI_API_KEY environment variable.",
            "raw_response": None,
        }

    prompt = build_audit_prompt(document_text, heuristics_data)

    try:
        from google import genai
        client = genai.Client(api_key=key, http_options={"headers": {"User-Agent": "CriticalLogic-Validator/1.0"}})
        response = client.models.generateContent(
            model=model_name,
            contents=prompt,
        )
        return {
            "success": True,
            "analysis_markdown": response.text,
            "model_used": model_name,
            "provider": "google.genai SDK",
        }
    except ImportError:
        pass
    except Exception as e:
        return {
            "success": False,
            "error": f"GenAI SDK execution error: {str(e)}",
            "raw_response": None,
        }

    try:
        import urllib.error
        import urllib.request

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "topP": 0.95,
            },
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "CriticalLogic-Validator/1.0",
            },
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=45) as response:
            result = json.loads(response.read().decode("utf-8"))
            candidates = result.get("candidates", [])
            if candidates:
                content_parts = candidates[0].get("content", {}).get("parts", [])
                text_result = "".join(part.get("text", "") for part in content_parts)
                return {
                    "success": True,
                    "analysis_markdown": text_result,
                    "model_used": model_name,
                    "provider": "urllib REST API",
                }
            return {
                "success": False,
                "error": "No candidate responses returned by the API.",
                "raw_response": result,
            }
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="ignore")
        return {
            "success": False,
            "error": f"API HTTP Error {e.code}: {err_msg}",
            "raw_response": None,
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Network or execution error: {str(e)}",
            "raw_response": None,
        }