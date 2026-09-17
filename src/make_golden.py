import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_PATH = os.path.join(BASE_DIR, '..', 'data', 'processed', 'amazon_conversations.csv')
OUTPUT_PATH = os.path.join(BASE_DIR, '..', 'data', 'golden_set.csv')

print(f"Reading from {INPUT_PATH}...")
df = pd.read_csv(INPUT_PATH)

# Filter for clean English tweets
df_clean = df.dropna()
df_english = df_clean[df_clean['customer_text'].map(lambda x: str(x).isascii())]

# Stratified random sample of 200 tweets for the Golden Evaluation Set
sample_size = min(200, len(df_english))
golden_df = df_english.sample(sample_size, random_state=42).reset_index(drop=True)

# Add empty columns ready for human labeling
golden_df['true_intent'] = ""
golden_df['true_escalate'] = ""
golden_df['true_escalation_reason'] = ""

golden_df.to_csv(OUTPUT_PATH, index=False)
print(f"Saved {sample_size} English tweets to {OUTPUT_PATH}! Ready for labeling.")
