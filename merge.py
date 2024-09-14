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
    "temperature": 0.5,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 100000,
    "response_mime_type": "text/plain",
}
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
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

def merge_graphs(existing_graph, new_graph):
    # Create sets of existing node IDs and link pairs
    existing_node_ids = set(node['id'] for node in existing_graph['nodes'])
    existing_links = set((link['source'], link['target']) for link in existing_graph['links'])

    # Add new nodes that don't already exist
    for node in new_graph['nodes']:
        if node['id'] not in existing_node_ids:
            existing_graph['nodes'].append(node)
            existing_node_ids.add(node['id'])

    # Add new links that don't already exist
    for link in new_graph['links']:
        link_pair = (link['source'], link['target'])
        if link_pair not in existing_links:
            existing_graph['links'].append(link)
            existing_links.add(link_pair)

    return existing_graph

def select_important_topics(topics, existing_graph, model):
    history = [{"role": "model", "parts": [f"""
You are an AI assistant tasked with selecting the most important topics to add to a knowledge graph.
Your goal is to identify the top 5 most important and relevant topics from the given list,
considering their potential impact and relationship to the existing graph structure.

Existing graph structure:
{json.dumps(existing_graph, indent=2)}

List of new topics to consider:
{", ".join(topics)}

Please select the 5 most important topics from the list above, considering:
1. Their relevance to the existing graph structure
2. Their potential to enhance the overall knowledge representation
3. Their importance in the field of study (in this case, related to React and web development)

Provide your response as a JSON array containing only the selected topic names, without any additional explanation.
"""]}]

    active_chat_session = model.start_chat(history=history)
    response = active_chat_session.send_message("Select the 5 most important topics.")
    ai_response = get_content(response)
    
    important_topics = extract_json(ai_response)
    if important_topics and isinstance(important_topics, list):
        return important_topics[:5]  # Ensure we only return up to 5 topics
    else:
        print("Failed to extract important topics")
        return []

def update_knowledge_graph(existing_graph, new_topics):
    # Check which topics are actually new
    existing_topics = set(node['id'] for node in existing_graph['nodes'])
    truly_new_topics = [topic for topic in new_topics if topic not in existing_topics]

    # If there are no new topics, return the existing graph unchanged
    if not truly_new_topics:
        print("All topics already exist in the graph. No update needed.")
        return existing_graph

    # Select important topics using LLM
    important_topics = select_important_topics(truly_new_topics, existing_graph, model)

    if not important_topics:
        print("No important new topics identified. No update needed.")
        return existing_graph

    print(f"Selected important topics for integration: {', '.join(important_topics)}")

    history = [{"role": "model", "parts": [f"""
You are a smart knowledge graph agent that creates and updates knowledge graphs 
based on lists of topics, subtopics, and existing graph structures. Follow these rules 
to create an informative and interconnected graph:

1. Use group id 1 for main topics and group id 2 for subtopics.
2. All group 2 nodes (subtopics) must have a parentId linking to their main topic.
3. Ensure every node is connected to at least one other node to prevent isolated nodes.
4. Preserve all existing nodes in the graph to avoid data loss. Only add new nodes and connections.
5. Create meaningful connections between nodes based on their relationships:
   - Connect related topics and subtopics across different main topics.
   - Link subtopics that have interdependencies or shared concepts.
   - Create connections that reflect learning paths or conceptual hierarchies.
6. Aim for a balance between group 1 and group 2 nodes, ensuring major topics are well-represented.
7. When adding new topics from the provided list, integrate them logically into the existing structure:
   - If a new topic fits as a main topic, add it as a group 1 node.
   - If it's more specific, add it as a group 2 node and connect it to an appropriate parent.
   - Create connections to existing nodes where relevant.

New topics to integrate:
{", ".join(important_topics)}

Existing graph:
{json.dumps(existing_graph, indent=2)}

Based on these instructions and the existing graph, create an updated knowledge graph 
that incorporates the new topics and follows the specified rules. Return only the JSON 
of the updated graph without any additional explanation. Include only the new nodes and links
you are adding to the existing graph.
"""]}]

    active_chat_session = model.start_chat(history=history)
    response = active_chat_session.send_message("Generate the updated knowledge graph.")
    ai_response = get_content(response)
    
    new_graph = extract_json(ai_response)
    if new_graph:
        return merge_graphs(existing_graph, new_graph)
    else:
        print("Failed to generate or extract updated graph")
        return existing_graph

# Example usage
existing_graph = {
    "nodes": [
        {
            "id": "Functional Components",
            "group": 1
        },
        {
            "id": "Rendering",
            "group": 1
        },
        {
            "id": "useState",
            "group": 2,
            "parentId": "Functional Components"
        },
        {
            "id": "useEffect",
            "group": 2,
            "parentId": "Functional Components"
        },
        {
            "id": "Virtual DOM",
            "group": 2,
            "parentId": "Rendering"
        },
        {
            "id": "Reconciliation",
            "group": 2,
            "parentId": "Rendering"
        }
    ],
    "links": [
        {
            "source": "Functional Components",
            "target": "Rendering"
        },
        {
            "source": "Functional Components",
            "target": "useState"
        },
        {
            "source": "Functional Components",
            "target": "useEffect"
        },
        {
            "source": "Rendering",
            "target": "Virtual DOM"
        },
        {
            "source": "Rendering",
            "target": "Reconciliation"
        }
    ]
}

new_topics = [
    "Hooks", "Forms", "Controlled Components", "State Management", "Validation", 
    "Event Handling", "Accessibility", "JSX", "Props", "State and Lifecycle",
    "Immutability", "Object.assign", "Side Effects", "Data Fetching", 
    "Event Listeners", "Cleanup Function"
]

updated_graph = update_knowledge_graph(existing_graph, new_topics)
print(json.dumps(updated_graph, indent=2))