/**
 * NJ IDE Copier - Popup Script v2.0
 */

const SERVER_URL = 'http://localhost:8765';

// Check server status on load
document.addEventListener('DOMContentLoaded', () => {
    checkServerStatus();
    setupEventListeners();
});

async function checkServerStatus() {
    try {
        const response = await fetch(`${SERVER_URL}/status`);
        if (response.ok) {
            updateStatus(true);
        } else {
            updateStatus(false);
        }
    } catch (err) {
        updateStatus(false);
    }
}

function updateStatus(connected) {
    const dot = document.getElementById('status-dot');
    const text = document.getElementById('status-text');
    
    if (connected) {
        dot.classList.add('connected');
        dot.classList.remove('disconnected');
        text.textContent = 'Connected';
    } else {
        dot.classList.add('disconnected');
        dot.classList.remove('connected');
        text.textContent = 'Disconnected';
    }
}

function setupEventListeners() {
    document.getElementById('btn-copy-last').addEventListener('click', copyLastCode);
    document.getElementById('btn-copy-all').addEventListener('click', copyAllCode);
    document.getElementById('btn-export-chat').addEventListener('click', exportChat);
    document.getElementById('btn-export-md').addEventListener('click', exportMarkdown);
    document.getElementById('btn-stats').addEventListener('click', showStats);
    document.getElementById('btn-exports').addEventListener('click', showExports);
}

async function copyLastCode() {
    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        const response = await chrome.tabs.sendMessage(tab.id, { action: 'copyLastResponse' });
        showNotification('Last code copied!', 'success');
    } catch (err) {
        showNotification('Failed to copy code', 'error');
    }
}

async function copyAllCode() {
    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        const response = await chrome.tabs.sendMessage(tab.id, { action: 'copyAllCode' });
        showNotification('All code copied!', 'success');
    } catch (err) {
        showNotification('Failed to copy code', 'error');
    }
}

async function exportChat() {
    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        const response = await chrome.tabs.sendMessage(tab.id, { action: 'exportChat' });
        showNotification('Chat exported successfully!', 'success');
    } catch (err) {
        showNotification('Failed to export chat', 'error');
    }
}

async function exportMarkdown() {
    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        const response = await chrome.tabs.sendMessage(tab.id, { action: 'exportMarkdown' });
        showNotification('Markdown exported!', 'success');
    } catch (err) {
        showNotification('Failed to export', 'error');
    }
}

async function showStats() {
    try {
        const response = await fetch(`${SERVER_URL}/errors/stats`);
        const stats = await response.json();
        
        if (stats.status === 'success') {
            let content = `Total Errors: ${stats.total_errors}\n`;
            content += `Fixed: ${stats.fixed_errors}\n`;
            content += `Fix Rate: ${stats.fix_rate}%\n\n`;
            content += `By Type:\n`;
            
            Object.entries(stats.by_type || {}).forEach(([type, info]) => {
                content += `• ${type}: ${info.count} (${info.severity})\n`;
            });
            
            document.getElementById('stats-content').textContent = content;
            document.getElementById('stats-modal').style.display = 'flex';
        } else {
            showNotification('Failed to load stats', 'error');
        }
    } catch (err) {
        showNotification('Server not connected', 'error');
    }
}

async function showExports() {
    try {
        const response = await fetch(`${SERVER_URL}/exports`);
        const data = await response.json();
        
        if (data.exports && data.exports.length > 0) {
            let content = `Found ${data.count} export(s)\n\n`;
            
            data.exports.slice(0, 5).forEach(exp => {
                const size = Math.round(exp.size / 1024);
                content += `📄 ${exp.filename}\n`;
                content += `   ${exp.modified_date} • ${size}KB\n\n`;
            });
            
            document.getElementById('exports-content').textContent = content;
            document.getElementById('exports-modal').style.display = 'flex';
        } else {
            document.getElementById('exports-content').textContent = 'No exports found yet.\n\nExport a chat to see it here!';
            document.getElementById('exports-modal').style.display = 'flex';
        }
    } catch (err) {
        showNotification('Server not connected', 'error');
    }
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

function showNotification(message, type) {
    // Simple alert for popup (could be improved with custom UI)
    alert(message);
}
