from flask import Flask, render_template, abort
import os

app = Flask(__name__)

@app.route('/')
def index():
    # List all markdown files in articles directory
    articles = []
    for filename in os.listdir('articles'):
        if filename.endswith('.md'):
            articles.append(filename[:-3])  # Remove .md extension
    return render_template('base.html', articles=articles)

@app.route('/article/<name>')
def article(name):
    try:
        # Read the markdown file
        with open(f'articles/{name}.md', 'r', encoding='utf-8') as file:
            content = file.read()
        return render_template('article.html', content=content)
    except FileNotFoundError:
        abort(404)

if __name__ == '__main__':
    app.run(debug=True)
