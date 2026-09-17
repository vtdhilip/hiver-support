import argparse
import sys
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'src'))

def main():
    parser = argparse.ArgumentParser(description="Amazon AI Customer Support Agent & Evaluation CLI")
    parser.add_argument("--query", type=str, help="Run inference on a single incoming customer tweet via CLI")
    parser.add_argument("--eval", action="store_true", help="Run the automated evaluation benchmark on the 200-sample Golden Set")
    parser.add_argument("--serve", action="store_true", help="Launch the interactive web dashboard (Flask)")
    
    args = parser.parse_args()
    
    if args.query:
        from agent import AmazonSupportAgent
        data_path = os.path.join(BASE_DIR, 'data', 'knowledge_base.csv')
        agent = AmazonSupportAgent(data_path)
        result = agent.process_message(args.query)
        
        print("\n" + "="*50)
        print("📦 AGENT TRIAGE RESULT")
        print("="*50)
        print(f"🧠 Detected Intent:     {result.get('intent')}")
        print(f"🚨 Escalation Decision: {'ESCALATE TO HUMAN' if result.get('escalate') else 'AUTO-HANDLE APPROVED'}")
        print(f"📝 Decision Reason:     {result.get('escalation_reason')}")
        print(f"💬 Drafted Reply:       {result.get('draft_reply')}")
        print("="*50 + "\n")
        
    elif args.eval:
        from evaluate import run_evaluation
        run_evaluation()
        
    elif args.serve:
        from app import app
        port = int(os.environ.get("PORT", 5000))
        print(f"Starting server on http://localhost:{port}")
        app.run(host="0.0.0.0", port=port)
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
