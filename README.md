# CriticalLogic-Validator

An automated academic text analytics, syntactic auditing, and rhetorical validation suite designed for research proposals, scientific manuscripts, conference submissions, and institutional motivation statements.

The system combines deterministic rule-based algorithms, regular-expression tokenizers, and advanced semantic validation to evaluate structural clarity, syntactic agency, argument coherence, and dialectical soundness.

---

## Architecture Overview

CriticalLogic-Validator is structured into modular layers:

```
CriticalLogic-Validator/
├── preprocessing.py     # Deterministic text normalization, tokenization & statistical profiling
├── heuristics.py        # Rule-based syntactic scoring, passive voice detection & readability indices
├── ai_engine.py         # Semantic argument evaluation and fallacy identification engine
├── app.py               # Streamlit web interface with real-time reactive metrics
├── run_audit.py         # Command-line interface and inter-process communication runner
├── requirements.txt     # Python runtime package dependencies
└── README.md            # Technical documentation and functional specification
```

---

## Detailed Functional Reference

### 1. `preprocessing.py`
Provides deterministic text parsing, normalization, and statistical extraction without external natural language processing overhead.

- **`clean_and_normalize_text(text: str) -> str`**
  Standardizes typographic symbols (smart quotes, em-dashes, en-dashes, ellipses), strips non-printable ASCII control characters, harmonizes line-endings to standard Unix delimiters, and collapses redundant whitespace while preserving paragraph boundaries.

- **`tokenize_paragraphs(text: str) -> List[str]`**
  Segments text into distinct paragraph units using contiguous newline boundaries, discarding empty or whitespace-only sections.

- **`tokenize_sentences(text: str) -> List[str]`**
  Decomposes prose into grammatical sentences using custom regular-expression lookarounds. Protects academic abbreviations (`e.g.`, `i.e.`, `et al.`, `cf.`, `Dr.`, `Prof.`, `Fig.`, `vs.`, `eq.`), numerical decimals, and trailing punctuation delimiters.

- **`tokenize_words(text_segment: str) -> List[str]`**
  Extracts alphanumeric word tokens from arbitrary sentence spans, stripping outer punctuation marks while preserving internal hyphenated compounds (e.g., `peer-reviewed`).

- **`compute_text_statistics(text: str) -> Dict[str, Any]`**
  Computes core descriptive metrics:
  - Total character count (inclusive and exclusive of whitespace)
  - Total word, sentence, and paragraph counts
  - Mean sentence length (words per sentence)
  - Mean word length (characters per word)
  - Lexical density (Type-Token Ratio / percentage of unique word forms)
  - Individual sentence length arrays
  - Estimated reading duration (based on 200 words per minute)

---

### 2. `heuristics.py`
Implements deterministic scoring functions, syntactic patterns, readability calculations, and the composite Structural Clarity Score.

- **`count_syllables_word(word: str) -> int`**
  Algorithmic syllable estimator utilizing vowel-run heuristics, terminal silent-e stripping, and consonant-le rules to support readability formulas.

- **`detect_passive_voice(text: str) -> Dict[str, Any]`**
  Syntactic pattern matcher scanning for auxiliary verb constructions (`is`, `was`, `were`, `been`, `be`, `are`, `am`, `being`, `get`, `got`) coupled with regular (`-ed`) or irregular past participles across intervening adverbial chains. Returns match occurrences, percentage of passive sentences, and flagged sentence indices.

- **`scan_transition_density(text: str) -> Dict[str, Any]`**
  Scans text against categorized academic signposts:
  - *Additive*: `furthermore`, `moreover`, `in addition`, `additionally`, `likewise`
  - *Adversative*: `however`, `nevertheless`, `conversely`, `in contrast`, `despite this`
  - *Causal*: `therefore`, `consequently`, `thus`, `hence`, `as a result`
  - *Sequential*: `firstly`, `secondly`, `subsequently`, `finally`, `in summary`
  Outputs category breakdowns, total transition occurrences, and density per 100 words.

- **`analyze_sentence_complexity(text: str) -> Dict[str, Any]`**
  Calculates length distribution metrics across sentences, computing variance and standard deviation ($\sigma$) to measure rhythmic cadence. Identifies run-on sentences (>38 words) and overly brief fragments (<6 words).

- **`compute_readability_scores(text: str) -> Dict[str, Any]`**
  Calculates standardized readability benchmarks:
  - **Flesch Reading Ease (FRE):** $206.835 - 1.015 \left(\frac{\text{words}}{\text{sentences}}\right) - 84.6 \left(\frac{\text{syllables}}{\text{words}}\right)$
  - **Flesch-Kincaid Grade Level (FKGL):** $0.39 \left(\frac{\text{words}}{\text{sentences}}\right) + 11.8 \left(\frac{\text{syllables}}{\text{words}}\right) - 15.59$
  Assigns qualitative reading and education-level classifications.

- **`calculate_structural_clarity_score(text: str) -> Dict[str, Any]`**
  Produces an algorithmic composite score (0–100 scale) evaluating:
  - Frequency of passive constructions (penalties for >18% and >30%)
  - Transition signpost density (optimal window: 1.5–4.5 per 100 words)
  - Incidence of clause-heavy run-on sentences
  - Sentence length standard deviation (rewarding cadence variation)
  - Paragraph structural distribution
  Outputs an integer score, qualitative rating, identified deductions, and confirmed strengths.

- **`run_full_local_heuristics(text: str) -> Dict[str, Any]`**
  Orchestrates all heuristic evaluations in a single unified execution pipeline.

---

### 3. `ai_engine.py`
Provides deep semantic validation, rhetorical fallacy detection, and actionable dialectical critiques.

- **`build_audit_prompt(document_text: str, heuristics_data: Dict[str, Any]) -> str`**
  Constructs a structured prompt template integrating the target document with all deterministic local metrics (word counts, passive ratios, transition rates, readability indices, and clarity deductions) to anchor semantic evaluation in quantitative findings.

- **`run_gemini_audit(document_text: str, heuristics_data: Dict[str, Any], api_key: Optional[str] = None, model_name: str = "gemini-3.8-flash") -> Dict[str, Any]`**
  Executes the semantic audit using the official SDK interface with an automated standard-library HTTP fallback. Generates structured output across three sections:
  1. *Logical Fallacies & Unbacked Claims*: Identifies non sequiturs, hasty generalizations, circularity, and unwarranted assertions with specific citations and remedy recommendations.
  2. *Argument Strength Assessment*: Delivers quantitative scores (1–10 scale) for premise soundness, evidence grounding, inferential coherence, and fallacy absence, followed by syllogism analysis.
  3. *Strategic Revision Roadmap*: Delivers prioritized intervention steps, active sentence rewrites, and an academic submission checklist.

---

### 4. `app.py`
Interactive web graphical user interface built with Streamlit.

- **`run_streamlit_app() -> None`**
  Launches the interactive dashboard featuring:
  - Live sidebar displaying deterministic metrics calculated instantaneously upon text entry
  - Preloaded academic document templates (Research Proposal, Postdoctoral Fellowship Letter, Empirical Manuscript)
  - Tab 1: Structural & Stylistic Breakdown with highlighted passive phrases, transition distributions, and cadence charts
  - Tab 2: Logical Fallacies & Argument Strength grading cards and syllogistic evaluations
  - Tab 3: Actionable Revisions, active transformation samples, and a pre-submission checklist


## Installation & Environment Setup

1. **Clone or download the repository:**
   ```bash
   git clone <repository_url>
   cd CriticalLogic-Validator
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Key (Optional for semantic evaluation):**
   ```bash
   export GEMINI_API_KEY="your-api-key"
   ```

---

## Usage

### Command-Line Execution
Run deterministic heuristics directly in the terminal:
```bash
python3 run_audit.py --text "Quantum algorithms have been widely evaluated. Therefore, we present a novel hybrid framework."
```

Or pipe text via stdin:
```bash
cat draft_proposal.txt | python3 run_audit.py --json
```

### Web Application Execution
Launch the interactive browser dashboard:
```bash
streamlit run app.py
```

---

## Quality & Coding Standards
- **PEP 8 Compliance:** All Python modules adhere to standard formatting and naming conventions.
- **Explicit Typing:** Function signatures feature comprehensive type annotations (`typing.List`, `typing.Dict`, `typing.Optional`, `typing.Any`).
- **Zero Heavy NLP Footprint:** Local parsing relies entirely on standard library modules (`re`, `math`, `json`, `sys`, `argparse`).
