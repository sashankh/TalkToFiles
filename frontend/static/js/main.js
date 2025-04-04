// DOM Elements
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const messagesContainer = document.getElementById('messages');
const submitButton = document.getElementById('submit-button');
const sourcesPanel = document.getElementById('sources-panel');
const closeSources = document.getElementById('close-sources');
const sourcesContent = document.getElementById('sources-content');

// Document List Elements
const documentList = document.getElementById('document-list');
const refreshDocsBtn = document.getElementById('refresh-docs-btn');

// File Upload Elements
const uploadForm = document.getElementById('upload-form');
const fileUpload = document.getElementById('file-upload');
const fileName = document.getElementById('file-name');
const uploadButton = document.getElementById('upload-button');
const uploadStatus = document.getElementById('upload-status');

// Chat history for context
let chatHistory = [];

// Function to fetch and display the document list
function fetchDocumentList() {
    // Show loading state
    documentList.innerHTML = '<p class="loading-documents">Loading documents...</p>';
    
    // Fetch documents from API
    fetch('/api/documents')
        .then(response => response.json())
        .then(data => {
            // Clear loading message
            documentList.innerHTML = '';
            
            if (data.documents && data.documents.length > 0) {
                console.log('Documents retrieved:', data.documents);
                
                // Create a list for the documents
                const docListElement = document.createElement('ul');
                docListElement.classList.add('doc-list');
                
                // Add each document to the list
                data.documents.forEach(doc => {
                    const docItem = document.createElement('li');
                    docItem.classList.add('doc-item');
                    
                    const docIcon = document.createElement('span');
                    docIcon.classList.add('doc-icon');
                    
                    // Add different icon based on file type
                    const fileType = doc.file_type || '';
                    if (fileType.includes('pdf')) {
                        docIcon.textContent = '📄';
                    } else if (fileType.includes('txt')) {
                        docIcon.textContent = '📝';
                    } else {
                        docIcon.textContent = '📑';
                    }
                    
                    const docTitle = document.createElement('span');
                    docTitle.classList.add('doc-title');
                    docTitle.textContent = doc.title || 'Unknown document';
                    
                    docItem.appendChild(docIcon);
                    docItem.appendChild(docTitle);
                    docListElement.appendChild(docItem);
                });
                
                documentList.appendChild(docListElement);
            } else {
                console.log('No documents found in the response');
                // No documents found
                documentList.innerHTML = '<p class="no-documents">No documents indexed yet. Upload or add documents to the watch directory.</p>';
            }
        })
        .catch(error => {
            console.error('Error fetching documents:', error);
            documentList.innerHTML = '<p class="error">Error loading documents. Please try again.</p>';
        });
}

// Event listener for refresh button
refreshDocsBtn.addEventListener('click', fetchDocumentList);

// Function to auto-resize textarea as user types
userInput.addEventListener('input', function() {
    // Reset height to auto to get the correct scrollHeight
    this.style.height = 'auto';
    
    // Set new height based on scrollHeight (with a max of 200px)
    const newHeight = Math.min(this.scrollHeight, 200);
    this.style.height = newHeight + 'px';
});

// Add Enter key functionality to send messages
userInput.addEventListener('keydown', function(e) {
    // Check if Enter key was pressed without Shift (Shift+Enter allows for newlines)
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault(); // Prevent default behavior (newline)
        submitButton.click(); // Trigger the submit button click
    }
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
    // Load the document list when the page loads
    fetchDocumentList();
});

// File Upload Functionality
fileUpload.addEventListener('change', function() {
    const file = this.files[0];
    if (file) {
        fileName.textContent = file.name;
    } else {
        fileName.textContent = 'No file chosen';
    }
});

uploadForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const file = fileUpload.files[0];
    if (!file) {
        uploadStatus.textContent = 'Please select a file to upload';
        uploadStatus.style.color = '#ff6b6b';
        return;
    }
    
    // Only allow PDF and TXT files
    if (!file.name.match(/\.(pdf|txt)$/i)) {
        uploadStatus.textContent = 'Please select a PDF or TXT file';
        uploadStatus.style.color = '#ff6b6b';
        return;
    }
    
    // Disable upload button during upload
    uploadButton.disabled = true;
    uploadStatus.textContent = 'Uploading...';
    uploadStatus.style.color = 'rgba(255, 255, 255, 0.7)';
    
    try {
        // Create a FormData object and append the file
        const formData = new FormData();
        formData.append('file', file);
        
        // Send the file to the server
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            uploadStatus.textContent = 'File uploaded successfully!';
            uploadStatus.style.color = '#4ade80';
            
            // Reset the file input
            fileUpload.value = '';
            fileName.textContent = 'No file chosen';
            
            // Show success message in chat
            addMessage(`I've uploaded ${file.name} and processed it for you. You can now ask questions about this document.`, 'user');
            addMessage('The document has been successfully processed. I can now answer questions about it.', 'assistant');
            
            // Refresh the document list
            fetchDocumentList();
        } else {
            uploadStatus.textContent = result.detail || 'Error uploading file';
            uploadStatus.style.color = '#ff6b6b';
        }
    } catch (error) {
        console.error('Error:', error);
        uploadStatus.textContent = 'Error uploading file';
        uploadStatus.style.color = '#ff6b6b';
    }
    
    // Re-enable upload button
    uploadButton.disabled = false;
});