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
