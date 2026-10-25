# CriticalLogic-Validator

> A production-grade textual audit and heuristic verification engine designed to evaluate academic papers, research proposals, and technical writing for structural clarity and syntactic consistency.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-GUI-red)
![Architecture](https://img.shields.io/badge/Architecture-Modular-green)
![License](https://img.shields.io/badge/License-MIT-orange)

---

## 📌 Overview

**CriticalLogic-Validator** is a dual-layer document analysis application built to bridge syntactic text processing with deep logical reasoning. Unlike standard wrapper utilities, the core engine executes **deterministic local preprocessing and custom regex heuristics** to evaluate document structure before any external semantic evaluation takes place.

The system is architected around clean code principles, ensuring high performance, modular separation of concerns, and rigorous error handling.

---

## 🛠️ Core Architecture & Modules

### 1. Preprocessing Engine (`preprocessing.py`)
* Implements custom regular expression parsers (`re`) to handle text normalization, whitespace cleansing, and sentence boundary tokenization without relying on heavy external NLP libraries.
* Computes real-time lexical statistics including character density, word frequencies, and average sentence length.

### 2. Heuristic Analysis Suite (`heuristics.py`)
* **Passive Voice Detector:** Scans text using custom auxiliary verb matching (`is`, `was`, `were`, `been`, `be`, `are`, `am`) combined with past participle patterns to isolate passive constructions and return exact line indices.
* **Transition Density Analyzer:** Evaluates academic flow by mapping logical connectors (e.g., *furthermore*, *consequently*, *therefore*).
* **Structural Clarity Scorer:** Generates a deterministic baseline score (0–100) based on variance in sentence length and paragraph density distributions.

### 3. Semantic Verification Pipeline (`ai_engine.py`)
* Integrates structured prompt templates to analyze logical consistency, argument strength, and fallacy patterns, utilizing local heuristic metadata for contextual depth.

### 4. Interactive Graphical User Interface (`app.py`)
* Built with Streamlit to deliver a responsive, clean SaaS-like dashboard featuring live sidebar metrics, custom CSS card styling, and tabbed analytical views.

---

## ⚙️ Tech Stack

* **Core Language:** Python 3.8+
* **GUI Framework:** Streamlit
* **Pattern Matching:** Python Standard Library (`re`, `math`, `collections`)
* **Data Integration:** Google GenAI SDK / urllib REST Fallback

---

## 🚀 Getting Started Locally

### Prerequisites
Ensure Python is installed on your system.

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/eshatahir279/CriticalLogic-Validator.git](https://github.com/eshatahir279/CriticalLogic-Validator.git)
   cd CriticalLogic-Validator
