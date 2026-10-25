from __future__ import annotations

import json
import os
import sys

try:
    import streamlit as st
except ImportError:
    print(
        "Streamlit is not installed in this environment.\n"
        "To run this UI in a Python environment, run:\n"
        "  pip install streamlit\n"
        "  streamlit run app.py\n"
    )
    st = None

from ai_engine import run_gemini_audit
from heuristics import run_full_local_heuristics
from preprocessing import compute_text_statistics

SAMPLE_RESEARCH_PROPOSAL = """Quantum computing algorithms have been widely considered by researchers to be transformative for combinatorial optimization. However, existing quantum approximate optimization algorithms (QAOA) are frequently constrained by gate noise, barren plateaus, and environmental decoherence.

Therefore, this research proposal introduces a novel hybrid quantum-classical ansatz that adaptively mitigates stochastic gate drift through localized tensor contraction. The experimental architecture was rigorously evaluated across three synthetic benchmark graphs, and superior polynomial convergence was consistently observed compared to traditional unconstrained variational algorithms.

It is universally known that classical heuristics fail completely at scale. Consequently, our quantum formulation will without doubt become the definitive gold standard for NP-hard industrial scheduling problems once physical hardware scales beyond 1,000 qubits. Furthermore, because preliminary numerical simulations were performed with zero statistical errors, funding this five-year project will inevitably establish computational supremacy across modern cryptographic architectures."""

SAMPLE_MOTIVATION_LETTER = """I am writing to express my fervent enthusiasm for the Postdoctoral Fellowship in Computational Epistemology at the Institute for Advanced Studies. My doctoral research has been focused on developing formal verification tools for deep neural network decision boundaries.

During my dissertation, multiple algorithmic benchmarks were successfully developed and published in premier peer-reviewed venues. It is recognized by all leading scholars that modern large language models suffer from hallucinations and unprovable probabilistic leaps. My proposed research agenda will fundamentally solve this crisis by synthesizing modal logic with differential geometric bounds.

I am undoubtedly the most qualified candidate for this fellowship because my multidisciplinary background uniquely bridges category theory and applied statistical learning. Joining your laboratory will enable me to expand these theoretical breakthroughs, and significant publications will rapidly be produced under your mentorship."""


def run_streamlit_app() -> None:
    if st is None:
        return

    st.set_page_config(
        page_title="CriticalLogic-Validator",
        page_icon="⚖️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Fira+Code:wght@400;500&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        .main-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding-bottom: 1.25rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 1.5rem;
        }
        .header-title {
            font-size: 2.1rem;
            font-weight: 800;
            background: linear-gradient(135deg, #60a5fa 0%, #a855f7 50%, #ec4899 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
            letter-spacing: -0.025em;
        }
        .header-sub {
            color: #94a3b8;
            font-size: 0.95rem;
            margin-top: 0.25rem;
        }
        .engine-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: rgba(16, 185, 129, 0.12);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 9999px;
            padding: 0.35rem 0.85rem;
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 0.03em;
            text-transform: uppercase;
        }
        .pulse-dot {
            width: 8px;
            height: 8px;
            background-color: #10b981;
            border-radius: 50%;
            box-shadow: 0 0 8px #10b981;
        }
        .metric-card {
            background: rgba(30, 41, 59, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 0.75rem;
            padding: 1rem 1.25rem;
            margin-bottom: 0.75rem;
            backdrop-filter: blur(8px);
        }
        .metric-label {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #94a3b8;
            margin-bottom: 0.25rem;
        }
        .metric-value {
            font-size: 1.4rem;
            font-weight: 700;
            color: #f8fafc;
        }
        .passive-highlight {
            background-color: rgba(239, 68, 68, 0.18);
            border-left: 3px solid #ef4444;
            padding: 0.75rem 1rem;
            border-radius: 0.375rem;
            margin-bottom: 0.75rem;
            font-size: 0.92rem;
            line-height: 1.5;
        }
        .passive-tag {
            display: inline-block;
            background: #ef4444;
            color: white;
            font-size: 0.7rem;
            font-weight: 700;
            padding: 0.1rem 0.4rem;
            border-radius: 0.25rem;
            margin-right: 0.5rem;
        }
        .fallacy-box {
            background: rgba(245, 158, 11, 0.08);
            border: 1px solid rgba(245, 158, 11, 0.25);
            border-radius: 0.5rem;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="main-header">
            <div>
                <h1 class="header-title">⚖️ CriticalLogic-Validator</h1>
                <div class="header-sub">Automated Academic Paper, Research Proposal & Motivation Letter Audit Tool</div>
            </div>
            <div>
                <span class="engine-badge">
                    <span class="pulse-dot"></span>
                    Local Heuristic Engine Active
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_preset, col_clear = st.columns([4, 1])
    with col_preset:
        preset_choice = st.selectbox(
            "Load Sample Academic Document:",
            [
                "Research Proposal (Quantum Computing / Optimization)",
                "Motivation Letter (Postdoc Fellowship / Logic)",
                "Blank / Custom Document",
            ],
            index=0,
        )

    initial_text = ""
    if "Proposal" in preset_choice:
        initial_text = SAMPLE_RESEARCH_PROPOSAL
    elif "Motivation" in preset_choice:
        initial_text = SAMPLE_MOTIVATION_LETTER

    doc_input = st.text_area(
        "Document Text for Audit:",
        value=initial_text,
        height=260,
        placeholder="Paste your abstract, research proposal, thesis introduction, or motivation letter here...",
        help="Paste complete academic or scholarly paragraphs to evaluate argument rigor and local stylistic metrics.",
    )

    stats = compute_text_statistics(doc_input)
    heuristics = run_full_local_heuristics(doc_input)

    char_len = len(doc_input)
    st.caption(
        f"📊 Document Length: **{stats['word_count']} words** | **{char_len} characters** | "
        f"**{stats['sentence_count']} sentences** | **{stats['paragraph_count']} paragraphs**"
    )

    with st.sidebar:
        st.markdown("### 📈 Live Document Metrics")
        st.caption("Updated instantaneously via local Python regex heuristics")

        c1, c2 = st.columns(2)
        with c1:
            st.metric("Words", stats["word_count"])
        with c2:
            st.metric("Read Time", f"{stats['estimated_reading_time_minutes']} min")

        passive_data = heuristics["passive_voice"]
        passive_pct = passive_data["passive_percentage"]
        st.metric(
            "Passive Sentences",
            f"{passive_data['passive_sentence_count']} / {passive_data['total_sentences']}",
            delta=f"{passive_pct}% (Ideal: <15%)",
            delta_color="inverse" if passive_pct > 18 else "normal",
        )

        clarity_data = heuristics["clarity"]
        clarity_score = clarity_data["score"]
        st.metric(
            "Structural Clarity",
            f"{clarity_score} / 100",
            delta=clarity_data["rating"],
            delta_color="normal" if clarity_score >= 70 else "inverse",
        )

        readability = heuristics["readability"]
        st.metric(
            "Flesch Reading Ease",
            f"{readability['flesch_reading_ease']}",
            help="0-30: Very Difficult; 30-50: College; 50-70: Standard; 70-100: Conversational",
        )
        st.caption(f"Target: **{readability['reading_ease_label']}** (Grade: {readability['flesch_kincaid_grade']})")

        trans_data = heuristics["transitions"]
        st.metric(
            "Transition Density",
            f"{trans_data['density_per_100_words']} / 100w",
            delta=f"{trans_data['total_transitions']} total markers",
        )

        st.markdown("---")
        st.markdown("#### ⚙️ Heuristic Engine Configuration")
        st.info(
            "**Engine:** Python 3 Regex + Irregular Participle Matrix\n\n"
            "**Auxiliary Token Chain:** `is`, `was`, `were`, `been`, `be`, `are` + intervening adverbs\n\n"
            "**Core Pipeline:** Local Deterministic Analysis + Semantic Verification"
        )

    col_btn, col_info = st.columns([2, 5])
    with col_btn:
        audit_clicked = st.button("🚀 Run Full Document Audit", type="primary", use_container_width=True)
    with col_info:
        st.caption("Executes both deep local heuristic decomposition and semantic evaluation.")

    if "audit_results" not in st.session_state:
        st.session_state.audit_results = None

    if audit_clicked:
        if not doc_input.strip() or stats["word_count"] < 15:
            st.error("Please provide at least 15 words of text to perform an audit.")
        else:
            with st.spinner("Analyzing text with local heuristics and semantic engine..."):
                combined_heuristics = {
                    "stats": stats,
                    "passive_voice": heuristics["passive_voice"],
                    "transitions": heuristics["transitions"],
                    "complexity": heuristics["complexity"],
                    "readability": heuristics["readability"],
                    "clarity": heuristics["clarity"],
                }
                ai_result = run_gemini_audit(doc_input, combined_heuristics)
                st.session_state.audit_results = {
                    "heuristics": combined_heuristics,
                    "ai_result": ai_result,
                }

    if st.session_state.audit_results:
        results = st.session_state.audit_results
        h = results["heuristics"]
        ai_res = results["ai_result"]

        st.markdown("---")
        st.subheader("📋 Audit Report & Critical Diagnostic")

        tab1, tab2, tab3 = st.tabs([
            "📊 Tab 1: Structural & Stylistic Breakdown",
            "🔍 Tab 2: Logical Fallacies & Argument Strength",
            "💡 Tab 3: Actionable Revisions & Roadmap",
        ])

        with tab1:
            st.markdown("### 🧱 Structural & Stylistic Analytics")
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Clarity Score", f"{h['clarity']['score']}/100", h["clarity"]["rating"])
            with m2:
                st.metric("Passive Sentences", f"{h['passive_voice']['passive_percentage']}%", f"{h['passive_voice']['passive_sentence_count']} sentences")
            with m3:
                st.metric("Mean Sentence Length", f"{h['complexity']['mean_length']} words", f"σ = {h['complexity']['std_dev']}")
            with m4:
                st.metric("Grade Level", f"Grade {h['readability']['flesch_kincaid_grade']}", h["readability"]["reading_ease_label"])

            c_left, c_right = st.columns(2)
            with c_left:
                st.markdown("##### ⚠️ Algorithmic Deductions")
                if h["clarity"]["deductions"]:
                    for ded in h["clarity"]["deductions"]:
                        st.markdown(f"- 🔴 {ded}")
                else:
                    st.success("No structural penalties triggered.")

            with c_right:
                st.markdown("##### ✅ Algorithmic Strengths")
                if h["clarity"]["strengths"]:
                    for s in h["clarity"]["strengths"]:
                        st.markdown(f"- 🟢 {s}")
                else:
                    st.info("No notable structural strengths found.")

            st.markdown("---")
            st.markdown("#### 🎯 Flagged Passive Voice Sentences")
            flagged = h["passive_voice"]["flagged_sentences"]
            if not flagged:
                st.success("🎉 Excellent! No passive voice constructions flagged in this text.")
            else:
                st.caption(f"Found {len(flagged)} sentences with auxiliary-participle passive constructions:")
                for item in flagged:
                    st.markdown(
                        f"""
                        <div class="passive-highlight">
                            <span class="passive-tag">Sentence #{item['index']}</span>
                            {item['sentence']}<br>
                            <small style="color: #cbd5e1;"><b>Identified Passive Triggers:</b> {", ".join([m['phrase'] for m in item['matches']])}</small>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            st.markdown("---")
            st.markdown("#### 🔀 Academic Transition Markers")
            tc = h["transitions"]["category_counts"]
            t_col1, t_col2, t_col3, t_col4 = st.columns(4)
            t_col1.metric("Additive (furthermore...)", tc.get("additive", 0))
            t_col2.metric("Adversative (however...)", tc.get("adversative", 0))
            t_col3.metric("Causal (therefore...)", tc.get("causal", 0))
            t_col4.metric("Sequential (finally...)", tc.get("sequential", 0))

        with tab2:
            st.markdown("### 🧠 Semantic Evaluation & Argument Strength")
            if not ai_res.get("success"):
                st.error(f"Semantic Evaluation Error: {ai_res.get('error')}")
                st.info("Tip: Ensure your GEMINI_API_KEY is configured in your environment or Secrets.")
            else:
                st.markdown(ai_res["analysis_markdown"])

        with tab3:
            st.markdown("### 🎯 Strategic Revisions & Action Plan")
            if ai_res.get("success"):
                st.info("Review the action items and sentence transforms generated below:")
                st.markdown(ai_res["analysis_markdown"])
            else:
                st.warning("Actionable revisions require semantic analysis. Please run audit with a valid API key.")


if __name__ == "__main__":
    if st is not None:
        run_streamlit_app()
    else:
        print("Run with: streamlit run app.py")