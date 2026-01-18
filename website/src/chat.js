/**
 * ApexAurum Chat - Archetype Conversations
 * BYOK (Bring Your Own Key) client-side chat with Claude
 * Supports streaming responses
 */

// Persona metadata - prompts loaded from /prompts/*.md
const PERSONAS = {
    azoth: {
        name: 'AZOTH',
        shortName: 'Az',
        title: 'Prima Materia',
        description: 'The universal solvent - breaks down complexity to find essence',
        promptFile: 'prompts/azoth.md'
    },
    elysian: {
        name: 'ELYSIAN',
        shortName: 'El',
        title: 'The Harmonizer',
        description: 'Seeks balance and synthesis - bridges opposing viewpoints',
        promptFile: 'prompts/elysian.md'
    },
    vajra: {
        name: 'VAJRA',
        shortName: 'Vj',
        title: 'The Thunderbolt',
        description: 'Indestructible clarity - cuts through confusion with precision',
        promptFile: 'prompts/vajra.md'
    },
    kether: {
        name: 'KETHER',
        shortName: 'Ke',
        title: 'The Crown',
        description: 'The highest perspective - guides emergence and alignment',
        promptFile: 'prompts/kether.md'
    }
};

// Prompt cache - stores loaded prompts to avoid re-fetching
const promptCache = {};

// State
let currentPersona = 'azoth';
let currentModel = 'claude-sonnet-4-5-20251022';
let conversationHistory = [];
let isStreaming = false;

// DOM elements
const apiKeyInput = document.getElementById('api-key');
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const clearChatBtn = document.getElementById('clear-chat');
const personaBtns = document.querySelectorAll('.persona-btn');
const modelBtns = document.querySelectorAll('.model-btn');
const currentPersonaName = document.querySelector('.current-persona-name');
const currentPersonaDesc = document.querySelector('.current-persona-desc');
const toggleVisibilityBtn = document.querySelector('.toggle-visibility');

/**
 * Load a persona's system prompt from its markdown file
 * Caches the result to avoid repeated fetches
 */
async function loadPrompt(personaKey) {
    if (promptCache[personaKey]) {
        return promptCache[personaKey];
    }

    const persona = PERSONAS[personaKey];
    if (!persona) {
        throw new Error(`Unknown persona: ${personaKey}`);
    }

    try {
        const response = await fetch(persona.promptFile);
        if (!response.ok) {
            throw new Error(`Failed to load prompt: ${response.status}`);
        }
        const text = await response.text();
        promptCache[personaKey] = text.trim();
        return promptCache[personaKey];
    } catch (error) {
        console.error(`Error loading prompt for ${personaKey}:`, error);
        throw error;
    }
}

/**
 * Preload all prompts in background for faster persona switching
 */
async function preloadPrompts() {
    const keys = Object.keys(PERSONAS);
    await Promise.all(keys.map(key => loadPrompt(key).catch(() => {})));
    console.log('ApexAurum Chat: Prompts preloaded');
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Load saved API key from localStorage
    const savedKey = localStorage.getItem('apex_api_key');
    if (savedKey) {
        apiKeyInput.value = savedKey;
        updateSendButton();
    }

    // Load saved model preference
    const savedModel = localStorage.getItem('apex_model');
    if (savedModel) {
        currentModel = savedModel;
        modelBtns.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.model === savedModel);
        });
    }

    // Preload prompts in background
    preloadPrompts();

    // API key handling
    apiKeyInput.addEventListener('input', () => {
        localStorage.setItem('apex_api_key', apiKeyInput.value);
        updateSendButton();
    });

    // Toggle API key visibility
    toggleVisibilityBtn.addEventListener('click', () => {
        const isPassword = apiKeyInput.type === 'password';
        apiKeyInput.type = isPassword ? 'text' : 'password';
        toggleVisibilityBtn.classList.toggle('showing', !isPassword);
    });

    // Persona selection
    personaBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const persona = btn.dataset.persona;
            selectPersona(persona);
        });
    });

    // Model selection
    modelBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const model = btn.dataset.model;
            selectModel(model);
        });
    });

    // Chat input handling
    chatInput.addEventListener('input', () => {
        autoResizeTextarea();
        updateSendButton();
    });

    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Send button
    sendBtn.addEventListener('click', sendMessage);

    // Clear chat
    clearChatBtn.addEventListener('click', clearChat);

    // Mobile nav toggle
    const navToggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-links');
    if (navToggle && navLinks) {
        navToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });
    }
});

function selectPersona(persona) {
    currentPersona = persona;

    personaBtns.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.persona === persona);
    });

    const p = PERSONAS[persona];
    currentPersonaName.textContent = p.name;
    currentPersonaDesc.textContent = p.description;

    clearChat();
}

function selectModel(model) {
    currentModel = model;
    localStorage.setItem('apex_model', model);

    modelBtns.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.model === model);
    });
}

function updateSendButton() {
    const hasKey = apiKeyInput.value.trim().length > 0;
    const hasMessage = chatInput.value.trim().length > 0;
    sendBtn.disabled = !hasKey || !hasMessage || isStreaming;
}

function autoResizeTextarea() {
    chatInput.style.height = 'auto';
    chatInput.style.height = Math.min(chatInput.scrollHeight, 200) + 'px';
}

function clearChat() {
    conversationHistory = [];
    chatMessages.innerHTML = `
        <div class="welcome-message">
            <div class="welcome-glyph">
                <svg viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="45" fill="none" stroke="currentColor" stroke-width="0.5" opacity="0.3"/>
                    <polygon points="50,15 80,70 20,70" fill="none" stroke="currentColor" stroke-width="1" opacity="0.6"/>
                    <circle cx="50" cy="50" r="15" fill="none" stroke="currentColor" stroke-width="1" opacity="0.8"/>
                </svg>
            </div>
            <h3>Converse with the Archetypes</h3>
            <p>Select a persona and enter your API key to begin. Each archetype embodies a distinct approach to dialogue and problem-solving.</p>
        </div>
    `;
}

function addMessage(role, content = '') {
    const welcome = chatMessages.querySelector('.welcome-message');
    if (welcome) {
        welcome.remove();
    }

    const persona = PERSONAS[currentPersona];
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? 'You' : persona.shortName;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    if (content) {
        renderContent(contentDiv, content);
    }

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);

    chatMessages.scrollTop = chatMessages.scrollHeight;

    return contentDiv;
}

function renderContent(container, text) {
    container.innerHTML = '';
    const paragraphs = text.split('\n\n').filter(p => p.trim());
    paragraphs.forEach(p => {
        const pEl = document.createElement('p');
        pEl.textContent = p.trim();
        container.appendChild(pEl);
    });
}

function addTypingIndicator() {
    const welcome = chatMessages.querySelector('.welcome-message');
    if (welcome) welcome.remove();

    const persona = PERSONAS[currentPersona];
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    messageDiv.id = 'typing-message';

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = persona.shortName;

    const typing = document.createElement('div');
    typing.className = 'typing-indicator';
    typing.innerHTML = '<span></span><span></span><span></span>';

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(typing);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTypingIndicator() {
    const typing = document.getElementById('typing-message');
    if (typing) typing.remove();
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'message-error';
    errorDiv.textContent = message;
    chatMessages.appendChild(errorDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendMessage() {
    const apiKey = apiKeyInput.value.trim();
    const userMessage = chatInput.value.trim();

    if (!apiKey || !userMessage || isStreaming) return;

    isStreaming = true;
    updateSendButton();

    // Add user message
    addMessage('user', userMessage);
    conversationHistory.push({ role: 'user', content: userMessage });

    // Clear input
    chatInput.value = '';
    autoResizeTextarea();

    // Show typing indicator
    addTypingIndicator();

    try {
        const systemPrompt = await loadPrompt(currentPersona);

        const response = await fetch('https://api.anthropic.com/v1/messages', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-api-key': apiKey,
                'anthropic-version': '2023-06-01',
                'anthropic-dangerous-direct-browser-access': 'true'
            },
            body: JSON.stringify({
                model: currentModel,
                max_tokens: 1024,
                stream: true,
                system: systemPrompt,
                messages: conversationHistory
            })
        });

        removeTypingIndicator();

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error?.message || `API error: ${response.status}`);
        }

        // Create message container for streaming
        const contentDiv = addMessage('assistant', '');
        let fullText = '';

        // Process the stream
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);
                    if (data === '[DONE]') continue;

                    try {
                        const event = JSON.parse(data);

                        if (event.type === 'content_block_delta' && event.delta?.text) {
                            fullText += event.delta.text;
                            renderContent(contentDiv, fullText);
                            chatMessages.scrollTop = chatMessages.scrollHeight;
                        }
                    } catch (e) {
                        // Skip non-JSON lines
                    }
                }
            }
        }

        // Add to conversation history
        conversationHistory.push({ role: 'assistant', content: fullText });

    } catch (error) {
        removeTypingIndicator();
        console.error('Chat error:', error);

        let errorMessage = error.message;
        if (error.message.includes('401')) {
            errorMessage = 'Invalid API key. Please check your key and try again.';
        } else if (error.message.includes('429')) {
            errorMessage = 'Rate limited. Please wait a moment and try again.';
        } else if (error.message.includes('Failed to fetch')) {
            errorMessage = 'Network error. Please check your connection.';
        }

        showError(errorMessage);
    }

    isStreaming = false;
    updateSendButton();
}

console.log('ApexAurum Chat: Initialized');
