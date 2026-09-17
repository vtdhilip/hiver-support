import os
from flask import Flask, render_template, request, jsonify
from agent import AmazonSupportAgent

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Check for packaged 1.2MB knowledge base first, then fallback to processed
KB_PATH = os.path.join(BASE_DIR, '..', 'data', 'knowledge_base.csv')
if not os.path.exists(KB_PATH):
    KB_PATH = os.path.join(BASE_DIR, '..', 'data', 'processed', 'amazon_conversations.csv')

print(f"Booting up AI Server with knowledge base: {KB_PATH}")
agent = None
try:
    agent = AmazonSupportAgent(KB_PATH)
except Exception as e:
    print(f"Notice on startup: {e}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/process', methods=['POST'])
def process_tweet():
    global agent
    if agent is None:
        try:
            agent = AmazonSupportAgent(KB_PATH)
        except Exception as e:
            return jsonify({"error": f"Agent could not initialize: {e}"}), 500

    data = request.get_json()
    customer_tweet = data.get('tweet', '')
    if not customer_tweet:
        return jsonify({"error": "No tweet provided"}), 400
    try:
        result = agent.process_message(customer_tweet)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
