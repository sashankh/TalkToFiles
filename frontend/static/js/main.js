// DOM Elements
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const messagesContainer = document.getElementById('messages');
const submitButton = document.getElementById('submit-button');
const sourcesPanel = document.getElementById('sources-panel');
const closeSources = document.getElementById('close-sources');
const sourcesContent = document.getElementById('sources-content');

// Chat history for context
let chatHistory = [];

// Function to auto-resize textarea as user types
userInput.addEventListener('input', function() {
    // Reset height to auto to get the correct scrollHeight
    this.style.height = 'auto';
    
    // Set new height based on scrollHeight (with a max of 200px)
    const newHeight = Math.min(this.scrollHeight, 200);
    this.style.height = newHeight + 'px';
});

// Function to add a message to the chat
function addMessage(content, role, sourceDocuments = null) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', role);
    
    const messageContent = document.createElement('div');
    messageContent.classList.add('message-content');
    
    // Add message text
    const messageText = document.createElement('p');
    messageText.textContent = content;
    messageContent.appendChild(messageText);
    
    // Add sources link if source documents are available
    if (sourceDocuments && sourceDocuments.length > 0) {
        const sourcesLink = document.createElement('a');
        sourcesLink.classList.add('sources-link');
        sourcesLink.textContent = 'View sources';
        sourcesLink.addEventListener('click', () => showSources(sourceDocuments));
        messageContent.appendChild(sourcesLink);
    }
    
    messageDiv.appendChild(messageContent);
    messagesContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    // Add to chat history
    chatHistory.push({
        role: role,
        content: content
    });
}

// Function to show loading indicator
function showLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.classList.add('message', 'assistant', 'loading');
    loadingDiv.id = 'loading-indicator';
    
    const loadingContent = document.createElement('div');
    loadingContent.classList.add('message-content');
    
    const loadingDots = document.createElement('div');
    loadingDots.classList.add('loading-dots');
    
    for (let i = 0; i < 3; i++) {
        const dot = document.createElement('span');
        loadingDots.appendChild(dot);
    }
    
    loadingContent.appendChild(loadingDots);
    loadingDiv.appendChild(loadingContent);
    messagesContainer.appendChild(loadingDiv);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Function to hide loading indicator
function hideLoading() {
    const loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.remove();
    }
}

// Function to handle form submission
chatForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const query = userInput.value.trim();
    if (!query) return;
    
    // Add user message to chat
    addMessage(query, 'user');
    
    // Clear input field and reset height
    userInput.value = '';
    userInput.style.height = 'auto';
    
    // Disable submit button and show loading
    submitButton.disabled = true;
    showLoading();
    
    try {
        // Call API with chat history
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                messages: chatHistory,
                top_k: 5
            })
        });
        
        const data = await response.json();
        
        // Hide loading indicator
        hideLoading();
        
        // Add assistant's response to chat
        addMessage(data.answer, 'assistant', data.source_documents);
    } catch (error) {
        console.error('Error:', error);
        hideLoading();
        addMessage('Sorry, there was an error processing your request. Please try again.', 'assistant');
    }
    
    // Re-enable submit button
    submitButton.disabled = false;
});

// Function to show sources panel
function showSources(sources) {
    // Clear previous content
    sourcesContent.innerHTML = '';
    
    if (sources && sources.length > 0) {
        sources.forEach((source, index) => {
            const sourceItem = document.createElement('div');
            sourceItem.classList.add('source-item');
            
            const sourceHeader = document.createElement('h4');
            sourceHeader.textContent = source.source || 'Document';
            
            const similaritySpan = document.createElement('span');
            similaritySpan.classList.add('similarity');
            similaritySpan.textContent = `${Math.round(source.similarity * 100)}% match`;
            sourceHeader.appendChild(similaritySpan);
            
            const sourceText = document.createElement('p');
            sourceText.textContent = source.text || '';
            
            sourceItem.appendChild(sourceHeader);
            sourceItem.appendChild(sourceText);
            
            sourcesContent.appendChild(sourceItem);
        });
    } else {
        const noSources = document.createElement('p');
        noSources.classList.add('no-sources');
        noSources.textContent = 'No sources available for this response.';
        sourcesContent.appendChild(noSources);
    }
    
    // Show panel
    sourcesPanel.classList.add('active');
}

// Close sources panel
closeSources.addEventListener('click', function() {
    sourcesPanel.classList.remove('active');
});

// Initialize - autofocus on input
document.addEventListener('DOMContentLoaded', function() {
    userInput.focus();
});