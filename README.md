pip install python-dotenv
pip install google-generativeai
pip install flask

todo:

auto categorization [done]
voice support
response streaming [done]
past chats
kg update (imp) [done]
summary (imp) [done]

dev:

adding a topic
    1. make {topic}.json file
    2. make {topic}.txt file

maintainance
    1. run extract_tags
    2. run summarize
    3. run compile_summary
    4. run update_knowledge_graph

concerns:

user will spend more time stuyding materials from other apps
user will find hard to talk to it in a free way
user will find this boring after some time
    how to ease ai interaction
user will not be able to upload large documents and projects in it
    or the actual ingestion will be complicated for user
after talking a lot the quality of articles will become low,
    hence everything from knowledge graph and summary quality will be low
this will not be helpful in data structures and algorithms and other fields

note

only 5 relevant tags are processed in articles route and in sidebar.
tags.json is like history. even if any nodes gets deleted, it doesnt affect history.
below scripts will not be affected.
    run extract_tags
    run summarize
    run compile_summary

features

document organization
knowledge graph
summary