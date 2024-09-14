import json
import os

def extract_tags():
    all_tags = {}
    memory_dir = 'memory'
    
    for filename in os.listdir(memory_dir):
        if filename.endswith('.json'):
            with open(os.path.join(memory_dir, filename), 'r') as file:
                data = json.load(file)
                for index, item in enumerate(data):
                    if 'tags' in item:
                        for tag_position, tag in enumerate(item['tags']):
                            if tag_position <= 4:  # Only consider tags in positions 0-4
                                if tag not in all_tags:
                                    all_tags[tag] = {"count": 0, "articles": {}}
                                if filename not in all_tags[tag]["articles"]:
                                    all_tags[tag]["articles"][filename] = []
                                all_tags[tag]["articles"][filename].append({
                                    "index": index,
                                    "position": tag_position
                                })
                                all_tags[tag]["count"] += 1

    # Filter out tags with no articles
    relevant_tags = {tag: info for tag, info in all_tags.items() if info["count"] > 0}
    
    return relevant_tags

def save_tags_to_file(tags):
    with open('static/tags.json', 'w') as file:
        json.dump({"tags": tags}, file, indent=2)

if __name__ == "__main__":
    tags = extract_tags()
    save_tags_to_file(tags)
    print(f"Extracted relevant tags with article counts, and saved to static/tags.json")