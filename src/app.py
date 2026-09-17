import os
from flask import Flask, render_template, request, jsonify
from agent import AmazonSupportAgent

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, '..', 'data', 'processed', 'amazon_conversations.csv')

agent = None
init_error = None

print("Booting up the AI Server...")
try:
    agent = AmazonSupportAgent(DATA_PATH)
except Exception as e:
    init_error = str(e)
    print(f"\n⚠️  Notice on startup: {init_error}\n")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/process', methods=['POST'])
def process_tweet():
    global agent, init_error
    if agent is None:
        try:
            agent = AmazonSupportAgent(DATA_PATH)
            init_error = None
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
    app.run(debug=True, port=5000)
