/**
 * NJ IDE Copier - Content script for AI chat extraction.
 * Works with ChatGPT, Claude, DeepSeek, Qwen, Kimi, MiMo, Gemini, and more.
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
        this.init();
    }

    init() {
        console.log(`[NJ IDE Copier] Platform: ${this.platform.name}`);
        this.setupUI();
        this.setupMessageListener();
        this.observeCodeBlocks();
    }

    setupUI() {
        if (document.getElementById('nj-ide-copier-actions')) return;

        const container = document.createElement('div');
        container.id = 'nj-ide-copier-actions';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 999999;
            display: flex;
            flex-direction: column;
            gap: 8px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        `;

        const badge = document.createElement('div');
        badge.textContent = `NJ IDE Copier - ${this.platform.name}`;
        badge.style.cssText = `
            padding: 4px 10px;
            background: rgba(33, 150, 243, 0.9);
            color: white;
            border-radius: 12px;
            font-size: 11px;
            text-align: center;
            font-weight: 600;
            margin-bottom: 4px;
        `;
        container.appendChild(badge);

        const buttons = [
            { text: 'Copy Full Chat', color: '#2196F3', action: () => this.copyFullChat() },
            { text: 'Copy Last Response', color: '#4CAF50', action: () => this.copyLastResponse() },
            { text: 'Copy All Code', color: '#FF9800', action: () => this.copyAllCode() },
            { text: 'Export Markdown', color: '#9C27B0', action: () => this.exportMarkdown() },
        ];

        buttons.forEach(({ text, color, action }) => {
            const btn = document.createElement('button');
            btn.textContent = text;
            btn.style.cssText = `
                padding: 8px 14px;
                background: ${color};
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 13px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                transition: all 0.2s;
                white-space: nowrap;
                text-align: left;
            `;
            btn.onmouseover = () => { btn.style.transform = 'scale(1.03)'; };
            btn.onmouseout = () => { btn.style.transform = 'scale(1)'; };
            btn.onclick = action;
            container.appendChild(btn);
        });

        document.body.appendChild(container);
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
                const lang = el.className.match(/language-(\w+)/)?.[1] || 'text';
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

    addCopyButton(codeEl, code, language) {
        if (codeEl.parentElement.querySelector('.nj-copier-btn')) return;

        const wrapper = document.createElement('div');
        wrapper.style.cssText = 'position: relative; display: inline-block; width: 100%;';

        const btn = document.createElement('button');
        btn.className = 'nj-copier-btn';
        btn.textContent = 'Copy to IDE';
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
            btn.textContent = 'Copied!';
            setTimeout(() => { btn.textContent = 'Copy to IDE'; }, 2000);
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
            const response = await fetch('http://localhost:8765/code/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const result = await response.json();
            console.log('[NJ IDE Copier] Sent to server:', result);
            return result;
        } catch (err) {
            console.error('[NJ IDE Copier] Server error:', err);
            return null;
        }
    }

    copyLastResponse() {
        if (this.lastCode) {
            this.sendToServer(this.lastCode, this.lastLanguage);
        }
    }

    copyAllCode() {
        this.allCodeBlocks.forEach(block => {
            this.sendToServer(block.code, block.language);
        });
    }

    copyFullChat() {
        const messages = document.querySelectorAll(this.platform.messageSelector);
        let fullText = '';

        messages.forEach(msg => {
            fullText += msg.textContent.trim() + '\n\n';
        });

        if (fullText) {
            this.sendToServer(fullText, 'markdown');
        }
    }

    exportMarkdown() {
        const messages = document.querySelectorAll(this.platform.messageSelector);
        let md = `# Chat Export - ${this.platform.name}\n\n`;

        messages.forEach(msg => {
            md += msg.textContent.trim() + '\n\n---\n\n';
        });

        this.sendToServer(md, 'markdown');
    }
}

// Auto-start
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new NJIDECopier());
} else {
    new NJIDECopier();
}
