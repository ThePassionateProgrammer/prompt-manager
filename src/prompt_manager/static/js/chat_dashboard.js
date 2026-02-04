// Import modules
import * as VoiceInteraction from './modules/voice_interaction.js';
import * as ConversationMode from './modules/conversation_mode.js';
import * as Notifications from './modules/notifications.js';
import * as ErrorHandler from './modules/error_handler.js';
import * as StateIndicator from './modules/conversation_state_indicator.js';
import * as VoiceSettings from './modules/voice_settings.js';
import * as Config from './modules/config.js';

// State management
let messages = [];
let currentProvider = 'openai';
let isLoading = false;
let currentConversationId = null;
let systemPrompt = null;

// Get conversation mode state machine from module
const conversationMode = ConversationMode.getConversationMode();

// Initialize
document.addEventListener('DOMContentLoaded', async function() {
    setupEventListeners();

    // Initialize error handler with notifications
    ErrorHandler.initializeErrorHandler({
        showNotification: Notifications.showNotification
    });

    // Initialize voice settings
    VoiceSettings.initializeVoiceSettings();

    // Initialize conversation state indicator
    StateIndicator.initializeStateIndicator({
        conversationMode: conversationMode
    });

    // Initialize conversation mode module with dependencies (use new notification system)
    ConversationMode.initializeDependencies({
        VoiceInteraction: VoiceInteraction,
        showNotification: Notifications.showNotification,
        StateIndicator: StateIndicator
    });

    // Initialize voice interaction module with dependencies (use new notification system)
    VoiceInteraction.initializeDependencies({
        conversationMode: conversationMode,
        conversationModeModule: ConversationMode,
        getIsLoading: () => isLoading,
        showNotification: Notifications.showNotification
    });
    VoiceInteraction.initializeVoiceRecognition();

    loadDashboardSettings();  // Load saved dashboard settings
    loadProviders();  // Load provider dropdown
    updateWelcomeTime();
    loadSystemPrompt();
    loadChatHistory();

    // Load hands-free settings from server (must complete before SilenceDetector is used)
    await Config.loadHandsFreeSettings();
});

function setupEventListeners() {
    // Slider updates
    document.getElementById('temperature').addEventListener('input', function() {
        document.getElementById('temp-value').textContent = this.value;
    });

    document.getElementById('max-tokens').addEventListener('input', function() {
        document.getElementById('tokens-value').textContent = this.value;
    });

    // Provider selection change
    document.getElementById('provider-select').addEventListener('change', function() {
        currentProvider = this.value;  // Update current provider
        loadModelsForProvider(this.value);
    });

    // Model selection change
    document.getElementById('model-select').addEventListener('change', function() {
        updateConversationMetadata();
    });

    // Input handling
    const chatInput = document.getElementById('chat-input');
    chatInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = this.scrollHeight + 'px';
    });

    // Enter creates new line - no special handling needed
    // Only Send button submits message

    // Button handlers
    document.getElementById('send-btn').addEventListener('click', sendMessage);
    document.getElementById('voice-btn').addEventListener('click', toggleVoiceInput);
    document.getElementById('conversation-mode-btn').addEventListener('click', toggleConversationMode);

    // Hands-free checkbox may not exist if it's in a modal that hasn't been opened yet
    const handsFreeCheckbox = document.getElementById('hands-free-checkbox');
    if (handsFreeCheckbox) {
        handsFreeCheckbox.addEventListener('change', (e) => {
            if (e.target.checked) {
                ConversationMode.enableHandsFreeMode();
            } else {
                ConversationMode.disableHandsFreeMode();
            }
        });
    }

    document.getElementById('clear-btn').addEventListener('click', clearChat);
    document.getElementById('export-btn').addEventListener('click', exportChat);
    document.getElementById('prompts-btn').addEventListener('click', openPromptLibrary);
    document.getElementById('prompt-lib-btn').addEventListener('click', openPromptLibrary);
    document.getElementById('chat-history-btn').addEventListener('click', openHistoryModal);
    document.getElementById('regenerate-btn').addEventListener('click', regenerateLastResponse);
    document.getElementById('save-prompt-btn').addEventListener('click', openSaveConvModal);

    // Voice settings button may not exist in new inline UI
    const voiceSettingsBtn = document.getElementById('voice-settings-btn');
    if (voiceSettingsBtn) {
        voiceSettingsBtn.addEventListener('click', openVoiceSettingsModal);
    }

    // Auto-save settings when they change
    document.getElementById('provider-select').addEventListener('change', saveDashboardSettings);
    document.getElementById('model-select').addEventListener('change', saveDashboardSettings);
    document.getElementById('temperature').addEventListener('change', saveDashboardSettings);
    document.getElementById('max-tokens').addEventListener('change', saveDashboardSettings);
}

// Load dashboard settings from server
async function loadDashboardSettings() {
    try {
        const response = await fetch('/api/settings/dashboard');
        const settings = await response.json();

        // Apply settings to controls (will be overridden by loadProviders if needed)
        if (settings.temperature) {
            const tempSlider = document.getElementById('temperature');
            tempSlider.value = settings.temperature;
            document.getElementById('temp-value').textContent = settings.temperature;
        }
        if (settings.max_tokens) {
            const tokensSlider = document.getElementById('max-tokens');
            tokensSlider.value = settings.max_tokens;
            document.getElementById('tokens-value').textContent = settings.max_tokens;
        }

        // Store for later use when providers load
        window.savedSettings = settings;
    } catch (error) {
        console.error('Error loading dashboard settings:', error);
    }
}

// Save dashboard settings to server
async function saveDashboardSettings() {
    try {
        const settings = {
            provider: document.getElementById('provider-select').value,
            model: document.getElementById('model-select').value,
            temperature: parseFloat(document.getElementById('temperature').value),
            max_tokens: parseInt(document.getElementById('max-tokens').value)
        };

        await fetch('/api/settings/dashboard', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(settings)
        });
    } catch (error) {
        console.error('Error saving dashboard settings:', error);
    }
}

// Load available providers
async function loadProviders() {
    try {
        const response = await fetch('/api/providers/list');
        const data = await response.json();

        const providerSelect = document.getElementById('provider-select');
        providerSelect.innerHTML = '';

        // Add "Select Provider" placeholder as first option
        const placeholderOption = document.createElement('option');
        placeholderOption.value = '';
        placeholderOption.textContent = 'Select Provider...';
        placeholderOption.disabled = true;
        providerSelect.appendChild(placeholderOption);

        // Add providers
        for (const [key, provider] of Object.entries(data.providers)) {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = provider.name.charAt(0).toUpperCase() + provider.name.slice(1);
            providerSelect.appendChild(option);
        }

        // Use saved provider preference if available, otherwise use default
        const savedProvider = window.savedSettings?.provider || data.default_provider;
        if (savedProvider) {
            providerSelect.value = savedProvider;
            currentProvider = savedProvider;
            await loadModelsForProvider(savedProvider);
        } else {
            // No default - show placeholder
            providerSelect.value = '';
        }
    } catch (error) {
        console.error('Error loading providers:', error);
        Notifications.showNotification('Failed to load providers', 'error');
    }
}

// Load models for selected provider
async function loadModelsForProvider(providerName) {
    if (!providerName) return;

    try {
        const response = await fetch(`/api/providers/${providerName}/models`);
        const data = await response.json();

        const modelSelect = document.getElementById('model-select');
        modelSelect.innerHTML = '';

        // Add models
        data.models.forEach((model, index) => {
            const option = document.createElement('option');
            option.value = model.id;
            option.textContent = model.name;
            modelSelect.appendChild(option);
        });

        // Select saved model if available, otherwise first one
        const savedModel = window.savedSettings?.model;
        if (savedModel && data.models.some(m => m.id === savedModel)) {
            modelSelect.value = savedModel;
        } else if (data.models.length > 0) {
            modelSelect.value = data.models[0].id;
        }

        // Update conversation metadata
        updateConversationMetadata();
    } catch (error) {
        console.error('Error loading models:', error);
        Notifications.showNotification('Failed to load models for ' + providerName, 'error');
    }
}

function togglePanel() {
    const panel = document.getElementById('control-panel');
    const btn = document.getElementById('toggle-panel-btn');

    panel.classList.toggle('collapsed');

    if (panel.classList.contains('collapsed')) {
        btn.textContent = '▼ Show Controls';
    } else {
        btn.textContent = '▲ Hide Controls';
    }
}

async function sendMessage(providedMessage = null) {
    // If called from button click, providedMessage will be the event object
    // Only use providedMessage if it's a string
    const input = document.getElementById('chat-input');
    const message = (typeof providedMessage === 'string' && providedMessage)
        ? providedMessage
        : input.value.trim();

    if (!message || isLoading) return;

    // Stop listening when sending (for both manual and conversation mode)
    if (VoiceInteraction.getIsListening()) {
        VoiceInteraction.stopListening();
    }

    // Conversation mode: transition to SENDING state
    if (conversationMode.isActive) {
        try {
            conversationMode.sendMessage();
        } catch (e) {
            console.error('Conversation mode error:', e);
            Notifications.showNotification(e.message, 'error');
            return;
        }
    }

    // Add user message
    addMessage('user', message);
    input.value = '';
    input.style.height = 'auto';

    // Get settings
    const model = document.getElementById('model-select').value;
    const temperature = parseFloat(document.getElementById('temperature').value);
    const maxTokens = parseInt(document.getElementById('max-tokens').value);

    // Build history (exclude system messages and welcome message)
    const history = messages
        .filter(msg => msg.type !== 'system')
        .map(msg => ({
            role: msg.type === 'user' ? 'user' : 'assistant',
            content: msg.content
        }));

    // Show loading
    isLoading = true;
    document.getElementById('loading-indicator').classList.add('active');
    document.getElementById('send-btn').disabled = true;

    // Get provider from dropdown to ensure it's current
    const providerSelect = document.getElementById('provider-select');
    const selectedProvider = providerSelect.value || currentProvider;

    console.log('Sending message with provider:', selectedProvider, 'model:', model);

    const payload = {
        message: message,
        provider: selectedProvider,
        model: model,
        temperature: temperature,
        max_tokens: maxTokens,
        history: history,
        system_prompt: systemPrompt,
        auto_trim: true
    };

    try {
        // Try streaming first
        const streamResponse = await fetch('/api/chat/stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (streamResponse.ok && streamResponse.headers.get('content-type')?.includes('text/event-stream')) {
            // Streaming mode: create empty message bubble and fill it
            const { messageDiv, textEl } = addStreamingMessage();
            let fullResponse = '';

            const reader = streamResponse.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop(); // Keep incomplete line in buffer

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);
                        if (data === '[DONE]') continue;
                        if (data.startsWith('[ERROR]')) {
                            addMessage('system', `Error: ${data.slice(8)}`);
                            continue;
                        }
                        fullResponse += data;
                        textEl.textContent = fullResponse;
                        messageDiv.closest('.chat-container')?.scrollTo(0, 99999);
                    }
                }
            }

            // Finalize the message in our messages array
            messages.push({ type: 'assistant', content: fullResponse, time: new Date().toISOString() });

            // Store for voice replay
            VoiceInteraction.storeLastResponse(fullResponse);

            if (conversationMode.shouldAutoPlay()) {
                conversationMode.receiveResponse();
                VoiceInteraction.autoPlayResponse(fullResponse);
            }

            await saveConversationAuto();
        } else {
            // Fall back to non-streaming endpoint
            const response = await fetch('/api/chat/send', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                const result = await response.json();
                addMessage('assistant', result.response);
                VoiceInteraction.storeLastResponse(result.response);

                if (conversationMode.shouldAutoPlay()) {
                    conversationMode.receiveResponse();
                    VoiceInteraction.autoPlayResponse(result.response);
                }

                updateTokenUsage(result.token_usage);

                if (result.token_usage?.warning) {
                    Notifications.showNotification(result.token_usage.warning, 'warning');
                }
                if (result.trimmed) {
                    Notifications.showNotification(`Auto-trimmed ${result.trimmed} old messages to fit context`, 'success');
                }

                await saveConversationAuto();
            } else {
                const error = await response.json();
                addMessage('system', `Error: ${error.error || 'Failed to send message'}`);
            }
        }
    } catch (error) {
        addMessage('system', `Network error: ${error.message}`);
    } finally {
        isLoading = false;
        document.getElementById('loading-indicator').classList.remove('active');
        document.getElementById('send-btn').disabled = false;
    }
}

function addStreamingMessage() {
    const messagesArea = document.getElementById('messages-area');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';

    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    messageDiv.innerHTML = `
        <div class="message-avatar assistant-avatar">🤖</div>
        <div class="message-content">
            <div class="message-header">
                <span class="message-sender">Assistant</span>
                <span class="message-time">${time}</span>
            </div>
            <div class="message-text streaming"></div>
            <div class="message-actions">
                <button class="btn-msg-action" onclick="copyMessage(this)">📋 Copy</button>
                <button class="btn-play" onclick="playMessage(this)">▶️ Play</button>
                <button class="btn-msg-action" onclick="saveAsPrompt(this)">💾 Save as Prompt</button>
            </div>
        </div>
    `;

    messagesArea.appendChild(messageDiv);
    messagesArea.scrollTop = messagesArea.scrollHeight;

    const textEl = messageDiv.querySelector('.message-text');
    return { messageDiv, textEl };
}

function addMessage(type, content) {
    const messagesArea = document.getElementById('messages-area');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;

    const avatarClass = type === 'user' ? 'user-avatar' :
                       type === 'assistant' ? 'assistant-avatar' : 'system-avatar';
    const avatarIcon = type === 'user' ? '👤' :
                      type === 'assistant' ? '🤖' : 'ℹ️';
    const sender = type === 'user' ? 'You' :
                  type === 'assistant' ? 'Assistant' : 'System';

    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    messageDiv.innerHTML = `
        <div class="message-avatar ${avatarClass}">${avatarIcon}</div>
        <div class="message-content">
            <div class="message-header">
                <span class="message-sender">${sender}</span>
                <span class="message-time">${time}</span>
            </div>
            <div class="message-text">${escapeHtml(content)}</div>
            ${type !== 'system' ? `
            <div class="message-actions">
                <button class="btn-msg-action" onclick="copyMessage(this)">📋 Copy</button>
                ${type === 'assistant' ? `<button class="btn-play" onclick="playMessage(this)">▶️ Play</button>` : ''}
                <button class="btn-msg-action" onclick="saveAsPrompt(this)">💾 Save as Prompt</button>
            </div>
            ` : ''}
        </div>
    `;

    messagesArea.appendChild(messageDiv);
    messagesArea.scrollTop = messagesArea.scrollHeight;

    messages.push({ type, content, time: new Date().toISOString() });

    // Update regenerate button state and all metadata
    updateRegenerateButton();
    updateConversationMetadata();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function clearChat() {
    if (messages.length <= 1) return; // Don't clear if only welcome message

    if (confirm('Are you sure you want to clear this chat?')) {
        const messagesArea = document.getElementById('messages-area');
        messagesArea.innerHTML = '';
        messages = [];
        // Re-add welcome message
        updateWelcomeTime();
        const welcomeMsg = messagesArea.querySelector('.message.system');
        if (welcomeMsg) {
            messages.push({
                type: 'system',
                content: welcomeMsg.querySelector('.message-text').textContent,
                time: new Date().toISOString()
            });
        }
        Notifications.showNotification('Chat cleared successfully', 'success');
    }
}

function exportChat() {
    if (messages.length <= 1) {
        Notifications.showNotification('No messages to export', 'error');
        return;
    }

    let exportText = 'Chat Export - Prompt Manager\n';
    exportText += '='.repeat(50) + '\n\n';

    messages.forEach(msg => {
        const time = new Date(msg.time).toLocaleString();
        const sender = msg.type === 'user' ? 'You' :
                      msg.type === 'assistant' ? 'Assistant' : 'System';
        exportText += `[${time}] ${sender}:\n${msg.content}\n\n`;
    });

    const blob = new Blob([exportText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-${new Date().toISOString().slice(0, 10)}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    Notifications.showNotification('Chat exported successfully', 'success');
}

function copyMessage(button) {
    const messageText = button.closest('.message-content').querySelector('.message-text').textContent;
    navigator.clipboard.writeText(messageText).then(() => {
        Notifications.showNotification('Message copied to clipboard', 'success');
    });
}

async function saveAsPrompt(button) {
    const messageText = button.closest('.message-content').querySelector('.message-text').textContent;

    // Prompt for a name
    const name = prompt('Enter a name for this prompt:');
    if (!name) return;

    try {
        const response = await fetch('/api/prompts', {  // Changed from /api/prompt to /api/prompts
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name,
                text: messageText,  // Changed from 'content' to 'text' to match API
                category: 'chat-saved',
                tags: ['chat']
            })
        });

        if (response.ok) {
            Notifications.showNotification('Prompt saved successfully!', 'success');
        } else {
            const error = await response.json();
            Notifications.showNotification(`Failed to save: ${error.error}`, 'error');
        }
    } catch (error) {
        Notifications.showNotification(`Error saving prompt: ${error.message}`, 'error');
    }
}

// Prompts Library Modal Functions
let allPrompts = [];

async function openPromptLibrary() {
    const modal = document.getElementById('prompts-modal');
    modal.style.display = 'flex';

    // Load prompts
    await loadPromptsList();
}

function closePromptsModal() {
    const modal = document.getElementById('prompts-modal');
    modal.style.display = 'none';
}

async function loadPromptsList() {
    const listContainer = document.getElementById('prompts-list');

    try {
        const response = await fetch('/api/prompts');

        if (response.ok) {
            const data = await response.json();
            allPrompts = data.prompts || [];

            if (allPrompts.length === 0) {
                listContainer.innerHTML = `
                    <div style="text-align: center; color: #718096; padding: 40px;">
                        <div style="font-size: 48px; margin-bottom: 16px;">📭</div>
                        <div style="font-size: 18px; margin-bottom: 8px;">No saved prompts yet</div>
                        <div style="font-size: 14px;">Prompts you save will appear here!</div>
                    </div>
                `;
                return;
            }

            // Render prompts
            renderPromptsList(allPrompts);
        } else {
            listContainer.innerHTML = `
                <div style="text-align: center; color: #e53e3e; padding: 40px;">
                    <div style="font-size: 48px; margin-bottom: 16px;">⚠️</div>
                    <div>Failed to load prompts</div>
                </div>
            `;
        }
    } catch (error) {
        listContainer.innerHTML = `
            <div style="text-align: center; color: #e53e3e; padding: 40px;">
                <div style="font-size: 48px; margin-bottom: 16px;">⚠️</div>
                <div>Error: ${error.message}</div>
            </div>
        `;
    }
}

function renderPromptsList(prompts) {
    const listContainer = document.getElementById('prompts-list');

    listContainer.innerHTML = prompts.map(prompt => `
        <div style="border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; margin-bottom: 12px; background: white; transition: all 0.2s ease;"
             onmouseover="this.style.background='#f7fafc'; this.style.borderColor='#cbd5e0';"
             onmouseout="this.style.background='white'; this.style.borderColor='#e2e8f0';">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                <div>
                    <div style="font-weight: 600; color: #1a202c; font-size: 16px; margin-bottom: 4px;">${prompt.name || 'Untitled'}</div>
                    ${prompt.category ? `<span style="display: inline-block; padding: 4px 12px; background: #edf2f7; color: #4a5568; border-radius: 12px; font-size: 12px; font-weight: 500;">📁 ${prompt.category}</span>` : ''}
                </div>
            </div>
            <div style="color: #718096; font-size: 14px; line-height: 1.6; margin-bottom: 12px; max-height: 60px; overflow: hidden; text-overflow: ellipsis;">
                ${(prompt.text || '').substring(0, 150)}${prompt.text && prompt.text.length > 150 ? '...' : ''}
            </div>
            <div style="display: flex; gap: 8px;">
                <button onclick="insertPrompt('${prompt.id}')"
                        style="flex: 1; padding: 8px 16px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 500; font-size: 13px;">
                    ✏️ Insert
                </button>
                <button onclick="viewPromptDetails('${prompt.id}')"
                        style="padding: 8px 16px; background: #f7fafc; color: #4a5568; border: 1px solid #e2e8f0; border-radius: 8px; cursor: pointer; font-weight: 500; font-size: 13px;">
                    👁️ View
                </button>
            </div>
        </div>
    `).join('');
}

function filterPrompts() {
    const searchTerm = document.getElementById('prompt-search').value.toLowerCase();

    if (!searchTerm) {
        renderPromptsList(allPrompts);
        return;
    }

    const filtered = allPrompts.filter(prompt =>
        (prompt.name && prompt.name.toLowerCase().includes(searchTerm)) ||
        (prompt.text && prompt.text.toLowerCase().includes(searchTerm)) ||
        (prompt.category && prompt.category.toLowerCase().includes(searchTerm))
    );

    renderPromptsList(filtered);
}

function insertPrompt(promptId) {
    const prompt = allPrompts.find(p => p.id === promptId);
    if (prompt && prompt.text) {
        const input = document.getElementById('chat-input');
        input.value = prompt.text;
        input.style.height = 'auto';
        input.style.height = input.scrollHeight + 'px';
        input.focus();
        closePromptsModal();
        Notifications.showNotification(`Inserted: ${prompt.name}`, 'success');
    }
}

function viewPromptDetails(promptId) {
    const prompt = allPrompts.find(p => p.id === promptId);
    if (prompt) {
        const details = `
Name: ${prompt.name}
Category: ${prompt.category || 'None'}

Text:
${prompt.text || 'No text'}

Created: ${prompt.created_at ? new Date(prompt.created_at).toLocaleString() : 'Unknown'}
        `.trim();

        alert(details);
    }
}

function saveChatHistory() {
    localStorage.setItem('chat_history', JSON.stringify(messages));
}

function loadChatHistory() {
    const saved = localStorage.getItem('chat_history');
    if (saved) {
        try {
            messages = JSON.parse(saved);
            // Reload messages into UI if needed
        } catch (e) {
            console.error('Failed to load chat history:', e);
        }
    }
}

function updateWelcomeTime() {
    const timeEl = document.getElementById('welcome-time');
    if (timeEl) {
        timeEl.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
}

// Notification function now provided by Notifications module
// All calls to showNotification use Notifications.showNotification via dependency injection

async function loadSystemPrompt() {
    try {
        const response = await fetch('/api/settings/system-prompt');
        if (response.ok) {
            const data = await response.json();
            systemPrompt = data.prompt;
        }
    } catch (error) {
        console.error('Error loading system prompt:', error);
    }
}

function getContextLimit(model) {
    /**Get context limit for a model.*/
    const limits = {
        'gpt-4-turbo-preview': 128000,
        'gpt-4': 8192,
        'gpt-3.5-turbo': 4096,
        'gpt-3.5-turbo-16k': 16384
    };
    return limits[model] || 4096;
}

function updateTokenUsage(tokenUsage) {
    const percentage = tokenUsage.percentage || 0;
    const bar = document.getElementById('token-bar');
    const percentageEl = document.getElementById('token-percentage');
    const warningEl = document.getElementById('token-warning');

    // Update percentage display
    percentageEl.textContent = `${percentage}%`;
    bar.style.width = `${percentage}%`;

    // Update bar color class
    bar.className = 'token-bar-fill';
    if (percentage < 50) {
        bar.classList.add('low');
    } else if (percentage < 80) {
        bar.classList.add('medium');
    } else {
        bar.classList.add('high');
    }

    // Show warning if high
    if (tokenUsage.warning) {
        warningEl.textContent = tokenUsage.warning;
        warningEl.style.display = 'inline';
    } else {
        warningEl.style.display = 'none';
    }
}

async function saveConversationAuto() {
    if (messages.length <= 1) return; // Don't save empty chats

    const model = document.getElementById('model-select').value;

    const conversationData = {
        id: currentConversationId,
        messages: messages.filter(m => m.type !== 'system').map(m => ({
            role: m.type === 'user' ? 'user' : 'assistant',
            content: m.content
        })),
        model: model,
        system_prompt: systemPrompt
    };

    try {
        const response = await fetch('/api/conversations/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(conversationData)
        });

        if (response.ok) {
            const result = await response.json();
            currentConversationId = result.id;
        }
    } catch (error) {
        console.error('Error saving conversation:', error);
    }
}

async function loadConversation(conversationId) {
    try {
        const response = await fetch(`/api/conversations/load/${conversationId}`);

        if (response.ok) {
            const conversation = await response.json();

            // Clear current messages
            messages = [];
            document.getElementById('messages-area').innerHTML = '';

            // Load messages
            conversation.messages.forEach(msg => {
                addMessage(msg.role, msg.content);
            });

            // Set conversation ID
            currentConversationId = conversation.id;

            // Update model if stored
            if (conversation.model) {
                document.getElementById('model-select').value = conversation.model;
            }

            // Recalculate token usage for loaded conversation
            const model = conversation.model || document.getElementById('model-select').value;
            const estimatedTokens = messages.reduce((total, msg) => {
                return total + Math.ceil(msg.content.length / 4);
            }, 0);

            // Update token display
            updateTokenUsage({
                prompt_tokens: estimatedTokens,
                total_tokens: estimatedTokens,
                context_limit: getContextLimit(model),
                percentage: Math.min(100, (estimatedTokens / getContextLimit(model)) * 100)
            });

            Notifications.showNotification('Conversation loaded', 'success');
        }
    } catch (error) {
        Notifications.showNotification('Error loading conversation', 'error');
    }
}

// History Modal Functions
async function openHistoryModal() {
    const modal = document.getElementById('history-modal');
    modal.style.display = 'flex';

    // Load conversations
    await loadConversationsList();
}

function closeHistoryModal() {
    const modal = document.getElementById('history-modal');
    modal.style.display = 'none';
}

async function loadConversationsList() {
    const listContainer = document.getElementById('history-list');

    try {
        const response = await fetch('/api/conversations/list?sort=date');

        if (response.ok) {
            const data = await response.json();
            const conversations = data.conversations || [];

            if (conversations.length === 0) {
                listContainer.innerHTML = `
                    <div style="text-align: center; color: #718096; padding: 40px;">
                        <div style="font-size: 48px; margin-bottom: 16px;">📭</div>
                        <div style="font-size: 18px; margin-bottom: 8px;">No conversations yet</div>
                        <div style="font-size: 14px;">Start chatting to create your first conversation!</div>
                    </div>
                `;
                return;
            }

            // Render conversation list
            listContainer.innerHTML = conversations.map(conv => `
                <div style="border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; margin-bottom: 12px; cursor: pointer; transition: all 0.2s ease; background: white;"
                     onmouseover="this.style.background='#f7fafc'; this.style.borderColor='#cbd5e0';"
                     onmouseout="this.style.background='white'; this.style.borderColor='#e2e8f0';"
                     onclick="loadConversationFromHistory('${conv.id}')">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                        <div style="font-weight: 600; color: #1a202c; font-size: 16px; flex: 1;">${conv.title || 'Untitled Conversation'}</div>
                        <button onclick="event.stopPropagation(); deleteConversationFromHistory('${conv.id}')"
                                style="background: none; border: none; color: #e53e3e; cursor: pointer; font-size: 18px; padding: 0 8px;"
                                title="Delete conversation">🗑️</button>
                    </div>
                    <div style="display: flex; gap: 16px; font-size: 13px; color: #718096;">
                        <span>💬 ${conv.message_count || 0} messages</span>
                        <span>📅 ${formatDate(conv.updated_at || conv.created_at)}</span>
                        ${conv.model ? `<span>🤖 ${conv.model}</span>` : ''}
                    </div>
                </div>
            `).join('');
        } else {
            listContainer.innerHTML = `
                <div style="text-align: center; color: #e53e3e; padding: 40px;">
                    <div style="font-size: 48px; margin-bottom: 16px;">⚠️</div>
                    <div>Failed to load conversations</div>
                </div>
            `;
        }
    } catch (error) {
        listContainer.innerHTML = `
            <div style="text-align: center; color: #e53e3e; padding: 40px;">
                <div style="font-size: 48px; margin-bottom: 16px;">⚠️</div>
                <div>Error: ${error.message}</div>
            </div>
        `;
    }
}

async function loadConversationFromHistory(conversationId) {
    closeHistoryModal();
    await loadConversation(conversationId);
}

async function deleteConversationFromHistory(conversationId) {
    if (!confirm('Are you sure you want to delete this conversation?')) {
        return;
    }

    try {
        const response = await fetch(`/api/conversations/delete/${conversationId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            Notifications.showNotification('Conversation deleted', 'success');
            await loadConversationsList(); // Reload list
        } else {
            Notifications.showNotification('Failed to delete conversation', 'error');
        }
    } catch (error) {
        Notifications.showNotification('Error deleting conversation', 'error');
    }
}

async function deleteAllConversations() {
    if (!confirm('⚠️ Are you sure you want to delete ALL conversations? This cannot be undone!')) {
        return;
    }

    // Double confirmation for destructive action
    if (!confirm('This will permanently delete all your conversation history. Continue?')) {
        return;
    }

    try {
        const response = await fetch('/api/conversations/list');
        if (response.ok) {
            const data = await response.json();
            const conversations = data.conversations || [];

            if (conversations.length === 0) {
                Notifications.showNotification('No conversations to delete', 'success');
                return;
            }

            // Delete all conversations
            let deleted = 0;
            for (const conv of conversations) {
                const delResponse = await fetch(`/api/conversations/delete/${conv.id}`, {
                    method: 'DELETE'
                });
                if (delResponse.ok) deleted++;
            }

            Notifications.showNotification(`Deleted ${deleted} conversation(s)`, 'success');
            await loadConversationsList(); // Reload list
        } else {
            Notifications.showNotification('Failed to load conversations', 'error');
        }
    } catch (error) {
        Notifications.showNotification('Error deleting conversations', 'error');
    }
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;

    return date.toLocaleDateString();
}

// Regenerate Last Response
async function regenerateLastResponse() {
    if (messages.length < 2 || isLoading) return;

    // Find the last user message
    let lastUserMessage = null;
    for (let i = messages.length - 1; i >= 0; i--) {
        if (messages[i].type === 'user') {
            lastUserMessage = messages[i];
            break;
        }
    }

    if (!lastUserMessage) {
        Notifications.showNotification('No user message to regenerate from', 'error');
        return;
    }

    // Remove all messages after the last user message (keep the user message)
    const userMessageIndex = messages.indexOf(lastUserMessage);
    messages = messages.slice(0, userMessageIndex + 1);

    // Re-render messages
    const messagesArea = document.getElementById('messages-area');
    messagesArea.innerHTML = '';
    messages.forEach(msg => {
        addMessage(msg.type, msg.content);
    });

    // Resend the last user message
    await sendMessage(lastUserMessage.content);
}

// Helper to update regenerate button state
function updateRegenerateButton() {
    const hasUserMessages = messages.some(m => m.type === 'user');
    document.getElementById('regenerate-btn').disabled = !hasUserMessages;
}

// Helper to update message count display
function updateMessageCount() {
    const count = messages.filter(m => m.type !== 'system').length;
    document.getElementById('msg-count').textContent = count;
}

function updateConversationMetadata() {
    // Update message count
    updateMessageCount();

    // Update model name
    const modelSelect = document.getElementById('model-select');
    const modelOption = modelSelect.options[modelSelect.selectedIndex];
    document.getElementById('model-name').textContent = modelOption.text.split(' (')[0]; // Get just the name

    // Update conversation time (when conversation started)
    if (!window.conversationStartTime) {
        window.conversationStartTime = new Date();
    }
    const elapsed = Math.floor((new Date() - window.conversationStartTime) / 60000); // minutes
    document.getElementById('conv-time').textContent = elapsed > 0 ? `${elapsed}m` : 'Just now';

    // Update last message time
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const mins = String(now.getMinutes()).padStart(2, '0');
    document.getElementById('last-msg-time').textContent = `${hours}:${mins}`;
}

// Save Conversation Modal Functions
function openSaveConvModal() {
    if (messages.length === 0 || messages.filter(m => m.type !== 'system').length === 0) {
        Notifications.showNotification('No messages to save', 'error');
        return;
    }

    const modal = document.getElementById('save-conv-modal');
    const input = document.getElementById('conv-title-input');

    // Auto-suggest title from first user message
    const firstUserMsg = messages.find(m => m.type === 'user');
    if (firstUserMsg) {
        const suggestedTitle = firstUserMsg.content.substring(0, 50);
        input.value = suggestedTitle + (firstUserMsg.content.length > 50 ? '...' : '');
    }

    modal.style.display = 'flex';
    setTimeout(() => input.focus(), 100);
}

function closeSaveConvModal() {
    const modal = document.getElementById('save-conv-modal');
    modal.style.display = 'none';
}

async function saveConversationWithTitle() {
    const title = document.getElementById('conv-title-input').value.trim();

    if (!title) {
        Notifications.showNotification('Please enter a title', 'error');
        return;
    }

    const model = document.getElementById('model-select').value;

    const conversationData = {
        id: currentConversationId,
        title: title,
        messages: messages.filter(m => m.type !== 'system').map(m => ({
            role: m.type === 'user' ? 'user' : 'assistant',
            content: m.content
        })),
        model: model,
        system_prompt: systemPrompt
    };

    try {
        const response = await fetch('/api/conversations/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(conversationData)
        });

        if (response.ok) {
            const result = await response.json();
            currentConversationId = result.id;
            closeSaveConvModal();
            Notifications.showNotification(`Saved: ${title}`, 'success');
        } else {
            Notifications.showNotification('Failed to save conversation', 'error');
        }
    } catch (error) {
        Notifications.showNotification('Error saving conversation', 'error');
    }
}

// Voice Settings Modal Functions
let voiceSettingsPanelCreated = false;

function openVoiceSettingsModal() {
    const modal = document.getElementById('voice-settings-modal');
    const container = document.getElementById('voice-settings-container');

    // Create the settings panel if not already created
    if (!voiceSettingsPanelCreated) {
        const panel = VoiceSettings.createSettingsPanel();

        // Add close button to panel
        const closeBtn = document.createElement('button');
        closeBtn.className = 'voice-settings-close';
        closeBtn.innerHTML = '×';
        closeBtn.onclick = closeVoiceSettingsModal;
        panel.insertBefore(closeBtn, panel.firstChild);

        container.appendChild(panel);
        voiceSettingsPanelCreated = true;
    }

    modal.classList.remove('hidden');

    // Close on backdrop click
    modal.onclick = function(e) {
        if (e.target === modal) {
            closeVoiceSettingsModal();
        }
    };
}

function closeVoiceSettingsModal() {
    const modal = document.getElementById('voice-settings-modal');
    modal.classList.add('hidden');
}

// Module Wrapper Functions (for HTML onclick handlers and event listeners)
// Actual implementations are in modules/

function toggleVoiceInput() {
    VoiceInteraction.toggleVoiceInput();
}

function playMessage(button) {
    VoiceInteraction.playMessage(button);
}

function toggleConversationMode() {
    ConversationMode.toggleConversationMode();
}

// Expose functions to global scope for inline onclick handlers in HTML
// These functions are called from onclick attributes and need to be on window object
window.togglePanel = togglePanel;
window.deleteAllConversations = deleteAllConversations;
window.closeHistoryModal = closeHistoryModal;
window.closePromptsModal = closePromptsModal;
window.closeSaveConvModal = closeSaveConvModal;
window.saveConversationWithTitle = saveConversationWithTitle;
window.openHistoryModal = openHistoryModal;
window.copyMessage = copyMessage;
window.saveAsPrompt = saveAsPrompt;
window.filterPrompts = filterPrompts;
window.insertPrompt = insertPrompt;
window.viewPromptDetails = viewPromptDetails;
window.saveChatHistory = saveChatHistory;
window.loadConversationFromHistory = loadConversationFromHistory;
window.deleteConversationFromHistory = deleteConversationFromHistory;
window.playMessage = playMessage;
window.openVoiceSettingsModal = openVoiceSettingsModal;
window.closeVoiceSettingsModal = closeVoiceSettingsModal;
