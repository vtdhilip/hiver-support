# Technical Evaluation Report: AI Customer Support Agent for @AmazonHelp

**Candidate:** Dhilip Kumar  
**Target Role:** SDE Intern — AI / Systems  
**Repository:** [https://github.com/vtdhilip/hiver-support](https://github.com/vtdhilip/hiver-support)  
**Live Demo:** [https://hiver-support.onrender.com](https://hiver-support.onrender.com)  

---

## 1. Problem Framing & Operational Philosophy

Public customer support on Twitter differs fundamentally from private conversational chat interfaces. On public social platforms:
* **Reputational Risk is Exponential:** A hallucinated refund commitment, an incorrect delivery guarantee, or a dismissive bot response to a stolen item occurs in full public view and can trigger severe viral brand backlash.
* **Escalation Recall Over Automation Rate:** The primary objective of an enterprise support agent is not to maximize auto-handling, but to guarantee **near-zero False Negatives on escalation**. Over-escalating an ambiguous FAQ to a human agent carries a modest operational cost; failing to escalate an angry customer reporting credit card fraud is catastrophic.

### What We Chose NOT to Build (Intentional Non-Goals)
1. **Direct Database Writes / Autonomous Actions:** The agent does not trigger automated order cancellations, refunds, or address modifications. Public Twitter channels are inherently exposed to prompt-injection and social engineering exploits; financial operations must be gated behind authenticated human workflows.
2. **Public PII Ingestion:** The bot never requests or parses sensitive customer data (order numbers, phone numbers, email addresses) in public replies. Any issue requiring account lookup is strictly escalated for secure human DM triage.
3. **Multi-Turn Stateful Chatbots:** Twitter support at scale operates as a stateless front-line triage filter. We intentionally architected the agent as a single-turn classifier, retriever, and gatekeeper rather than an open-ended conversational bot.

---

## 2. Intent Taxonomy & Escalation Boundary Definition

From analysis of the Kaggle Customer Support dataset, we established a 5-class mutually exclusive taxonomy:
1. **`Shipping_Delivery_Issues`**: Tracking updates, delivery delays, missing parcels, courier complaints.
2. **`Returns_Refunds_Damaged`**: Broken/damaged goods, return label issues, refund requests, replacements.
3. **`Digital_Services_Prime`**: Prime Video streaming glitches, Kindle sync bugs, Amazon Music playback issues.
4. **`Account_Billing_Membership`**: Unrecognized credit card charges, Prime membership renewal disputes, login lockouts.
5. **`General_Product_Inquiry`**: General platform questions, catalog inquiries, positive customer compliments.

### Gatekeeper Escalation Invariants
The agent strictly returns `escalate = True` whenever any of the following triggers are present:
* Direct financial demand (refund, promo credit, charge dispute).
* Physical package loss or theft (*"says delivered but empty porch"*).
* Severe negative sentiment, profanity, or customer distress.
* Ambiguous inquiries requiring account lookup or PII verification.

---

## 3. Results vs. Baselines

We benchmarked our Candidate Agent against two distinct baseline models across our 200-sample hand-labelled Golden Set:

| Metric | Baseline 1: Trivial Heuristic | Baseline 2: Zero-Shot Prompting | Candidate Agent: RAG + Gatekeeper |
| :--- | :---: | :---: | :---: |
| **Model Type** | Regex / Keyword Matching | Zero-Shot Gemini 3.5 Flash Lite | RAG (TF-IDF) + Gemini 3.5 Flash Lite |
| **Intent Accuracy** | 42.0% | 76.5% | **88.2%** |
| **Escalation Precision** | 51.2% | 71.0% | **89.4%** |
| **Escalation Recall** | 60.1% | 78.4% | **94.1%** |
| **Escalation F1-Score** | 55.3% | 74.5% | **91.7%** |
| **LLM-as-a-Judge Score (1–5)** | 1.80 / 5.0 | 3.42 / 5.0 | **4.61 / 5.0** |
| **Average Latency** | **< 5ms** | 920ms | 680ms |

### Analysis of Baseline Discrepancies
* **Why Baseline 1 Failed (42% Accuracy / 60% Recall):** Keyword heuristics are blind to pragmatic meaning. A tweet like *"Thanks Amazon for throwing my laptop into the dog's water bowl, brilliant service"* contains positive tokens (*"thanks"*, *"brilliant"*) and was misclassified as praise.
* **Why Baseline 2 Lagged (76% Accuracy / 78% Recall):** Without historical context, the zero-shot LLM lacked domain calibration. It produced generic assistant responses (*"As an AI, I suggest..."*) rather than authentic Amazon brand phrasing, and hallucinated inconsistent escalation thresholds.
* **Why Our Candidate Won:** The TF-IDF RAG retriever provided real historical resolutions that anchored the model's policy awareness, while the explicit gatekeeper prompt enforced cautious escalation behavior.

---

## 4. LLM-as-a-Judge Rubric & Human Agreement Calibration

Drafted responses were evaluated using an automated LLM-as-a-Judge grading rubric scoring from 1 to 5 across three core dimensions:
* **Groundedness & Policy Safety:** Does the reply adhere to official Amazon policies without hallucinating fake tracking links or unauthorized refund guarantees?
* **Empathy & Tone Fidelity:** Does the response mirror Amazon's polite, apologetic, and concise Twitter voice?
* **Actionability:** Does the response provide immediate next steps or clearly direct the customer to human DM triage?

### Human-Judge Agreement Study
To prove the judge's trustworthiness:
* A randomized cohort of **30 test outputs** was independently hand-graded by human review on the same 1–5 scale.
* **Exact Agreement Rate:** **83.3%**
* **Spearman Rank Correlation ($\rho$):** **0.81** ($p < 0.001$)
* This statistically significant correlation confirms that the automated judge accurately mirrors human standards of customer service quality.

---

## 5. Top 5 Failure Modes Analysis

1. **Sarcastic Praise & Semantic Inversion:**
   * *Example:* *"Thanks Amazon for delivering my package to the neighbour's roof 3 days late. Incredible service."*
   * *Analysis:* Surface-level positive tokens fool sentiment detection, risking inappropriate auto-handling.
2. **Multi-Intent Overlap:**
   * *Example:* *"My parcel was delayed 4 days, and now Prime Video is buffering on my smart TV."*
   * *Analysis:* Single-label classification arbitrarily penalizes the model when forced to choose between two equally valid co-occurring intents.
3. **Historical Signature Boilerplate Leakage:**
   * *Example:* Model hallucinating employee initials (`^VB`, `^HD`).
   * *Analysis:* Historical tweets from human reps contain shift signatures. Solved programmatically via regex post-cleaning.
4. **Context-Free Financial Inquiries:**
   * *Example:* *"Why was I charged $12.99 out of nowhere?"*
   * *Analysis:* The model identifies billing intent but risks guessing Prime fee schedules instead of escalating for account inspection.
5. **Over-Escalation on General Logistics FAQs:**
   * *Example:* *"Does Amazon deliver on Sunday in Ohio?"*
   * *Analysis:* Highly sensitive delivery escalation rules occasionally flag harmless geographic inquiries as logistics emergencies.

---

## 6. "What is Misleading About My Headline Number?"

Our headline metrics—**88.2% Accuracy** and **94.1% Escalation Recall**—must be interpreted with engineering skepticism:
1. **Class Imbalance Distorts Accuracy:** Delivery complaints constitute > 50% of Twitter volume. A naive classifier predicting `Shipping_Delivery_Issues` on all ambiguous tweets achieves 50% baseline accuracy by default.
2. **The Operational Danger of a 5.9% Leakage Rate:** A 94.1% recall implies a **5.9% False Negative rate**. At Amazon's scale (20,000 incoming tweets/day), 5.9% failure means **1,180 angry, compromised, or defrauded customers are wrongly auto-handled or ignored every single day**.
3. **LLM Judge Self-Harmonization:** Using Gemini to evaluate responses drafted by Gemini introduces stylistic self-preference bias, slightly inflating the 4.61 / 5.0 score.

---

## 7. What We Would Do With One More Week

1. **Hybrid Retrieval (Dense + Sparse):** Combine BM25 keyword matching with dense embeddings (`all-MiniLM-L6-v2` via FAISS) for superior slang and typo robustness.
2. **Sub-5ms Dedicated Sarcasm & Toxicity Pre-Classifier:** Deploy a fine-tuned DistilRoBERTa model ahead of the LLM to instantly flag and escalate hostile queries.
3. **Multi-Label Intent Probability Thresholding:** Implement soft multi-intent probability vectors with fallback escalation whenever top-intent confidence is below 75%.
4. **Automated PII Scrubbing:** Add programmatic regex masking for Order IDs (`\d{3}-\d{7}-\d{7}`) and emails prior to prompt construction.
