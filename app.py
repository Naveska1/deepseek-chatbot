from flask import Flask, request, jsonify, render_template
import os
import requests
import base64

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
    file_contents = data.get('fileContents', '')
    image_data = data.get('imageData', None)

    if not user_message and not file_contents and not image_data:
        return jsonify({'error': 'No message or file content provided'}), 400

    try:
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        headers = {
            "Content-Type": "application/json"
        }

        # Build the parts for the Gemini API call
        parts = []
        if user_message:
            parts.append({"text": user_message})
        if file_contents:
            parts.append({"text": f"Here is some text content for you to analyze:\n\n{file_contents}"})
        if image_data:
            # Add image data to the parts, Gemini can handle it directly
            parts.append({
                "inlineData": {
                    "mimeType": "image/jpeg",  # Or image/png, etc.
                    "data": image_data
                }
            })

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": parts
                }
            ]
        }

        # Make the API call to Gemini
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        
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
