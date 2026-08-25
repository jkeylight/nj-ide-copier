import * as vscode from 'vscode';
import { HttpClient } from './utils/httpClient';

export class ErrorTracker {
    constructor(
        private context: vscode.ExtensionContext,
        private httpClient: HttpClient
    ) {}

    async showErrorTracker(): Promise<void> {
        try {
            const response = await this.httpClient.get('/errors/stats');

            const panel = vscode.window.createWebviewPanel(
                'njIdeCopierErrors',
                'NJ Copier - Error Tracker',
                vscode.ViewColumn.One,
                { enableScripts: true, retainContextWhenHidden: true }
            );

            panel.webview.html = this.generateErrorHtml(response);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to load error stats: ${error}`);
        }
    }

    private generateErrorHtml(stats: any): string {
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
