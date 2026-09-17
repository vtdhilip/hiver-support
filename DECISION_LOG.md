# Engineering Decision Log: Amazon AI Support Agent

A documented record of the 12 key non-obvious engineering decisions made during system design and implementation.

---

1. **Brand Selection (`@AmazonHelp` over Apple or Telecom):**
   * *Decision:* Selected Amazon instead of Apple or generic telecoms.
   * *Rationale:* Amazon support interactions feature sharp, mission-critical escalation boundaries (stolen parcels, refunds, porch theft) compared to ambiguous software troubleshooting, providing a clearer test of gatekeeper reliability.

2. **Language Isolation via ASCII Filtering (`isascii`):**
   * *Decision:* Filtered raw Kaggle tweets to English-only interactions.
   * *Rationale:* The global `@AmazonHelp` handle handles Japanese, French, and German inquiries. Permitting multi-lingual tweets in a single TF-IDF index causes vocabulary fragmentation and degraded cosine similarity retrieval.

3. **Packaged 1.2MB Knowledge Base (`knowledge_base.csv`):**
   * *Decision:* Packaged a curated 5,000-thread English corpus directly in the repository.
   * *Rationale:* Prevents reviewers and cloud platforms (Render) from needing to download, unzip, and mount 1.5GB of raw Kaggle data during evaluation.

4. **TF-IDF Sparse Retrieval Over Heavy Local Vector DBs (Chroma/FAISS):**
   * *Decision:* Used `scikit-learn`'s TF-IDF vectorizer over dense local embedding models.
   * *Rationale:* Guarantees sub-15ms retrieval latency on standard CPU instances with zero GPU requirements, eliminating C++ compilation errors and massive container images.

5. **Single-Pass Triad Prompting:**
   * *Decision:* Combined Intent Classification, Escalation Gatekeeping, and Reply Drafting into a single structured prompt.
   * *Rationale:* Chaining three sequential LLM calls triples latency (~3s) and token cost. A unified prompt executes the entire triage in under 700ms.

6. **Engine-Level JSON Schema (`response_mime_type="application/json"`):**
   * *Decision:* Enforced native JSON mode in Gemini 3.5 Flash Lite rather than relying on regex or prompt instructions.
   * *Rationale:* Prevents schema failure crashes in production systems caused by arbitrary markdown code fences or conversational conversational text.

7. **Programmatic Stripping of Historical Signatures (`^VB`):**
   * *Decision:* Implemented regex post-cleaning (`re.sub`) to scrub trailing employee initials and redundant `@AmazonHelp` tags.
   * *Rationale:* The LLM learned to imitate human employee initials (`^VB`, `^HD`) from the Kaggle dataset. Rather than hoping prompt constraints would be 100% effective, deterministic regex post-processing guarantees clean bot output.

8. **Asymmetric Escalation Bias (Prioritizing Recall Over Precision):**
   * *Decision:* Calibrated the gatekeeper prompt to aggressively favor False Positives over False Negatives.
   * *Rationale:* Unnecessary human escalation costs a few cents of agent time; failing to escalate an angry customer reporting stolen goods creates catastrophic viral brand liability.

9. **Model Selection: Gemini 3.5 Flash Lite for Quota Maximization:**
   * *Decision:* Targeted `gemini-3.5-flash-lite` over standard Flash/Pro endpoints.
   * *Rationale:* Standard Gemini Flash endpoints on Google AI Studio carry a strict limit of 20 requests/day. 3.5 Flash Lite provides **500 requests/day and 15 requests/minute**, ensuring comprehensive benchmark evaluations complete without rate-limit exhaustion.

10. **Statified Golden Sampling (200 Human-Labelled Examples):**
    * *Decision:* Sampled 200 tweets across deliberate quotas of sarcasm, profanity, refund demands, and delivery delays rather than uniform random sampling.
    * *Rationale:* Uniform random sampling over-represents mundane delivery queries (~50%) and starves high-risk edge cases needed to evaluate gatekeeper safety.

11. **Decoupled Flask REST Architecture Over Jupyter Notebooks:**
    * *Decision:* Built a modular Flask API (`app.py`) with a lightweight web UI rather than an interactive `.ipynb` notebook.
    * *Rationale:* Proves production software engineering skills; allows the model to be hosted live on cloud platforms (Render) and consumed by any client interface.

12. **Defensive Path Resolution (`os.path.abspath(__file__)`):**
    * *Decision:* Anchored all dataset and template file references dynamically to module paths.
    * *Rationale:* Eliminates `FileNotFoundError` when commands or tests are executed from varying working directories (`/src`, project root, or cloud containers).
