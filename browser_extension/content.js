/**
 * NJ IDE Copier - Content script for AI chat extraction.
 * Version 2.0 - Updated with full export and stats features
 */

function detectPlatform() {
    const host = window.location.hostname;

    if (host.includes('chat.openai.com') || host.includes('chatgpt.com')) {
        return {
            name: 'ChatGPT',
            codeSelector: 'pre code, div[class*="code"] pre',
            messageSelector: '[data-message-author-role], [class*="message"]',
            contentSelector: '.markdown, [class*="message-content"]',
        };
    }
    if (host.includes('claude.ai')) {
        return {
            name: 'Claude',
            codeSelector: 'pre code, .code-block code',
            messageSelector: '[data-is-streaming], [class*="message"]',
            contentSelector: '.font-claude-message, [class*="message-content"]',
        };
    }
    if (host.includes('deepseek.com')) {
        return {
            name: 'DeepSeek',
            codeSelector: 'pre code',
            messageSelector: '[class*="message"], [class*="chat-message"]',
            contentSelector: '[class*="message-content"], [class*="content"]',
        };
    }
    if (host.includes('tongyi.aliyun.com') || host.includes('qianwen.aliyun.com')) {
        return {
            name: 'Qwen',
            codeSelector: 'pre code, .code-block code',
            messageSelector: '[class*="message-item"], [class*="chat-item"]',
            contentSelector: '[class*="message-content"]',
        };
    }
    if (host.includes('kimi.moonshot.cn')) {
        return {
            name: 'Kimi',
            codeSelector: 'pre code, .code-block code',
            messageSelector: '[class*="message"], [class*="msg"]',
            contentSelector: '[class*="content"]',
        };
    }
    if (host.includes('chatglm.cn')) {
        return {
            name: 'ChatGLM',
            codeSelector: 'pre code, .code-block code',
            messageSelector: '[class*="message"]',
            contentSelector: '[class*="content"]',
        };
    }
    if (host.includes('gemini.google.com')) {
        return {
            name: 'Gemini',
            codeSelector: 'pre code, code-block code',
            messageSelector: '[class*="message"], .model-response-text',
            contentSelector: '.model-response-text, [class*="message-content"]',
        };
    }
    if (host.includes('huggingface.co/chat')) {
        return {
            name: 'HuggingChat',
            codeSelector: 'pre code',
            messageSelector: '[class*="message"]',
            contentSelector: '[class*="message-content"], .prose',
        };
    }
    if (host.includes('poe.com')) {
        return {
            name: 'Poe',
            codeSelector: 'pre code',
            messageSelector: '[class*="Message"]',
            contentSelector: '[class*="MessageContent"]',
        };
    }
    if (host.includes('perplexity.ai')) {
        return {
            name: 'Perplexity',
            codeSelector: 'pre code',
            messageSelector: '[class*="prose"], [class*="message"]',
            contentSelector: '.prose, [class*="message-content"]',
        };
    }
    if (host.includes('you.com')) {
        return {
            name: 'You.com',
            codeSelector: 'pre code',
            messageSelector: '[class*="message"]',
            contentSelector: '[class*="message-content"]',
        };
    }
    if (host.includes('arena.ai')) {
        return {
            name: 'Arena.ai',
            codeSelector: 'pre code, [data-testid*="code"] code, .code-block code',
            messageSelector: '[class*="message"], [class*="chat"], article, [role="article"]',
            contentSelector: '[class*="content"], [class*="message-content"], .prose',
        };
    }

    return {
        name: 'Unknown',
        codeSelector: 'pre code',
        messageSelector: '[class*="message"], [role="article"]',
        contentSelector: '[class*="message-content"], [class*="content"], .markdown',
    };
}

class NJIDECopier {
    constructor() {
        this.platform = detectPlatform();
        this.lastCode = '';
        this.lastLanguage = '';
        this.allCodeBlocks = [];
        this.serverUrl = 'http://localhost:8765';
        this.init();
    }

    init() {
        console.log(`[NJ IDE Copier v2.0] Platform: ${this.platform.name}`);
        this.setupFloatingUI();
        this.setupMessageListener();
        this.observeCodeBlocks();
        this.checkServerStatus();
    }

    async checkServerStatus() {
        try {
            const response = await fetch(`${this.serverUrl}/status`);
            if (response.ok) {
                this.updateStatusIndicator('connected');
            } else {
                this.updateStatusIndicator('error');
            }
        } catch (err) {
            this.updateStatusIndicator('disconnected');
        }
    }

    updateStatusIndicator(status) {
        const indicator = document.getElementById('nj-server-status');
        if (indicator) {
            indicator.className = `status-indicator ${status}`;
            indicator.title = `Server: ${status}`;
        }
    }

    setupFloatingUI() {
        if (document.getElementById('nj-ide-copier-floating')) return;

        const container = document.createElement('div');
        container.id = 'nj-ide-copier-floating';
        container.innerHTML = `
            <div class="nj-toggle-btn" id="nj-toggle-btn">
                <span class="nj-toggle-icon">🎯</span>
                <span class="nj-toggle-text">NJ IDE Copier</span>
            </div>
            
            <div class="nj-panel" id="nj-panel" style="display: none;">
                <div class="nj-header">
                    <span id="nj-server-status" class="status-indicator disconnected" title="Server Status"></span>
                    <span class="nj-title">NJ IDE Copier v2.0</span>
                    <span class="nj-platform">${this.platform.name}</span>
                    <button class="nj-close-btn" id="nj-close-btn">×</button>
                </div>
                
                <div class="nj-section">
                    <div class="nj-section-title">📋 Quick Actions</div>
                    <button class="nj-btn nj-btn-primary" data-action="copy-last">
                        <span class="btn-icon">📝</span>
                        <span class="btn-text">Copy Last Code</span>
                    </button>
                    <button class="nj-btn nj-btn-secondary" data-action="copy-all">
                        <span class="btn-icon">📚</span>
                        <span class="btn-text">Copy All Code</span>
                    </button>
                </div>
                
                <div class="nj-section">
                    <div class="nj-section-title">💾 Export</div>
                    <button class="nj-btn nj-btn-export" data-action="export-chat">
                        <span class="btn-icon">📄</span>
                        <span class="btn-text">Export Full Chat</span>
                    </button>
                    <button class="nj-btn nj-btn-export" data-action="export-markdown">
                        <span class="btn-icon">📝</span>
                        <span class="btn-text">Export as Markdown</span>
                    </button>
                </div>
                
                <div class="nj-section">
                    <div class="nj-section-title">📊 Statistics</div>
                    <button class="nj-btn nj-btn-stats" data-action="show-stats">
                        <span class="btn-icon">📈</span>
                        <span class="btn-text">View Error Stats</span>
                    </button>
                    <button class="nj-btn nj-btn-stats" data-action="show-exports">
                        <span class="btn-icon">📂</span>
                        <span class="btn-text">List Exports</span>
                    </button>
                </div>
                
                <div class="nj-status-bar">
                    <span class="nj-status-text">Server: <span id="nj-status-text">Checking...</span></span>
                </div>
            </div>
        `;

        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            #nj-ide-copier-floating {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 999999;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }
            
            .nj-toggle-btn {
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 10px 16px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 25px;
                color: white;
                cursor: pointer;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                transition: all 0.3s;
                font-size: 14px;
                font-weight: 600;
            }
            
            .nj-toggle-btn:hover {
                transform: scale(1.05);
                box-shadow: 0 6px 20px rgba(0,0,0,0.4);
            }
            
            .nj-toggle-icon {
                font-size: 18px;
            }
            
            .nj-panel {
                position: absolute;
                top: 50px;
                right: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 16px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                min-width: 280px;
                color: white;
                overflow: hidden;
                animation: slideDown 0.3s ease;
            }
            
            @keyframes slideDown {
                from {
                    opacity: 0;
                    transform: translateY(-10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .nj-close-btn {
                background: rgba(255,255,255,0.2);
                border: none;
                color: white;
                font-size: 18px;
                width: 24px;
                height: 24px;
                border-radius: 50%;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.2s;
            }
            
            .nj-close-btn:hover {
                background: rgba(255,255,255,0.3);
                transform: scale(1.1);
            }
            
            .nj-header {
                background: rgba(0,0,0,0.2);
                padding: 12px 16px;
                display: flex;
                align-items: center;
                gap: 10px;
                border-bottom: 1px solid rgba(255,255,255,0.1);
            }
            
            .status-indicator {
                width: 10px;
                height: 10px;
                border-radius: 50%;
                background: #666;
                animation: pulse 2s infinite;
            }
            
            .status-indicator.connected {
                background: #4CAF50;
            }
            
            .status-indicator.disconnected {
                background: #f44336;
            }
            
            .status-indicator.error {
                background: #FF9800;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            
            .nj-title {
                font-weight: 700;
                font-size: 14px;
                flex: 1;
            }
            
            .nj-platform {
                font-size: 11px;
                opacity: 0.8;
                background: rgba(255,255,255,0.2);
                padding: 2px 8px;
                border-radius: 10px;
            }
            
            .nj-section {
                padding: 12px 16px;
                border-bottom: 1px solid rgba(255,255,255,0.1);
            }
            
            .nj-section-title {
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                opacity: 0.8;
                margin-bottom: 10px;
            }
            
            .nj-btn {
                width: 100%;
                padding: 10px 14px;
                margin-bottom: 8px;
                background: rgba(255,255,255,0.15);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 8px;
                color: white;
                cursor: pointer;
                font-size: 13px;
                display: flex;
                align-items: center;
                gap: 10px;
                transition: all 0.2s;
                text-align: left;
            }
            
            .nj-btn:last-child {
                margin-bottom: 0;
            }
            
            .nj-btn:hover {
                background: rgba(255,255,255,0.25);
                transform: translateX(4px);
            }
            
            .nj-btn:active {
                transform: translateX(2px);
            }
            
            .nj-btn-primary {
                background: #4CAF50;
                border-color: #4CAF50;
            }
            
            .nj-btn-primary:hover {
                background: #45a049;
            }
            
            .nj-btn-secondary {
                background: #2196F3;
                border-color: #2196F3;
            }
            
            .nj-btn-secondary:hover {
                background: #1976D2;
            }
            
            .nj-btn-export {
                background: #9C27B0;
                border-color: #9C27B0;
            }
            
            .nj-btn-export:hover {
                background: #7B1FA2;
            }
            
            .nj-btn-stats {
                background: #FF9800;
                border-color: #FF9800;
            }
            
            .nj-btn-stats:hover {
                background: #F57C00;
            }
            
            .btn-icon {
                font-size: 16px;
                width: 24px;
                text-align: center;
            }
            
            .btn-text {
                flex: 1;
            }
            
            .nj-status-bar {
                padding: 8px 16px;
                background: rgba(0,0,0,0.2);
                font-size: 11px;
                text-align: center;
            }
            
            .nj-status-text {
                opacity: 0.9;
            }
        `;

        document.head.appendChild(style);
        document.body.appendChild(container);

        // Toggle button click handler
        const toggleBtn = document.getElementById('nj-toggle-btn');
        const panel = document.getElementById('nj-panel');
        const closeBtn = document.getElementById('nj-close-btn');
        
        toggleBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
        });
        
        closeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            panel.style.display = 'none';
        });
        
        // Close panel when clicking outside
        document.addEventListener('click', (e) => {
            if (!container.contains(e.target)) {
                panel.style.display = 'none';
            }
        });

        // Add click handlers for buttons
        container.querySelectorAll('.nj-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = btn.dataset.action;
                this.handleAction(action);
            });
        });

        // Update status text
        this.updateStatusText();
    }

    async updateStatusText() {
        const statusText = document.getElementById('nj-status-text');
        if (!statusText) return;

        try {
            const response = await fetch(`${this.serverUrl}/status`);
            if (response.ok) {
                statusText.textContent = 'Connected';
                statusText.style.color = '#4CAF50';
            }
        } catch (err) {
            statusText.textContent = 'Disconnected';
            statusText.style.color = '#f44336';
        }
    }

    async handleAction(action) {
        switch(action) {
            case 'copy-last':
                await this.copyLastResponse();
                break;
            case 'copy-all':
                await this.copyAllCode();
                break;
            case 'export-chat':
                await this.exportFullChat();
                break;
            case 'export-markdown':
                await this.exportMarkdown();
                break;
            case 'show-stats':
                await this.showErrorStats();
                break;
            case 'show-exports':
                await this.showExports();
                break;
        }
    }

    setupMessageListener() {
        chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
            if (request.action === 'copyFullChat') {
                this.copyFullChat();
                sendResponse({ status: 'done' });
            } else if (request.action === 'copyLastResponse') {
                this.copyLastResponse();
                sendResponse({ status: 'done' });
            } else if (request.action === 'copyAllCode') {
                this.copyAllCode();
                sendResponse({ status: 'done' });
            } else if (request.action === 'exportMarkdown') {
                this.exportMarkdown();
                sendResponse({ status: 'done' });
            } else if (request.action === 'getLastCode') {
                sendResponse({ code: this.lastCode, language: this.lastLanguage });
            } else if (request.action === 'exportChat') {
                this.exportFullChat();
                sendResponse({ status: 'done' });
            } else if (request.action === 'showErrorStats') {
                this.showErrorStats();
                sendResponse({ status: 'done' });
            } else if (request.action === 'listExports') {
                this.showExports();
                sendResponse({ status: 'done' });
            }
            return true;
        });
    }

    observeCodeBlocks() {
        this.extractCodeBlocks();
        const observer = new MutationObserver(() => this.extractCodeBlocks());
        observer.observe(document.body, { childList: true, subtree: true });
    }

    extractCodeBlocks() {
        const codeElements = document.querySelectorAll(this.platform.codeSelector);
        this.allCodeBlocks = [];

        codeElements.forEach(el => {
            const code = el.textContent.trim();
            if (code && code.length > 10) {
                const lang = el.className.match(/language-(\w+)/)?.[1] || this.detectLanguage(code);
                this.allCodeBlocks.push({ code, language: lang, element: el });
                this.addCopyButton(el, code, lang);
            }
        });

        if (this.allCodeBlocks.length > 0) {
            const last = this.allCodeBlocks[this.allCodeBlocks.length - 1];
            this.lastCode = last.code;
            this.lastLanguage = last.language;
        }
    }

    detectLanguage(code) {
        if (code.includes('def ') && code.includes(':')) return 'python';
        if (code.includes('function ') || code.includes('const ') || code.includes('let ')) return 'javascript';
        if (code.includes('public class') || code.includes('private void')) return 'java';
        if (code.includes('#include') || code.includes('int main')) return 'cpp';
        if (code.includes('package ') && code.includes('import ')) return 'java';
        return 'text';
    }

    addCopyButton(codeEl, code, language) {
        if (codeEl.parentElement.querySelector('.nj-copier-btn')) return;

        const btn = document.createElement('button');
        btn.className = 'nj-copier-btn';
        btn.textContent = '📋 Copy';
        btn.style.cssText = `
            position: absolute;
            top: 4px;
            right: 4px;
            padding: 4px 10px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 11px;
            z-index: 10;
            opacity: 0.8;
        `;
        btn.onmouseover = () => { btn.style.opacity = '1'; };
        btn.onmouseout = () => { btn.style.opacity = '0.8'; };
        btn.onclick = (e) => {
            e.stopPropagation();
            this.sendToServer(code, language);
            btn.textContent = '✅ Copied!';
            btn.style.background = '#45a049';
            setTimeout(() => {
                btn.textContent = '📋 Copy';
                btn.style.background = '#4CAF50';
            }, 2000);
        };

        codeEl.parentElement.style.position = 'relative';
        codeEl.parentElement.appendChild(btn);
    }

    async sendToServer(code, language, errorInfo = null) {
        const payload = {
            code: code,
            language: language,
            context: {
                platform: this.platform.name,
                url: window.location.href,
                timestamp: Date.now(),
            }
        };
        if (errorInfo) {
            payload.error_info = errorInfo;
        }

        try {
            const response = await fetch(`${this.serverUrl}/code/update`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const result = await response.json();
            console.log('[NJ IDE Copier] Sent to server:', result);
            this.showNotification(`Code saved: ${result.action}`);
            return result;
        } catch (err) {
            console.error('[NJ IDE Copier] Server error:', err);
            this.showNotification('❌ Server not connected', 'error');
            return null;
        }
    }

    async sendChatToServer(messages) {
        const payload = {
            title: `${this.platform.name} Chat - ${new Date().toLocaleString()}`,
            platform: this.platform.name,
            url: window.location.href,
            messages: messages
        };

        try {
            const response = await fetch(`${this.serverUrl}/chat/full`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const result = await response.json();
            console.log('[NJ IDE Copier] Chat exported:', result);
            
            if (result.status === 'success') {
                this.showNotification(`✅ Chat exported: ${result.export_filename}`);
            } else {
                this.showNotification(`❌ Export failed: ${result.message}`, 'error');
            }
            
            return result;
        } catch (err) {
            console.error('[NJ IDE Copier] Export error:', err);
            this.showNotification('❌ Server not connected', 'error');
            return null;
        }
    }

    async copyLastResponse() {
        if (this.lastCode) {
            await this.sendToServer(this.lastCode, this.lastLanguage);
        } else {
            this.showNotification('⚠️ No code found', 'warning');
        }
    }

    async copyAllCode() {
        if (this.allCodeBlocks.length === 0) {
            this.showNotification('⚠️ No code blocks found', 'warning');
            return;
        }

        for (const block of this.allCodeBlocks) {
            await this.sendToServer(block.code, block.language);
        }
        this.showNotification(`✅ Copied ${this.allCodeBlocks.length} code blocks`);
    }

    async copyFullChat() {
        const messages = this.extractMessages();
        if (messages.length === 0) {
            this.showNotification('⚠️ No messages found', 'warning');
            return;
        }

        await this.sendChatToServer(messages);
    }

    extractMessages() {
        const messageElements = document.querySelectorAll(this.platform.messageSelector);
        const messages = [];

        messageElements.forEach((el, index) => {
            const role = el.querySelector('[data-message-author-role]')?.dataset.messageAuthorRole || 
                         (el.textContent.includes('You:') ? 'user' : 'assistant');
            
            const content = el.textContent.trim();
            const codeBlocks = [];

            // Extract code blocks
            const codeEls = el.querySelectorAll('pre code');
            codeEls.forEach(codeEl => {
                codeBlocks.push({
                    code: codeEl.textContent.trim(),
                    language: this.detectLanguage(codeEl.textContent)
                });
            });

            if (content) {
                messages.push({
                    id: `msg-${index}`,
                    role: role,
                    content: content,
                    codeBlocks: codeBlocks
                });
            }
        });

        return messages;
    }

    async exportFullChat() {
        const messages = this.extractMessages();
        if (messages.length === 0) {
            this.showNotification('⚠️ No messages to export', 'warning');
            return;
        }

        await this.sendChatToServer(messages);
    }

    async exportMarkdown() {
        const messages = this.extractMessages();
        
        let md = `# ${this.platform.name} Chat Export\n\n`;
        md += `**Date:** ${new Date().toLocaleString()}\n\n`;
        md += `---\n\n`;

        messages.forEach((msg, i) => {
            md += `## ${i + 1}. [${msg.role.toUpperCase()}]\n\n`;
            md += `${msg.content}\n\n`;
            
            if (msg.codeBlocks && msg.codeBlocks.length > 0) {
                md += `### Code Blocks:\n\n`;
                msg.codeBlocks.forEach((block, j) => {
                    md += `#### Block ${j + 1} (${block.language})\n\n`;
                    md += `\`\`\`${block.language}\n${block.code}\n\`\`\`\n\n`;
                });
            }
            
            md += `---\n\n`;
        });

        await this.sendToServer(md, 'markdown');
        this.showNotification('✅ Markdown exported');
    }

    async showErrorStats() {
        try {
            const response = await fetch(`${this.serverUrl}/errors/stats`);
            const stats = await response.json();
            
            if (stats.status === 'success') {
                const message = `
📊 Error Statistics

Total Errors: ${stats.total_errors}
Fixed: ${stats.fixed_errors}
Fix Rate: ${stats.fix_rate}%

By Type:
${Object.entries(stats.by_type || {}).map(([type, info]) => 
    `• ${type}: ${info.count} (${info.severity})`
).join('\n')}
                `.trim();
                
                this.showModal('Error Statistics', message);
            }
        } catch (err) {
            this.showNotification('❌ Could not load stats', 'error');
        }
    }

    async showExports() {
        try {
            const response = await fetch(`${this.serverUrl}/exports`);
            const data = await response.json();
            
            if (data.exports && data.exports.length > 0) {
                const message = `
📂 Recent Exports (${data.count} total)

${data.exports.slice(0, 5).map(exp => 
    `• ${exp.filename}\n  ${exp.modified_date} (${Math.round(exp.size / 1024)}KB)`
).join('\n\n')}
                `.trim();
                
                this.showModal('Recent Exports', message);
            } else {
                this.showModal('Recent Exports', 'No exports found yet.\n\nExport a chat to see it here!');
            }
        } catch (err) {
            this.showNotification('❌ Could not load exports', 'error');
        }
    }

    showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 12px 20px;
            background: ${type === 'error' ? '#f44336' : type === 'warning' ? '#FF9800' : '#4CAF50'};
            color: white;
            border-radius: 8px;
            font-size: 13px;
            z-index: 9999999;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    showModal(title, content) {
        const modal = document.createElement('div');
        modal.innerHTML = `
            <div class="nj-modal-overlay" style="
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0,0,0,0.7);
                z-index: 9999999;
                display: flex;
                align-items: center;
                justify-content: center;
            ">
                <div class="nj-modal" style="
                    background: white;
                    border-radius: 12px;
                    max-width: 500px;
                    width: 90%;
                    max-height: 80vh;
                    overflow: auto;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.4);
                ">
                    <div style="
                        padding: 16px 20px;
                        border-bottom: 1px solid #e0e0e0;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    ">
                        <h3 style="margin: 0; color: #333; font-size: 16px;">${title}</h3>
                        <button class="nj-modal-close" style="
                            background: none;
                            border: none;
                            font-size: 24px;
                            cursor: pointer;
                            color: #999;
                            padding: 0;
                            width: 30px;
                            height: 30px;
                        ">×</button>
                    </div>
                    <div style="padding: 20px; color: #333; font-size: 14px; line-height: 1.6; white-space: pre-wrap;">
                        ${content}
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        modal.querySelector('.nj-modal-close').onclick = () => modal.remove();
        modal.querySelector('.nj-modal-overlay').onclick = (e) => {
            if (e.target === modal.querySelector('.nj-modal-overlay')) modal.remove();
        };
    }
}

// Auto-start
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new NJIDECopier());
} else {
    new NJIDECopier();
}
