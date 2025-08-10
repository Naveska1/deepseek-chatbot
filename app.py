from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import os
import base64

app = Flask(__name__)

# This line now gets the API key from a secure environment variable.
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')

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
    user_message = data.get('message', '')
    file_contents = data.get('fileContents', '')
    image_data = data.get('imageData', None)

    if not user_message and not file_contents and not image_data:
        return jsonify({'error': 'No message or file content provided'}), 400

    try:
        # Construct the conversation history for the AI
        chat_history = []

        # Build the prompt with file contents if available
        if file_contents:
            full_message = f"Here is some text content for you to analyze:\n\n{file_contents}\n\nUser request: {user_message}"
        else:
            full_message = user_message

        # Handle image and text content together (multimodal)
        if image_data:
            # For multimodal input, we need a specific model like Gemini
            # Note: This requires the OpenAI client to be configured for a Gemini-compatible API
            # For OpenRouter, the models are specified in the 'model' parameter
            
            # The prompt for the AI to analyze the image
            prompt_for_image = full_message or "What can you tell me about this image?"

            # Structure the payload for a multimodal request
            payload = {
                "model": "openai/gpt-oss-20b:free", # Specify Gemini model for multimodal
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt_for_image
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ]
            }

            completion = client.chat.completions.create(**payload)
        
        # Handle text-only chat
        else:
            completion = client.chat.completions.create(
                # Use DeepSeek for a powerful text-only chat experience
                model="deepseek/deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful and friendly AI assistant. You can analyze text content and provide summaries or insights."
                    },
                    {
                        "role": "user",
                        "content": full_message
                    }
                ]
            )

        ai_response = completion.choices[0].message.content
        return jsonify({'response': ai_response})

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': f'An internal error occurred: {e}'}), 500

if __name__ == '__main__':
    if OPENROUTER_API_KEY is None:
        print("Error: OPENROUTER_API_KEY environment variable is not set.")
    else:
        # Run the app in debug mode
        app.run(debug=True)
