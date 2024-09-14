document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    const container = document.getElementById('container');
    const toggleButton = document.getElementById('toggle-sidebar');
    const tagList = document.getElementById('tag-list');
    const articleList = document.getElementById('article-list');
    const articleContent = document.getElementById('article-content');
    const articlePanel = document.getElementById('article-panel');
    const closeArticleBtn = document.getElementById('close-article-btn');
    const closeChatBtn = document.getElementById('close-chat-btn');
    const chatPanel = document.getElementById('chat-panel');

    // Get the current topic from the URL
    const urlParams = new URLSearchParams(window.location.search);
    const currentTopic = urlParams.get('topic');

    if (toggleButton) {
        toggleButton.addEventListener('click', () => {
            sidebar?.classList.toggle('active');
            container?.classList.toggle('sidebar-active');
        });
    }

    if (closeArticleBtn) {
        closeArticleBtn.addEventListener('click', () => {
            if (articlePanel) articlePanel.style.display = 'none';
        });
    }

    if (closeChatBtn) {
        closeChatBtn.addEventListener('click', () => {
            if (chatPanel) chatPanel.style.display = 'none';
        });
    }

    // Load tags and node data
    Promise.all([
        fetch('/static/tags.json').then(response => response.json()),
        fetch(`/api/node-data/${currentTopic}`).then(response => response.json())
    ])
        .then(([tagsData, graphData]) => {
            // Extract nodes from the new structure
            const nodes = graphData.nodes || [];
            const relevantLabels = new Set(nodes.map(node => node.id));

            const relevantTags = Object.entries(tagsData.tags || {})
                .filter(([tag, info]) => {
                    return Object.keys(info.articles || {}).some(article =>
                        relevantLabels.has(article.replace('.json', ''))
                    );
                })
                .sort((a, b) => (b[1].count || 0) - (a[1].count || 0));

            if (tagList) {
                relevantTags.forEach(([tag, info]) => {
                    const li = document.createElement('li');
                    li.innerHTML = `${tag} <span class="tag-count">(${info.count || 0})</span>`;
                    li.addEventListener('click', () => loadArticles(tag));
                    tagList.appendChild(li);
                });
            }
        })
        .catch(error => console.error('Error loading data:', error));

    function loadArticles(tag) {
        if (!articleList || !articleContent || !articlePanel) return;

        articleList.innerHTML = '<h2>Articles</h2>';
        articleContent.innerHTML = '';

        // Properly encode the tag name
        const encodedTag = encodeURIComponent(tag);

        fetch(`/api/articles?tag=${encodedTag}`)
            .then(response => response.json())
            .then(data => {
                data.forEach(article => {
                    const div = document.createElement('div');
                    const title = (article.parts[0] || '').substring(0, 50) + '...';
                    div.innerHTML = `<strong>${title}</strong><br><small>source: ${article.source || 'Unknown'}</small>`;
                    div.addEventListener('click', () => showArticleContent(article));
                    articleList.appendChild(div);
                });
                articlePanel.style.display = 'flex';
            })
            .catch(error => console.error('Error loading articles:', error));
    }

    function showArticleContent(article) {
        if (!articleContent) return;

        const content = marked.parse(article.parts[0] || '');
        articleContent.innerHTML = `
            <h4>${(article.parts[0] || '').substring(0, 50)}...</h4>
            <p><em>Source: ${article.source || 'Unknown'}</em></p>
            <div>${content}</div>
        `;
    }
});