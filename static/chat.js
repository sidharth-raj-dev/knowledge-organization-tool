const chatOutput = document.getElementById('chat-output');
const sidePanel = document.getElementById('sidePanel');
const closeButton = document.getElementById('close-btn');

function sendMessage() {
    const messageInput = document.querySelector('#chat-input input');
    if (!messageInput) {
        console.error('Chat input field not found');
        return;
    }
    const message = messageInput.value.trim();
    if (message === '') {
        console.log('Empty message, not sending');
        return;
    }

    appendMessage('user', message);
    messageInput.value = '';

    fetch('/api/message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: message }),
    })
        .then(response => {
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            let fullResponse = '';

            function processStream({ done, value }) {
                if (done) {
                    console.log('Stream complete');
                    return;
                }

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n\n');
                buffer = lines.pop();

                lines.forEach(line => {
                    if (line.startsWith('data: ')) {
                        const data = JSON.parse(line.slice(6));
                        if (data.chunk) {
                            appendMessage('assistant', data.chunk, true);
                            fullResponse += data.chunk;
                        } else if (data.json_data) {
                            console.log('Received JSON data:', data.json_data);
                        } else if (data.end) {
                            console.log('End of stream');
                            processFullResponse(fullResponse);
                        }
                    }
                });

                return reader.read().then(processStream);
            }

            return reader.read().then(processStream);
        })
        .catch(error => {
            console.error('Error:', error);
            appendMessage('assistant', 'An error occurred while processing your request.');
        });
}

function appendMessage(role, content, isStreaming = false) {
    const chatOutput = document.getElementById('chat-output');
    let messageElement;

    if (isStreaming && chatOutput.lastElementChild && chatOutput.lastElementChild.dataset.role === 'assistant') {
        messageElement = chatOutput.lastElementChild;
        messageElement.innerHTML += content;
    } else {
        messageElement = document.createElement('div');
        messageElement.classList.add('message', role);
        messageElement.dataset.role = role;
        messageElement.innerHTML = content;
        chatOutput.appendChild(messageElement);
    }

    chatOutput.scrollTop = chatOutput.scrollHeight;
}

function processFullResponse(fullResponse) {
    const chatOutput = document.getElementById('chat-output');
    const lastMessage = chatOutput.lastElementChild;
    if (lastMessage && lastMessage.dataset.role === 'assistant') {
        lastMessage.innerHTML = marked.parse(fullResponse);
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const sendButton = document.querySelector('#chat-input button');
    const inputField = document.querySelector('#chat-input input');

    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    } else {
        console.error('Send button not found');
    }

    if (inputField) {
        inputField.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    } else {
        console.error('Input field not found');
    }
});

document.getElementById('close-btn').addEventListener('click', function () {
    document.getElementById('chat-panel').classList.remove('open');
});