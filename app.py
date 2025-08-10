from flask import Flask, request, jsonify, render_template
import os
import requests

app = Flask(__name__)

# This line now gets the API key from a secure environment variable.
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# Route to serve the HTML file
@app.route('/')
def index():
    return render_template('index.html')

# API endpoint to handle chat requests
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'No message or file content provided'}), 400

    try:
        # Gemini API endpoint for the text-only model
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Structure the payload for a text-only Gemini request
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": user_message}
                    ]
                }
            ]
        }

        # Make the API call to Gemini
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        result = response.json()
        ai_response = result['candidates'][0]['content']['parts'][0]['text']
        
        return jsonify({'response': ai_response})

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': f'An internal error occurred: {e}'}), 500

if __name__ == '__main__':
    if GEMINI_API_KEY is None:
        print("Error: GEMINI_API_KEY environment variable is not set. Please set it.")
    else:
        app.run(debug=True)
