/**
 * Background Service Worker for NJ IDE Copier.
 * Routes messages between popup and content scripts.
 */

// Handle messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'getServerStatus') {
        fetch('http://localhost:8765/status')
            .then(response => response.json())
            .then(data => sendResponse({ status: 'online', data }))
            .catch(() => sendResponse({ status: 'offline' }));
        return true; // Keep message channel open for async response
    }

    if (request.action === 'forwardToContent') {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (tabs[0]) {
                chrome.tabs.sendMessage(tabs[0].id, request.payload);
            }
        });
        sendResponse({ status: 'forwarded' });
        return true;
    }
});

// Handle keyboard shortcuts
chrome.commands?.onCommand?.addListener((command) => {
    if (command === 'copy-last-response') {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (tabs[0]) {
                chrome.tabs.sendMessage(tabs[0].id, { action: 'copyLastResponse' });
            }
        });
    }
});
