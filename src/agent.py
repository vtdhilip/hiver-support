import os
import re
import json
import pandas as pd
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as genai

# Automatically loads variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

class AmazonSupportAgent:
    def __init__(self, data_path):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file! Please add it to your .env file.")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-3.5-flash-lite",
            generation_config={"response_mime_type": "application/json"}
        )
        
        print("Indexing historical support data...")
        df = pd.read_csv(data_path).dropna()
        df_english = df[df['customer_text'].map(lambda x: str(x).isascii())]
        self.kb = df_english.sample(min(5000, len(df_english)), random_state=42).reset_index(drop=True)
        
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = self.vectorizer.fit_transform(self.kb['customer_text'])
        print("Agent ready!")

    def retrieve_context(self, query, top_k=3):
        """Finds 3 most similar past customer issues using TF-IDF cosine similarity."""
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        top_indices = scores.argsort()[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            results.append({
                "past_issue": self.kb.iloc[idx]['customer_text'],
                "past_reply": self.kb.iloc[idx]['amazon_reply']
            })
        return results

    def process_message(self, customer_query):
        """Classifies intent, decides escalation, and drafts a reply."""
        context = self.retrieve_context(customer_query)
        
        prompt = f"""You are an AI customer support agent for @AmazonHelp.
Analyze the customer tweet and return ONLY a JSON object with:
1. "intent": One of [Shipping_Delivery_Issues, Returns_Refunds_Damaged, Digital_Services_Prime, Account_Billing_Membership, General_Product_Inquiry]
2. "escalate": true if human intervention is needed (e.g. refund, stolen item, angry customer), false otherwise.
3. "escalation_reason": Short reason for escalation decision.
4. "draft_reply": A polite reply grounded in the historical examples below.
   RULES FOR REPLY:
   - Do NOT include employee initials/signatures (like ^VB, ^HD, ^JT).
   - Do NOT prepend @AmazonHelp or customer handle placeholders.
   - Keep it concise, helpful, and empathetic.

Historical Examples:
{json.dumps(context, indent=2)}

Customer Tweet:
{customer_query}
"""
        response = self.model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()
            
        data = json.loads(text)
        
        # Defensive post-cleaning to strip trailing agent signatures like ^VB
        if "draft_reply" in data and isinstance(data["draft_reply"], str):
            clean_reply = re.sub(r'\s*\^[A-Za-z]{1,4}\s*$', '', data["draft_reply"]).strip()
            clean_reply = re.sub(r'^@\w+\s*', '', clean_reply).strip()
            data["draft_reply"] = clean_reply
            
        return data
