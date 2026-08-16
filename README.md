# 🩺 GenAR AI Engineering Challenge: Safety Report AI

> Build an AI System for Regulatory Safety Reporting (PADER)

**Core Philosophy: Strict Data Grounding**  
An LLM should never perform arithmetic or statistical aggregations on raw clinical records. Deterministic Python engines calculate all numbers, percentages, and group counts. The LLM's sole responsibility is translating pre-verified evidence packets into clear, regulatory-compliant narrative summaries.

---

## ⚡ Project Summary & Access Links

This project was developed using Lovable and Python to automate the generation of Periodic Adverse Drug Experience Reports (PADER).

* **Live Interactive Application:** https://pharmareport-buddy.lovable.app
* **Lovable Project Workspace:** https://lovable.dev/projects/71944b0e-8792-4c21-9339-127b9bacde1a

---

## 🚀 Quick Start & Local Development

To run this repository locally, ensure you have **Python 3.10+** and **Node.js** installed on your system.

### 1. Repository Setup & Dependencies
Execute the following commands in your terminal to set up the environment:

* `git clone <your-repository-url>`
* `cd <repository-name>`
* `npm install`
* `python -m venv venv`
* `source venv/bin/activate` (or `venv\Scripts\activate` on Windows)
* `pip install -r requirements.txt`

### 2. Environment Configuration
Export your API key to enable LLM-assisted section generation:
* `export OPENAI_API_KEY="your-api-key-here"`

### 3. Execution Command
To run the full end-to-end report generation pipeline from the command line:
* `python src/generate_report.py --data dataset/Bisoprolol_icsr_sample_1068rows.csv --output report_output.md`

---

## 🏗 Theoretical System Architecture & Data Flow

Rather than passing unorganized CSV data directly to an LLM, the system processes regulatory safety data through a **five-stage decoupled pipeline**:

### Stage 1: Data Ingestion & Deduplication
The raw dataset (`Bisoprolol_icsr_sample_1068rows.csv`) contains 1,068 rows of Individual Case Safety Reports (ICSRs). Individual patients often report multiple adverse reactions across separate rows under the same case ID. Python ingests the file and performs initial cleaning by deduplicating records on `safetyreportid`, establishing a precise baseline of 1,024 unique safety cases.

### Stage 2: Deterministic Analytics Engine
A pure Python module executes all arithmetic operations. It calculates case counts, calculates percentage distributions (e.g., serious vs. non-serious cases), groups demographics (age, sex, country), ranks adverse event frequencies (MedDRA Preferred Terms), and computes outcome metrics. Because this step uses deterministic code, mathematical accuracy is 100% reproducible and immune to model hallucination.

### Stage 3: Evidence Packet Assembly
The computed statistics are formatted into minimal, section-specific JSON structures called "Evidence Packets." Each report section (such as Narrative Summary or Demographics) receives only the exact metrics required for its specific writing task. This prevents context window bloat, reduces token cost, and isolates the LLM from seeing raw patient rows.

### Stage 4: Grounded LLM Narrative Generation
The evidence packets are injected into tailored system prompts for each section. The LLM is given strict negative constraints: it is instructed to act purely as a regulatory technical writer, synthesizing the provided JSON figures into formal prose without performing any math, inferring unbacked safety conclusions, or introducing external facts.

### Stage 5: Human Control & Review Gate
Before any generated report is finalized, output text flows into an interactive review interface. Medical reviewers can read the draft narrative, inspect the linked evidence tags backing each key figure, provide feedback notes, and explicitly choose to **Approve** or **Flag for Rework** each section.

---

## ⚖️ Division of Responsibilities: Deterministic Code vs. AI

* **Deterministic Python Engine:** Responsible for dataset parsing, ID deduplication, arithmetic, group aggregations, sorting, and percentage calculations. *Rationale:* LLMs struggle with precise counting and floating-point math across large datasets; hardcoded algorithms guarantee accuracy.
* **Evidence Assembler:** Responsible for key mapping, JSON payload scoping, and evidence hashing. *Rationale:* Eliminates noise and guarantees traceability between numbers in the narrative and source data.
* **Large Language Model (AI):** Responsible for translating structured numeric packets into cohesive, professional, regulatory-style narrative paragraphs. *Rationale:* LLMs excel at adapting structured data into consistent prose following specific tone guidelines.

---

## 📝 Prompt & Context Design Theory

Prompts are designed using a strict separation between permanent system persona guidelines and dynamically injected context packets.

### System Persona Template
"You are a Pharmacovigilance Regulatory Writer. Synthesize the provided pre-computed evidence packet into a formal PADER Narrative Summary. You MUST strictly adhere to the provided numbers. Do NOT calculate, estimate, or infer figures not present in the data payload. Maintain a neutral, factual regulatory tone."

### Dynamic Evidence Packet Example (Narrative Summary Section)
* Reporting Period: 2025-01-01 to 2025-12-31
* Total Unique Cases: 1,024
* Serious Cases: 1,023 (99.9%)
* Non-Serious Cases: 1 (0.1%)
* Top Reactions: Acute kidney injury (22 cases), Drug ineffective (12 cases), Cerebral haemorrhage (7 cases)
* Instructions: Summarize these exact figures into two short regulatory paragraphs.

---

## 🔒 Data Grounding & Traceability Mechanics

To guarantee that every sentence in the generated report is backed by facts:

1. **Zero Raw Data Exposure:** The LLM is never given direct access to raw CSV rows.
2. **Explicit Negative System Constraints:** System instructions explicitly forbid the model from calculating numbers or introducing external safety opinions.
3. **Traceable Evidence Tags:** Every generated metric is associated with an evidence tag (e.g., `[E:total_cases]`) linking directly to the underlying Python aggregation output.

---

## 👤 Human Control & Review Workflow

The pipeline enforces human oversight prior to finalizing any report output:

* **Interactive Review Interface:** Reviewers can inspect generated narrative sections side-by-side with supporting evidence metrics.
* **Granular Section Actions:** Each section can be individually **Approved** or **Flagged for Rework**, with reviewer comments recorded.
* **Evidence Verification:** Generated sentences feature inline evidence markers mapping directly to verified Python aggregations under the evidence display panel.
* **State Synchronization:** Approval decisions made in the frontend interface synchronize directly with the backend review tracking script (`python -m safety_reporting.review`).

---

## 📊 Scalability & Automated Evaluation Strategy

To evaluate quality across thousands of generated reports without manual reading:

* **Regex Numeric Auditing:** Parse the generated narrative text using regular expressions and cross-check every extracted number against the source JSON Evidence Packet. Any unlisted number flags an automatic hallucination error.
* **LLM-as-a-Judge Validation:** Run a secondary verification prompt asking an independent model to check if the generated text strictly agrees with the JSON payload.
* **Unit Testing:** Run automated test suites against the Python aggregation engine to verify edge-case handling (such as missing patient ages or null fields).

---

## ⚠️ Known Limitations

* **Sequential Execution:** The prototype processes report sections sequentially; multi-report batch processing at scale would require asynchronous worker queues (such as `asyncio` or Celery).
* **Dataset-Specific Column Mapping:** Column names are mapped specifically to the Bisoprolol dataset schema; generalizing across diverse dataset formats requires an abstract configuration mapping layer.
* **Session Persistence:** Pending reviewer approvals in the UI prototype are stored in browser memory prior to being committed to the permanent database layer.

---

## 🔮 Generalization & Future Expansion (PSUR, DSUR, PBRER)

To expand this prototype to handle other pharmaceutical report types (such as PSUR, PBRER, or DSUR) without rewriting core code, the system uses a **Configuration-Driven Architecture**:

* **Declarative Report Schemas:** Report structures are defined in JSON configurations declaring required sections and analysis dependencies.
* **Reusable Analysis Modules:** Python aggregation functions (such as serious case breakdowns) are decoupled from report types and serve multiple document templates.
* **Dynamic Prompt Injection:** Each report type imports its own tone rules and section prompts while sharing the underlying calculation engine.
