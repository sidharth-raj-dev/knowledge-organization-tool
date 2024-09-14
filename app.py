from flask import Flask, request, jsonify, send_from_directory, Response
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv
import os
import json
import re
from urllib.parse import unquote

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

# Global variable to store the active chat session
active_chat_session = None
active_topic = None  # Store the active topic

def get_history_file_path(topic):
    return os.path.join("memory", f"{topic}.json")

def load_history(topic):
    file_path = get_history_file_path(topic)
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):  # Handle both missing and malformed files
        return []
    
def content_to_dict(content):
    """Converts Content or Part objects to a dictionary."""
    if isinstance(content, dict):
        result = {'role': content.get('role', ''), 'parts': content.get('parts', [])}
        for key in ['tags', 'heading', 'summary']:
            if key in content:
                result[key] = content[key]
        return result
    elif hasattr(content, 'role') and hasattr(content, 'parts'):
        result = {'role': content.role, 'parts': [str(part) for part in content.parts]}
        for key in ['tags', 'heading', 'summary']:
            if hasattr(content, key):
                result[key] = getattr(content, key)
        return result
    else:
        return content

def save_history(topic, new_messages):
    if not topic:
        raise ValueError("Topic must be defined to save history.")
    
    file_path = get_history_file_path(topic)
    
    try:
        with open(file_path, 'r') as file:
            history = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []
    
    for message in new_messages:
        message_dict = content_to_dict(message)
        
        # Handle tags, heading, and summary
        extra_info = {}
        for key in ['tags', 'heading', 'summary']:
            if key in message_dict:
                extra_info[key] = message_dict.pop(key)
        
        history_item = {
            "role": message_dict['role'],
            "parts": message_dict['parts']
        }
        history_item.update(extra_info)
        history.append(history_item)

    try:
        with open(file_path, 'w') as file:
            json.dump(history, file, indent=4)
    except Exception as e:
        print('error in save_history: ', e)

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

def stream_response(response):
    full_response = ""
    for chunk in response:
        chunk_text = chunk.text
        full_response += chunk_text
        yield f"data: {json.dumps({'chunk': chunk_text})}\n\n"
    
    json_data = extract_json(full_response)
    if json_data:
        yield f"data: {json.dumps({'json_data': json_data})}\n\n"
    
    yield f"data: {json.dumps({'end': True, 'full_response': full_response})}\n\n"

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return send_from_directory('', 'index.html')

@app.route('/canvas.html')
def canvas():
    return send_from_directory('static', 'canvas.html')

@app.route('/api/topics', methods=['GET'])
def get_topics():
    topics_dir = 'topics'
    topics = [f.split('.')[0] for f in os.listdir(topics_dir) if f.endswith('.txt')]
    return jsonify(topics)

@app.route('/api/node-data/<topic>')
def get_node_data(topic):
    try:
        with open(f'nodes/{topic}.json', 'r') as file:
            node_data = json.load(file)
        return jsonify(node_data)
    except FileNotFoundError:
        return jsonify({"error": f"Node data for {topic} not found"}), 404

@app.route('/api/node-click', methods=['POST'])
def node_click():
    global active_topic, active_chat_session
    data = request.get_json()
    main_topic = data.get('mainTopic')
    active_topic = data.get('topic')
    print(active_topic)
    
    if active_topic and main_topic:
        # history = load_history(active_topic)
        # if not history:
        try:
            with open(f'topics/{main_topic}.txt', 'r') as file:
                topic_content = file.read()

            final_prompt = f"""
you are an AI model that will help the user about {active_topic}.

{topic_content}
"""         
            history = [{"role": "model", "parts": final_prompt}]
            active_chat_session = model.start_chat(history=history)
            
            return jsonify({"message": "node clicked", "status": "success", "topic": active_topic}), 200
        except FileNotFoundError:
            return jsonify({"error": f"Topic file for {main_topic} not found"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Topic not provided"}), 400

@app.route('/api/message', methods=['POST'])
def process_message():
    global active_chat_session, active_topic
    user_input = request.json.get('message', '')

    if user_input.strip() == '':
        return jsonify({"error": "Message is empty"}), 400

    if active_chat_session is None:
        return jsonify({"error": "No active chat session. Please select a topic first."}), 400

    try:
        response = active_chat_session.send_message(user_input, stream=True)
        
        def generate():
            full_response = ""
            for chunk in stream_response(response):
                yield chunk
                if chunk.startswith("data: "):
                    data = json.loads(chunk[6:])
                    if 'chunk' in data:
                        full_response += data['chunk']
                    elif 'end' in data and data['end']:
                        full_response = data['full_response']
            
            model_message = {"role": "model", "parts": [full_response]}
            json_data = extract_json(full_response)
            if json_data:
                for key in ['tags', 'heading', 'summary']:
                    if key in json_data:
                        model_message[key] = json_data[key]
            
            new_messages = [
                {"role": "user", "parts": [user_input]},
                model_message
            ]
            active_chat_session.history.extend(new_messages)
            save_history(active_topic, new_messages)

        return Response(generate(), content_type='text/event-stream')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/articles', methods=['GET'])
def get_articles():
    encoded_tag = request.args.get('tag')
    if not encoded_tag:
        return jsonify({"error": "Tag parameter is required"}), 400

    # Decode the tag
    tag = unquote(encoded_tag)

    # Load the tags.json file
    try:
        with open('static/tags.json', 'r') as file:
            tags_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return jsonify({"error": "Tags data not found or invalid"}), 500

    if tag not in tags_data['tags']:
        return jsonify([]), 200  # Return an empty list if the tag is not found

    articles = []
    tag_info = tags_data['tags'][tag]

    for filename, occurrences in tag_info['articles'].items():
        file_path = os.path.join('memory', filename)
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                for occurrence in occurrences:
                    index = occurrence['index']
                    position = occurrence['position']
                    # Only include articles where the tag position is 4 or less
                    if position <= 4 and index < len(data):
                        item = data[index]
                        item['source'] = filename
                        item['tag_position'] = position
                        articles.append(item)
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Error reading or decoding file: {filename}")

    # Sort articles by relevancy
    # Primary sort: tag position (lower is better)
    # Secondary sort: frequency of tag in the file (higher is better)
    articles.sort(key=lambda x: (x['tag_position'], -len(tag_info['articles'][x['source']])))

    # Remove the temporary 'tag_position' key from the articles
    for article in articles:
        article.pop('tag_position', None)

    return jsonify(articles)

if __name__ == '__main__':
    app.run(debug=True)