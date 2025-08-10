from flask import Flask, request, jsonify, render_template
import os
import requests
import base64
from PyPDF2 import PdfReader # Import the PDF library

app = Flask(__name__)

# This line now gets the API key from a secure environment variable.
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# Route to serve the HTML file
@app.route('/')
def index():
    return render_template('index.html')

# API endpoint to handle chat and file uploads
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.form.get('message', '')
    
    file_contents = ''
    image_data = None
    
    # Process files from the form data
    if 'file' in request.files:
        for uploaded_file in request.files.getlist('file'):
            file_type = uploaded_file.content_type
            
            if file_type == 'application/pdf':
                try:
                    pdf_reader = PdfReader(uploaded_file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() or ""
                    file_contents += f"Content from PDF '{uploaded_file.filename}':\n\n{text}\n\n"
                except Exception as e:
                    return jsonify({'error': f'Failed to process PDF: {str(e)}'}), 400
            
            elif file_type.startswith('image/'):
                image_bytes = uploaded_file.read()
                image_data = base64.b64encode(image_bytes).decode('utf-8')
            
            elif file_type.startswith('text/'):
                text = uploaded_file.read().decode('utf-8')
                file_contents += f"Content from text file '{uploaded_file.filename}':\n\n{text}\n\n"

    if not user_message and not file_contents and not image_data:
        return jsonify({'error': 'No message or file content provided'}), 400

    try:
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        headers = {
            "Content-Type": "application/json"
        }

        parts = []
        if user_message:
            parts.append({"text": user_message})
        if file_contents:
            parts.append({"text": file_contents})
        if image_data:
            parts.append({
                "inlineData": {
                    "mimeType": "image/jpeg",
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

