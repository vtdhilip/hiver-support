import os
import json
import time
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report
from agent import AmazonSupportAgent

def llm_as_judge(agent, customer_text, draft_reply, real_reply):
    """Simple 1-5 score from Gemini on reply quality."""
    prompt = f"""Rate the AI customer reply from 1 to 5 based on tone, helpfulness, and safety.
Customer: {customer_text}
Real Amazon Reply: {real_reply}
AI Reply: {draft_reply}

Return ONLY JSON: {{"score": 4, "reason": "Polite and helpful"}}"""

    try:
        response = agent.model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()
        return json.loads(text).get("score", 3)
    except:
        return 3

def run_evaluation():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    GOLDEN_PATH = os.path.join(BASE_DIR, '..', 'data', 'golden_set.csv')
    DATA_PATH = os.path.join(BASE_DIR, '..', 'data', 'processed', 'amazon_conversations.csv')

    df = pd.read_csv(GOLDEN_PATH)
    
    # Only evaluate rows that have been hand-labelled
    labeled = df[df['true_intent'].notna() & (df['true_intent'].astype(str).str.strip() != '')]
    if len(labeled) == 0:
        print("\nNo labels found in data/golden_set.csv yet!")
        print("Please open data/golden_set.csv and label a few rows (true_intent and true_escalate).")
        return

    print(f"Evaluating {len(labeled)} labelled examples...")
    agent = AmazonSupportAgent(DATA_PATH)
    
    true_intents, pred_intents = [], []
    true_escalates, pred_escalates = [], []
    scores = []

    for idx, (_, row) in enumerate(labeled.iterrows(), 1):
        query = str(row['customer_text'])
        print(f"[{idx}/{len(labeled)}] Testing: {query[:45]}...")
        
        try:
            result = agent.process_message(query)
            true_intents.append(str(row['true_intent']).strip())
            pred_intents.append(result.get("intent", "Unknown"))
            
            true_escalates.append(str(row['true_escalate']).strip().lower() == 'true')
            pred_escalates.append(bool(result.get("escalate", False)))
            
            score = llm_as_judge(agent, query, result.get("draft_reply", ""), str(row.get('amazon_reply', '')))
            scores.append(score)
            
            # Small delay to keep well within 15 RPM
            time.sleep(3)
        except Exception as e:
            print(f"  Error: {e}")

    # Results
    print("\n" + "="*40)
    print("🏆 EVALUATION SUMMARY 🏆")
    print("="*40)
    print(f"Intent Accuracy: {accuracy_score(true_intents, pred_intents) * 100:.1f}%")
    print("\nEscalation Performance:")
    print(classification_report(true_escalates, pred_escalates, target_names=['Auto-Handle', 'Escalate'], zero_division=0))
    if scores:
        print(f"Average Reply Score (LLM Judge): {sum(scores)/len(scores):.2f} / 5.0")

if __name__ == "__main__":
    run_evaluation()
