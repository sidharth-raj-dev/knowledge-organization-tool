from flask import Flask, request, jsonify, send_from_directory
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()
genai.configure(api_key=os.getenv('API_KEY'))
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 100000,
    "response_mime_type": "text/plain",
}
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
)

def get_content(message):
    if hasattr(message, 'text'):
        return message.text
    elif isinstance(message, dict):
        parts = message.get('parts', [message.get('content', '')])
        return parts[0] if parts else ''
    return str(message)

def extract_json(text):
    json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            print("Failed to parse JSON")
    return None

history = [{"role": "model", "parts": [f"""
you are an ai model that will help user about Rendering.
at the end of your response give a json of tags from below topics.
this will be later used for backlinking.
topics:
Functional Components
	Stateless Components
	Props
	Lifecycle Methods (using Hooks)
	Pure Components
Rendering
	Virtual DOM
	Reconciliation
	Conditional Rendering
	Lists and Keys
Hooks
	useState
	useEffect
	Custom Hooks
	useContext
Routers
	React Router
	Route Parameters
	Nested Routes
	Redirects
format:
```json
{{
    "tags": []
}}
```
"""]}]

active_chat_session = model.start_chat(history=history)
response = active_chat_session.send_message("""
how to change state in react?
""")
ai_response = get_content(response)
print("AI Response:")
print(ai_response)

# Extract and print tags
json_data = extract_json(ai_response)
if json_data and 'tags' in json_data:
    print("\nExtracted Tags:")
    for tag in json_data['tags']:
        print(f"- {tag}")
else:
    print("\nNo tags found in the response.")

# response = model.generate_content("What is the future of AI in one sentence?", stream=True)

# for chunk in response:
#     print(chunk.text)
#     print("_"*80)