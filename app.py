from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import os

app = Flask(__name__)

OPENROUTER_API_KEY = "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"
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# Route to serve the HTML file
@app.route('/')
def index():
    return render_template('index.html')

# API endpoint to handle chat requests
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        completion = client.chat.completions.create(
            model="deepseek/deepseek-r1:free", 
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful and friendly AI assistant."
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )
        
        ai_response = completion.choices[0].message.content
        return jsonify({'response': ai_response})

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': 'An internal error occurred'}), 500

if __name__ == '__main__':
    app.run(debug=True)
