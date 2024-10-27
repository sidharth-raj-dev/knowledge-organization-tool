from flask import Flask, render_template, abort
import os
import json

app = Flask(__name__)

# Get the absolute path to the directory containing app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_articles_metadata():
    try:
        metadata_path = os.path.join(BASE_DIR, 'articles_meta.json')
        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

@app.route('/')
def index():
    # Load metadata
    articles_meta = load_articles_metadata()
    
    # Get list of available markdown files
    articles = []
    articles_dir = os.path.join(BASE_DIR, 'articles')
    if os.path.exists(articles_dir):
        for filename in os.listdir(articles_dir):
            if filename.endswith('.md'):
                article_id = filename[:-3]  # Remove .md extension
                # Get metadata if available, otherwise use filename as title
                article_data = articles_meta.get(article_id, {
                    'title': article_id,
                    'tags': [],
                    'description': '',
                    'date': ''
                })
                article_data['id'] = article_id  # Add the ID for linking
                articles.append(article_data)
    
    # Sort by date (newest first) if date exists
    articles.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    return render_template('base.html', articles=articles)

@app.route('/article/<name>')
def article(name):
    try:
        article_path = os.path.join(BASE_DIR, 'articles', f'{name}.md')
        with open(article_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return render_template('article.html', content=content)
    except FileNotFoundError:
        abort(404)

if __name__ == '__main__':
    app.run(debug=True)