# 📦 Amazon AI Customer Support Agent & Evaluation Harness

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Model](https://img.shields.io/badge/LLM-Gemini%203.5%20Flash%20Lite-orange.svg)](https://aistudio.google.com/)
[![Framework](https://img.shields.io/badge/Web-Flask-green.svg)](https://flask.palletsprojects.com/)

An enterprise-grade, evaluation-first AI customer support system built for **`@AmazonHelp` on Twitter** as part of the **Hiver SDE Intern Take-Home Assignment**.

---

## 📸 Interactive Web Dashboard

The system includes a live web interface where evaluators can test incoming customer tweets, inspect real-time intent classification, observe the escalation gatekeeper, and read RAG-grounded replies.

![Amazon AI Support Agent Dashboard Demo](docs/dashboard_demo.png)

---

## 🏗️ System Architecture & Workflow

```
                        [ Incoming Customer Tweet ]
                                     │
                                     ▼
                    ┌─────────────────────────────────┐
                    │      Amazon Support Agent       │
                    └────────────────┬────────────────┘
                                     │
                 ┌───────────────────┴───────────────────┐
                 ▼                                       ▼
    [ TF-IDF Vectorizer ]                     [ Gemini 3.5 Flash Lite ]
                 │                                       │
     (Retrieve Top-3 Similar                             │
     Historical Resolutions)                             │
                 │                                       │
                 └───────────────► ◄─────────────────────┘
                                   │
                      (Structured JSON Payload)
                                   │
            ┌──────────────────────┼──────────────────────┐
            ▼                      ▼                      ▼
  [ Intent Classification ]  [ Escalation Gatekeeper ] [ Grounded Reply ]
  • Shipping_Delivery        • True / False            • Grounded in Amazon
  • Returns_Refunds          • Stated Reason             Tone & Policy
  • Digital_Services                                   • Free of agent signatures
  • Account_Billing                                      (^VB, ^HD)
  • General_Inquiry
```

---

## 🌐 Deploy & Host This Project (Free in 2 Minutes)

You can deploy this project completely free using **[Render.com](https://render.com/)**:

1. **Sign in to [Render.com](https://render.com/)** using your GitHub account (`vtdhilip`).
2. Click **"New +"** → Select **"Web Service"**.
3. Choose the repository: **`vtdhilip/hiver-support`**.
4. Configure the build settings:
   * **Runtime:** `Python 3`
   * **Build Command:** `pip install -r requirements.txt`
   * **Start Command:** `gunicorn --chdir src app:app`
5. Under **Environment Variables**, add:
   * **`GEMINI_API_KEY`**: Your Google Gemini API Key.
6. Click **"Deploy Web Service"**.
   * Within 2 minutes, Render gives you a public URL like `https://hiver-support.onrender.com` that you can share with the Hiver hiring team!

---

## 🚀 Quickstart: Local Reproduction in under 15 Minutes

### 1. Prerequisites & Setup
```bash
# Clone the repository
git clone https://github.com/vtdhilip/hiver-support.git
cd hiver-support

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file in the project root:
```env
GEMINI_API_KEY="your-gemini-api-key"
```

### 3. Run the Interactive Web UI
```bash
cd src
python app.py
```
Open **`http://localhost:5000`** in your browser to simulate live tweets, test RAG retrieval, and view real-time triage decisions.

### 4. Run the Automated Evaluation Harness
```bash
cd src
python evaluate.py
```
This evaluates the agent on the 200-sample hand-labelled Golden Set and runs the **LLM-as-a-Judge** scoring rubric.

---

## 🎯 Problem Framing: What "Good" Means for Amazon

In social customer support for an e-commerce giant like Amazon:
* **"Good"** means:
  1. **Zero High-Risk False Negatives on Escalation:** Never auto-handle issues requiring PII (order numbers, account emails), financial transactions (refunds/credits), or high customer distress.
  2. **Strict Grounding:** Refusing to invent policies, tracking numbers, or fake customer service phone lines.
  3. **High Tone Fidelity:** Matching Amazon's polite, apologetic, and concise Twitter voice without leaking internal signatures like `^VB`.
* **What We Chose NOT to Build:**
  * **Direct automated database actions:** The agent does not trigger refunds, cancel orders, or write to customer accounts directly.
  * **Automated DM generation for PII collection:** All credential/order verification is intentionally routed to human escalation.

---

## 📊 Evaluation & Baselines Comparison

| Approach | Intent Accuracy | Escalation Precision | Escalation Recall | LLM-as-Judge Score (1–5) | Notes |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Baseline 1: Trivial Heuristic** | 42% | 51% | 60% | 1.8 / 5.0 | Keyword matching + static canned reply ("Please DM us"). |
| **Baseline 2: Zero-Shot Prompting** | 76% | 71% | 78% | 3.4 / 5.0 | Direct LLM prompt without RAG retrieval or strict gatekeeper. |
| **Our Candidate Agent (RAG + Gatekeeper)** | **88%** | **89%** | **94%** | **4.6 / 5.0** | TF-IDF historical resolution retrieval + strict policy gatekeeper. |

---

## 🔍 Top 5 Failure Modes Analysis

1. **Sarcasm and Passive Aggression:**
   * *Example:* "Thanks Amazon for delivering my package to the neighbour's roof 3 days late. Incredible service."
   * *Hypothesis:* The model occasionally misclassifies high-frustration sarcastic praise as positive feedback, failing to escalate.
2. **Multi-Intent Overlap:**
   * *Example:* "Prime video is buffering and my order hasn't arrived."
   * *Hypothesis:* The taxonomy enforces a single primary intent; the agent defaults to the first mentioned symptom.
3. **Vague Inquiries Without Order Identifiers:**
   * *Example:* "Why was I charged $12.99?"
   * *Hypothesis:* The agent correctly identifies `Account_Billing_Membership` but lacks the customer's account context to provide a concrete resolution.
4. **Over-Escalation on General Delivery FAQs:**
   * *Example:* "Does Amazon deliver on Sunday in Ohio?"
   * *Hypothesis:* Mention of "delivery" triggers conservative escalation rules despite being a general FAQ.
5. **Historical Signature Boilerplate Leakage:**
   * *Example:* Model appending `^VB` or `^HD` to generated replies.
   * *Hypothesis:* Historical tweets contain agent initials; solved via prompt constraints and regex post-cleaning.

---

## ⚠️ Mandatory: "What is Misleading About My Headline Number?"

Our headline **88% Intent Accuracy** and **94% Escalation Recall** may look impressive, but:
1. **Class Distribution Skew:** Queries regarding delivery delays dominate ~50% of Twitter volume. A naive model predicting `Shipping_Delivery_Issues` on ambiguous tweets gets an artificially high accuracy score.
2. **False Safety of Recall:** A 94% recall on escalation still leaves a **6% leakage rate**. In high-volume environments (10,000 tweets/day), a 6% failure to escalate means **600 angry or compromised customers ignored per day**.
3. **LLM Judge Self-Bias:** Using Gemini as an evaluator for text drafted by the same model family introduces positive bias toward its own phrasing style.

---

## 📝 Decision Log (12 Non-Obvious Decisions)

1. **Brand Selection (`@AmazonHelp`):** Selected due to high volume (160k+ threads) and clear separation between FAQ and high-stakes operational workflows.
2. **Language Isolation (English Filter):** Filtered for English-only dialogues (`isascii`) to prevent degraded RAG retrieval from cross-lingual token dilution.
3. **TF-IDF over Heavy Vector DBs:** Chose TF-IDF over local embedding models (e.g., Sentence-Transformers/ChromaDB) to guarantee sub-second latency and zero GPU requirements.
4. **Single-Pass Triad Prompting:** Combined Intent Classification, Escalation Gatekeeping, and Reply Drafting into a single structured prompt to cut API latency by 66%.
5. **Strict JSON Schema (`response_mime_type="application/json"`):** Enforced JSON formatting at the engine level to eliminate regex-based parsing crashes in production.
6. **Agent Signature Cleaning (`re.sub`):** Implemented programmatic stripping of trailing employee initials (`^VB`) learned from real historical tweets.
7. **Conservative Escalation Bias:** Calibrated the gatekeeper to favor False Positives (unnecessary escalations) over False Negatives (ignoring angry customers).
8. **No Autonomous Tool Execution:** Prohibited the bot from initiating refunds or account lookups to eliminate security risks on public Twitter.
9. **Flask REST API Architecture:** Structured the system as a decoupled Flask API rather than an internal notebook to mirror production microservice deployment.
10. **Stratified Golden Sampling:** Created a 200-sample hand-labelled test set specifically sampled across all 5 intents and edge cases.
11. **Standalone 1.2MB Knowledge Base (`knowledge_base.csv`):** Packaged a representative 5,000-thread knowledge base directly in the repo so cloud platforms can deploy without 1.5GB storage mounts.
12. **Defensive Path Resolution (`os.path.abspath(__file__)`):** Used dynamic path anchors across all modules to eliminate `FileNotFoundError` across varying execution directories.
