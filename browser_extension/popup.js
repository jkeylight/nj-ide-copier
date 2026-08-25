/**
 * Popup script for NJ IDE Copier.
 * Handles UI interactions and server status.
 */

document.addEventListener('DOMContentLoaded', async () => {
    await updateStatus();
    await detectPlatform();

    // Button click handlers
    document.getElementById('copyFullChat').addEventListener('click', () => {
        sendAction('copyFullChat');
    });

    document.getElementById('copyLastResponse').addEventListener('click', () => {
        sendAction('copyLastResponse');
    });

    document.getElementById('copyAllCode').addEventListener('click', () => {
        sendAction('copyAllCode');
    });

    document.getElementById('exportMarkdown').addEventListener('click', () => {
        sendAction('exportMarkdown');
    });

    // IDE selection
    document.getElementById('ideSelect').addEventListener('change', (e) => {
        chrome.storage.sync.set({ defaultIde: e.target.value });
    });

    // Load saved IDE preference
    chrome.storage.sync.get(['defaultIde'], (result) => {
        if (result.defaultIde) {
            document.getElementById('ideSelect').value = result.defaultIde;
        }
    });
});

function sendAction(action) {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs[0]) {
            chrome.tabs.sendMessage(tabs[0].id, { action: action }, (response) => {
                if (chrome.runtime.lastError) {
                    // Content script not available on this page
                    showPlatformStatus('Visit an AI chat site to use');
                }
            });
        }
    });
}

async function detectPlatform() {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs[0]) {
            const url = tabs[0].url || '';
            let platform = 'Unknown';

            if (url.includes('chatgpt.com') || url.includes('chat.openai.com')) platform = 'ChatGPT';
            else if (url.includes('claude.ai')) platform = 'Claude';
            else if (url.includes('deepseek.com')) platform = 'DeepSeek';
            else if (url.includes('tongyi.aliyun.com') || url.includes('qianwen.aliyun.com')) platform = 'Qwen';
            else if (url.includes('gemini.google.com')) platform = 'Gemini';
            else if (url.includes('kimi.moonshot.cn')) platform = 'Kimi';
            else if (url.includes('chatglm.cn')) platform = 'ChatGLM';
            else if (url.includes('huggingface.co/chat')) platform = 'HuggingChat';
            else if (url.includes('poe.com')) platform = 'Poe';
            else if (url.includes('perplexity.ai')) platform = 'Perplexity';
            else if (url.includes('you.com')) platform = 'You.com';

            document.getElementById('currentPlatform').textContent = platform;

            if (platform === 'Unknown') {
                showPlatformStatus('Visit an AI chat site to use');
            }
        }
    });
}

function showPlatformStatus(msg) {
    document.getElementById('currentPlatform').textContent = msg;
    document.getElementById('currentPlatform').style.color = '#FF9800';
}

async function updateStatus() {
    try {
        const response = await fetch('http://localhost:8765/status');
        const status = await response.json();

        document.getElementById('serverStatus').textContent = 'Running';
        document.getElementById('serverStatus').style.color = '#4CAF50';

        document.getElementById('activeIDE').textContent = status.active_ide || 'None detected';

        // Update IDE selector with detected IDEs
        const select = document.getElementById('ideSelect');
        if (status.ides) {
            status.ides.forEach(ide => {
                const option = document.createElement('option');
                option.value = ide.id;
                option.textContent = ide.name;
                select.appendChild(option);
            });
        }
    } catch (error) {
        document.getElementById('serverStatus').textContent = 'Not Running';
        document.getElementById('serverStatus').style.color = '#f44336';
        document.getElementById('activeIDE').textContent = 'Start server first';
    }
}

// Auto-refresh every 5 seconds
setInterval(updateStatus, 5000);
