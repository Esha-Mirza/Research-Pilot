from flask import Flask, render_template, request, jsonify
from orchestrator import run_research

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/research', methods=['POST'])
def research_endpoint():
    data = request.get_json()
    topic = data.get('topic', '').strip()
    
    if not topic:
        return jsonify({"error": "Topic is required"}), 400
        
    try:
        # Executes orchestrator workflow
        results = run_research(topic)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)