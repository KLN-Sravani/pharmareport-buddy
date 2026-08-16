# 🩺 GenAR AI Engineering Challenge: Regulatory Safety Reporting System (PADER)

<p align="center">
  <img src="https://img.shields.io/badge/Status-Prototype_v0-brightgreen?style=for-the-badge" alt="Status" />
  <img src="https://img.shields.io/badge/Architecture-Deterministic_%2B_LLM-blue?style=for-the-badge" alt="Architecture" />
  <img src="https://img.shields.io/badge/Target-PADER_Report-orange?style=for-the-badge" alt="Target Report" />
</p>

> **Core Philosophy:** **Strict Data Grounding.** An LLM should never perform arithmetic or statistical aggregations on raw clinical records. Deterministic Python engines calculate the figures; the LLM merely translates pre-verified evidence packets into clear, regulatory-compliant narrative summaries.

---

## 🚀 Quick Start (How to Run)

### **1. Prerequisites & Setup**
Ensure you have **Python 3.10+** installed.

```bash
# Clone the repository
git clone <your-repository-url>
cd firstname-lastname-genar-challenge

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
---

## 👤 Human Control & Review Workflow

The pipeline enforces a **Human-in-the-Loop Gate** before any report is finalized:

* **Interactive Review Interface:** Reviewers can inspect every generated section side-by-side with its supporting data.
* **Granular Section Decisions:** Each section can be individually **Approved** or **Flagged for rework** with reviewer comments attached.
* **Evidence Tracing & Verification:** Generated sentences include clickable evidence markers (e.g., `[E:reporting_period]`, `[E:total_cases]`) mapping directly to underlying verified Python aggregations under the **EVIDENCE USED BY THIS SECTION** panel.
* **State Persistence:** Reviewer actions are tracked in the frontend and synchronized back to the Python backend via the authoritative review script (`python -m safety_reporting.review`).

---

## ⚠️ Known Limitations

* **Single-Threaded Section Processing:** Version 0 processes sections sequentially. For multi-report batch processing at scale, an asynchronous worker queue (e.g., `asyncio` or Celery) should be implemented.
* **Static Schema Mapping:** Column mapping between raw CSV inputs and analytical aggregators is tailored to the Bisoprolol dataset structure; expanding to dynamic schemas requires a configurable schema mapping layer.
* **Browser-Local Session State:** In the prototype, pending review actions are held in browser memory before being committed to the persistent storage layer.
