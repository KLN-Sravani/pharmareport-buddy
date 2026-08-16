# 🏗️ System Architecture & Engineering Specifications

> **Safety Report AI (PADER Automation Pipeline)**  
> *A decoupled, deterministic-first framework for regulatory safety report generation.*

---

## 🎯 Architectural Philosophy & Core Principles

* **Evidence as a First-Class Object:** Analyses produce structured evidence items containing raw scalar values, calculation methodology metadata, and precise case-ID trace arrays. The same underlying object serves prompt context packets, rendered Markdown tables, evidence registers, and interactive UI drill-downs.
* **Declarative Dependency Decoupling:** Report sections declare their data requirements (`requires`) within configuration files (`pader.json`). Sections do not directly execute calculations or fetch raw datasets.
* **Narrow Model Boundaries:** Language Models operate strictly within a controlled translation layer (translating structured numeric packets into formal narrative prose). Deterministic validation layers flank both sides of the model call.
* **Data-Driven Report Types:** Creating alternative regulatory report formats (e.g., PSUR, DSUR, PBRER) requires declaring a new specification file rather than modifying underlying Python execution pipelines.
* **End-to-End Provenance:** Output bundles record comprehensive execution metadata, including source dataset SHA-256 hashes, specification versions, model parameters, pipeline timestamps, and Gateway run IDs.

---

## 🔄 Tiered Execution Lifecycle

The pipeline processes clinical data and produces regulatory outputs across six distinct layers:

### 1. Specification Declaration (`config/reports/pader.json`)
The system loads a JSON report specification that acts as the architectural blueprint. It defines global instructions, model parameters, section order, maximum word counts, required evidence dependencies (`requires`), and section-to-evidence rendering tables.

### 2. Ingestion, Validation & Deterministic Analysis (`dataset.py` & `analyses.py`)
* **Data Ingestion (`dataset.py`):** Ingests raw ICSR records (e.g., 1,068 rows), maps raw headers to a canonical schema, and executes data-quality validation rules.
* **Deterministic Computation (`analyses.py`):** Runs a registry of 15 hardcoded analytical routines to calculate deduplicated case counts, serious vs. non-serious ratios, reaction frequencies, and demographic distributions.
* **Output:** Generates a verified **Evidence Set** containing scalar values, calculation methods, and supporting case IDs.
* **Human Gate 1 (Analysis Review):** Provides a human review point to validate calculation logs and evidence registers before invoking LLM calls.

### 3. Context Packet Assembly (`packet.py`)
Parses the specification requirements for each section and extracts only the declared evidence IDs from the master Evidence Set. Assembles a scoped prompt packet combining global regulatory rules, reporting period metadata, isolated evidence values, and section-specific instructions.

### 4. Grounded Narrative Generation (`llm.py`)
Submits the scoped context packet to the Lovable AI Gateway (utilizing `gemini-3-flash` or target LLMs) via a streamed chat session. The model synthesizes the pre-calculated metrics into formal, regulatory-compliant Markdown text.

### 5. Automated Verification Engine (`verify.py`)
Every draft section undergoes programmatic verification prior to human presentation:
* **Numeric Audit:** Ensures every number present in the narrative exists within the source evidence payload (`numbers ⊆ evidence`).
* **Citation Integrity:** Validates inline evidence tags (e.g., `[E:id]`) against registered evidence IDs.
* **Rule Enforcement:** Detects and flags unauthorized clinical inferences or banned safety conclusions.
* **Auto-Flagging:** Generates audit findings and attaches status flags to invalid sections.

### 6. Human Approval & Final Rendering (`review.py` & `render.py`)
* **Human Gate 2 (Review Workspace):** Medical reviewers inspect draft narratives, evaluate verification findings, attach comments, and mark sections as **Approved** or **Flagged for Rework** (`review.py`).
* **Final Assembly (`render.py`):** Compiles approved narrative prose, rendered data tables, complete evidence registers, and provenance appendices into final output artifacts (`out/PADER_report.md`, `out/report_bundle.json`, and `out/case_index_full.csv`).
