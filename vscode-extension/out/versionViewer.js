"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.VersionViewer = void 0;
const vscode = __importStar(require("vscode"));
class VersionViewer {
    constructor(context, httpClient) {
        this.context = context;
        this.httpClient = httpClient;
    }
    async showHistory() {
        try {
            const response = await this.httpClient.get('/versions');
            if (response && response.blocks && response.blocks.length > 0) {
                const panel = vscode.window.createWebviewPanel('njIdeCopierHistory', 'NJ Copier - Version History', vscode.ViewColumn.One, { enableScripts: true, retainContextWhenHidden: true });
                panel.webview.html = this.generateHistoryHtml(response.blocks);
            }
            else {
                vscode.window.showInformationMessage('No version history available');
            }
        }
        catch (error) {
            vscode.window.showErrorMessage(`Failed to load history: ${error}`);
        }
    }
    async revertVersion() {
        try {
            const response = await this.httpClient.get('/versions');
            if (!response || !response.blocks || response.blocks.length === 0) {
                vscode.window.showWarningMessage('No versions available to revert');
                return;
            }
            const blocks = response.blocks.map((block, index) => ({
                label: `${block.language} - Block ${index + 1}`,
                description: `${block.versions.length} versions`,
                blockData: block
            }));
            const selectedBlock = await vscode.window.showQuickPick(blocks, {
                placeHolder: 'Select code block to revert'
            });
            if (!selectedBlock) {
                return;
            }
            const versions = selectedBlock.blockData.versions.map((version) => ({
                label: `Version ${version.version_id}`,
                description: version.status,
                detail: version.change_summary || 'No changes',
                versionData: version
            }));
            const selectedVersion = await vscode.window.showQuickPick(versions, {
                placeHolder: 'Select version to revert to'
            });
            if (!selectedVersion) {
                return;
            }
            const confirmation = await vscode.window.showWarningMessage(`Revert to version ${selectedVersion.versionData.version_id}?`, { modal: true }, 'Yes', 'No');
            if (confirmation !== 'Yes') {
                return;
            }
            const revertResponse = await this.httpClient.post('/version/revert', {
                block_id: selectedBlock.blockData.block_id,
                version_id: selectedVersion.versionData.version_id
            });
            if (revertResponse.status === 'success') {
                vscode.window.showInformationMessage(`Reverted to version ${selectedVersion.versionData.version_id}`);
            }
        }
        catch (error) {
            vscode.window.showErrorMessage(`Failed to revert version: ${error}`);
        }
    }
    generateHistoryHtml(blocks) {
        const blockHtml = blocks.map((block, index) => {
            const versionsHtml = block.versions.map((version, vIndex) => {
                const statusClass = this.getStatusClass(version.status);
                const isCurrent = vIndex === block.versions.length - 1;
                return `
                    <div class="version-item ${statusClass} ${isCurrent ? 'current' : ''}">
                        <div class="version-header">
                            <span class="version-id">${version.version_id}</span>
                            <span class="status-badge ${statusClass}">${version.status}</span>
                            ${isCurrent ? '<span class="current-badge">Current</span>' : ''}
                        </div>
                        <div class="version-meta">
                            ${version.change_summary ? `<p>${version.change_summary}</p>` : ''}
                        </div>
                        <pre class="code-preview"><code>${this.escapeHtml(version.code.substring(0, 500))}${version.code.length > 500 ? '...' : ''}</code></pre>
                    </div>
                `;
            }).join('');
            return `
                <div class="block-section">
                    <h3>${block.language} - Block ${index + 1}</h3>
                    <p class="block-info">Block ID: ${block.block_id} | Updated: ${new Date(block.updated_at * 1000).toLocaleString()}</p>
                    <div class="versions-list">${versionsHtml}</div>
                </div>
            `;
        }).join('');
        return `<!DOCTYPE html>
<html>
<head>
<style>
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 20px; background: #1e1e1e; color: #ccc; }
.block-section { background: #2d2d2d; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
.block-section h3 { color: #4fc3f7; margin: 0 0 10px 0; }
.block-info { color: #888; font-size: 12px; }
.versions-list { display: flex; flex-direction: column; gap: 10px; }
.version-item { border: 1px solid #444; border-radius: 6px; padding: 10px; }
.version-item.error { border-left: 4px solid #f44336; }
.version-item.fixed { border-left: 4px solid #4caf50; }
.version-item.current { background: #383838; border: 2px solid #4fc3f7; }
.version-header { display: flex; align-items: center; gap: 10px; margin-bottom: 5px; }
.version-id { font-weight: bold; }
.status-badge { padding: 2px 8px; border-radius: 12px; font-size: 11px; }
.status-badge.error { background: #5c2020; color: #f48771; }
.status-badge.fixed { background: #1e3a1e; color: #81c784; }
.current-badge { background: #0e639c; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; }
.code-preview { background: #1e1e1e; border: 1px solid #444; border-radius: 4px; padding: 10px; font-family: 'Consolas', monospace; font-size: 12px; overflow-x: auto; white-space: pre-wrap; }
</style>
</head>
<body>
<h2 style="color:#4fc3f7">Version History</h2>
${blockHtml}
</body>
</html>`;
    }
    getStatusClass(status) {
        switch (status.toLowerCase()) {
            case 'error': return 'error';
            case 'fixed': return 'fixed';
            default: return '';
        }
    }
    escapeHtml(text) {
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    }
}
exports.VersionViewer = VersionViewer;
//# sourceMappingURL=versionViewer.js.map