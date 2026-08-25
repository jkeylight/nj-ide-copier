/**
 * NJ IDE Copier - Background Service Worker v2.0
 */

const SERVER_URL = 'http://localhost:8765';

// Handle messages from content script and popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('[Background] Received message:', request.action);
    
    if (request.action === 'getServerStatus') {
        checkServerStatus().then(sendResponse);
        return true;
    }
    
    if (request.action === 'copyToServer') {
        sendToServer(request.data).then(sendResponse);
        return true;
    }
    
    return false;
});

async function checkServerStatus() {
    try {
        const response = await fetch(`${SERVER_URL}/status`);
        return { status: response.ok ? 'connected' : 'disconnected' };
    } catch (err) {
        return { status: 'disconnected' };
    }
}

async function sendToServer(data) {
    try {
        const endpoint = data.endpoint || '/code/update';
        const response = await fetch(`${SERVER_URL}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data.payload)
        });
        
        const result = await response.json();
        return { success: true, data: result };
    } catch (err) {
        console.error('[Background] Server error:', err);
        return { success: false, error: err.message };
    }
}

// Badge management
chrome.runtime.onInstalled.addListener(() => {
    console.log('[NJ IDE Copier] Extension installed');
    chrome.action.setBadgeText({ text: 'v2' });
    chrome.action.setBadgeBackgroundColor({ color: '#667eea' });
});

// Update badge when server status changes
setInterval(async () => {
    const status = await checkServerStatus();
    if (status.status === 'connected') {
        chrome.action.setBadgeBackgroundColor({ color: '#4CAF50' });
    } else {
        chrome.action.setBadgeBackgroundColor({ color: '#f44336' });
    }
}, 30000);
