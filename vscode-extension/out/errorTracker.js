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
exports.ErrorTracker = void 0;
const vscode = __importStar(require("vscode"));
class ErrorTracker {
    constructor(context, httpClient) {
        this.context = context;
        this.httpClient = httpClient;
    }
    async showErrorTracker() {
        try {
            const response = await this.httpClient.get('/errors/stats');
            const panel = vscode.window.createWebviewPanel('njIdeCopierErrors', 'NJ Copier - Error Tracker', vscode.ViewColumn.One, { enableScripts: true, retainContextWhenHidden: true });
            panel.webview.html = this.generateErrorHtml(response);
        }
        catch (error) {
            vscode.window.showErrorMessage(`Failed to load error stats: ${error}`);
        }
    }
    generateErrorHtml(stats) {
        const totalErrors = stats.total_errors || 0;
        const errorsByType = stats.errors_by_type || {};
        const errorRows = Object.entries(errorsByType).map(([type, count]) => `
            <tr>
                <td>${type}</td>
                <td>${count}</td>
            </tr>
        `).join('');
        return `<!DOCTYPE html>
<html>
<head>
<style>
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 20px; background: #1e1e1e; color: #ccc; }
h2 { color: #4fc3f7; }
.stat-card { background: #2d2d2d; border-radius: 8px; padding: 20px; margin: 10px 0; }
.stat-number { font-size: 36px; font-weight: bold; color: #4fc3f7; }
table { width: 100%; border-collapse: collapse; margin-top: 10px; }
th, td { padding: 8px 12px; text-align: left; border-bottom: 1px solid #444; }
th { background: #383838; color: #4fc3f7; }
</style>
</head>
<body>
<h2>Error Tracker</h2>
<div class="stat-card">
    <div>Total Errors</div>
    <div class="stat-number">${totalErrors}</div>
</div>
<div class="stat-card">
    <h3>Errors by Type</h3>
    <table>
        <tr><th>Type</th><th>Count</th></tr>
        ${errorRows || '<tr><td colspan="2">No errors tracked</td></tr>'}
    </table>
</div>
</body>
</html>`;
    }
}
exports.ErrorTracker = ErrorTracker;
//# sourceMappingURL=errorTracker.js.map