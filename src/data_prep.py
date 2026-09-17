import pandas as pd
import os

# Set base project directory (one level up from src/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_INPUT_CSV = os.path.join(BASE_DIR, 'data', 'raw', 'twcs.csv')
DEFAULT_OUTPUT_CSV = os.path.join(BASE_DIR, 'data', 'processed', 'amazon_conversations.csv')

def extract_amazon_threads(input_csv=DEFAULT_INPUT_CSV, output_csv=DEFAULT_OUTPUT_CSV):
    print(f"Looking for dataset at {input_csv}...")
    
    if not os.path.exists(input_csv):
        print(f"Error: Could not find {input_csv}.")
        print("Please download 'twcs.csv' from Kaggle and place it in the 'data/raw/' folder.")
        return

    print("Loading the massive dataset (this might take a minute)...")
    # Load only necessary columns to save RAM
    df = pd.read_csv(input_csv, usecols=['tweet_id', 'author_id', 'inbound', 'text', 'in_response_to_tweet_id'])
    
    print("Extracting Amazon replies...")
    # Find all tweets where the author is AmazonHelp
    amazon_replies = df[df['author_id'] == 'AmazonHelp']
    
    print("Matching Amazon replies to customer queries...")
    # Merge the dataset with itself to link the Customer's tweet with Amazon's reply
    conversations = pd.merge(
        amazon_replies, 
        df, 
        left_on='in_response_to_tweet_id', 
        right_on='tweet_id', 
        suffixes=('_amazon', '_customer')
    )
    
    # Clean up the final dataset
    final_df = conversations[[
        'tweet_id_customer', 
        'text_customer', 
        'text_amazon'
    ]].copy()
    
    final_df.columns = ['customer_tweet_id', 'customer_text', 'amazon_reply']
    final_df = final_df.dropna()
    
    print(f"Success! Extracted {len(final_df)} Amazon conversations.")
    
    # Ensure processed directory exists and save
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    final_df.to_csv(output_csv, index=False)
    print(f"Saved to {output_csv}. You can now open this easily!")

if __name__ == "__main__":
    extract_amazon_threads()

