import os
import json
from collections import defaultdict

def load_json(file_path):
    print(f"Loading JSON file: {file_path}")
    with open(file_path, 'r') as file:
        return json.load(file)

def save_text(content, file_path):
    print(f"Saving text file: {file_path}")
    with open(file_path, 'w') as file:
        file.write(content)

def compile_summary(topic):
    print(f"\nCompiling summary for topic: {topic}")
    tags_file = f'tags/{topic}.json'
    summary_file = f'summary/{topic}.txt'
    
    if not os.path.exists(tags_file):
        print(f"Tags file not found for topic: {topic}")
        return

    tags_data = load_json(tags_file)
    print(f"Loaded tags data for {topic}. Found {len(tags_data)} tags.")
    
    summary = f"Summary for {topic}:\n\n"
    article_summaries = defaultdict(set)  # Using a set to store unique summaries

    for tag, info in tags_data.items():
        print(f"Processing tag: {tag}")
        for article, positions in info['articles'].items():
            print(f"  Processing article: {article}")
            memory_file = f'memory/{article}'
            if os.path.exists(memory_file):
                memory_data = load_json(memory_file)
                print(f"    Loaded memory file: {memory_file}")
                for position in positions:
                    index = position['index']
                    if index < len(memory_data):
                        entry = memory_data[index]
                        if 'summary' in entry:
                            article_summaries[article].add(entry['summary'])
                            print(f"    Added unique summary for index {index}")

    print(f"Compiled unique summaries for {len(article_summaries)} articles.")

    for article, summaries in article_summaries.items():
        # summary += f"Article: {article}\n"
        for s in summaries:
            summary += f"- {s}\n"
        summary += "\n"

    # Track progress (simple metric: number of articles covered)
    total_articles = len(article_summaries)
    summary += f"\nProgress: {total_articles} articles covered in this topic.\n"

    save_text(summary, summary_file)
    print(f"Summary compiled and saved for topic: {topic}")

def main():
    topics_folder = 'topics'
    summary_folder = 'summary'

    print(f"Starting summary compilation process.")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Topics folder: {topics_folder}")
    print(f"Summary folder: {summary_folder}")

    # Create summary folder if it doesn't exist
    os.makedirs(summary_folder, exist_ok=True)

    # List contents of topics folder
    print(f"Contents of {topics_folder} folder:")
    try:
        for item in os.listdir(topics_folder):
            print(f"  {item}")
    except FileNotFoundError:
        print(f"  Error: {topics_folder} folder not found")
    except PermissionError:
        print(f"  Error: Permission denied to access {topics_folder} folder")

    topic_files = [f for f in os.listdir(topics_folder) if f.endswith('.txt')]
    print(f"Found {len(topic_files)} topic files.")

    for topic_file in topic_files:
        topic = topic_file.replace('.txt', '')
        compile_summary(topic)

    print("Summary compilation process completed.")

if __name__ == "__main__":
    main()