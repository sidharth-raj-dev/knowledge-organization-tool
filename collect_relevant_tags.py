import json
import os
from collections import defaultdict

def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def save_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

def scan_tags_for_topic(topic_title):
    # Load tags data
    tags_data = load_json('static/tags.json')
    
    # Load node data for the topic
    node_data = load_json(f'nodes/{topic_title}.json')
    
    # Extract relevant labels (node IDs)
    relevant_labels = set(node['id'] for node in node_data.get('nodes', []))
    
    # Scan for relevant tags
    relevant_tags = defaultdict(lambda: {'count': 0, 'articles': {}})
    
    for tag, info in tags_data.get('tags', {}).items():
        for article, article_info in info.get('articles', {}).items():
            if article.replace('.json', '') in relevant_labels:
                relevant_tags[tag]['count'] += 1
                relevant_tags[tag]['articles'][article] = article_info
    
    # Sort tags by count
    sorted_tags = dict(sorted(relevant_tags.items(), key=lambda x: x[1]['count'], reverse=True))
    
    return sorted_tags

def main():
    # Assume topics are stored in a 'topics' folder
    topics_folder = 'topics'
    tags_folder = 'tags'
    
    # Create tags folder if it doesn't exist
    os.makedirs(tags_folder, exist_ok=True)
    
    for topic_file in os.listdir(topics_folder):
        if topic_file.endswith('.txt'):
            topic_title = topic_file.replace('.txt', '')
            
            # Scan tags for the topic
            topic_tags = scan_tags_for_topic(topic_title)
            
            # Save the result in the tags folder
            save_json(topic_tags, os.path.join(tags_folder, f'{topic_title}.json'))
            
            print(f"Processed tags for topic: {topic_title}")

if __name__ == "__main__":
    main()