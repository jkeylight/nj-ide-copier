import * as vscode from 'vscode';
import { ServerManager } from './serverManager';
import { CodeInserter } from './codeInserter';
import { VersionViewer } from './versionViewer';
import { ErrorTracker } from './errorTracker';
import { StatusBarManager } from './statusBar';
import { HttpClient } from './utils/httpClient';
import { Config } from './utils/config';

let serverManager: ServerManager;
let codeInserter: CodeInserter;
let versionViewer: VersionViewer;
let errorTracker: ErrorTracker;
let statusBar: StatusBarManager;
let httpClient: HttpClient;
let config: Config;

export function activate(context: vscode.ExtensionContext) {
    console.log('NJ IDE Copier extension is now active');

    config = new Config();
    httpClient = new HttpClient(config.getServerPort());
    serverManager = new ServerManager(context, httpClient);
    codeInserter = new CodeInserter(httpClient, config);
    versionViewer = new VersionViewer(context, httpClient);
    errorTracker = new ErrorTracker(context, httpClient);
    statusBar = new StatusBarManager();

    registerCommands(context);

    if (config.shouldAutoStart()) {
        serverManager.startServer();
    }

    vscode.window.showInformationMessage('NJ IDE Copier is ready!');
}

function registerCommands(context: vscode.ExtensionContext) {
    context.subscriptions.push(
        vscode.commands.registerCommand('nj-ide-copier.start', async () => {
            await serverManager.startServer();
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('nj-ide-copier.stop', async () => {
            await serverManager.stopServer();
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('nj-ide-copier.dashboard', () => {
            DashboardPanel.createOrShow(context.extensionUri, httpClient);
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('nj-ide-copier.insertCode', async () => {
            await codeInserter.insertLastCode();
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('nj-ide-copier.showHistory', async () => {
            await versionViewer.showHistory();
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('nj-ide-copier.revertVersion', async () => {
            await versionViewer.revertVersion();
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('nj-ide-copier.copyToClipboard', async () => {
            await codeInserter.copyToClipboard();
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('nj-ide-copier.showErrors', async () => {
            await errorTracker.showErrorTracker();
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('nj-ide-copier.configure', async () => {
            await vscode.commands.executeCommand(
                'workbench.action.openSettings',
                'nj-ide-copier'
            );
        })
    );
}

class DashboardPanel {
    public static currentPanel: DashboardPanel | undefined;
    private static readonly viewType = 'njIdeCopierDashboard';
    private panel: vscode.WebviewPanel;
    private extensionUri: vscode.Uri;
    private httpClient: HttpClient;

    public static createOrShow(extensionUri: vscode.Uri, httpClient: HttpClient) {
        if (DashboardPanel.currentPanel) {
            DashboardPanel.currentPanel.panel.reveal(vscode.ViewColumn.One);
            return;
        }
        const panel = vscode.window.createWebviewPanel(
            DashboardPanel.viewType,
            'NJ Copier Dashboard',
            vscode.ViewColumn.One,
            { enableScripts: true, retainContextWhenHidden: true }
        );
        DashboardPanel.currentPanel = new DashboardPanel(panel, extensionUri, httpClient);
    }

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri, httpClient: HttpClient) {
        this.panel = panel;
        this.extensionUri = extensionUri;
        this.httpClient = httpClient;
        this.panel.webview.html = this.getHtml();
        this.panel.onDidDispose(() => { DashboardPanel.currentPanel = undefined; });
    }

    private getHtml(): string {
        return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NJ IDE Copier Dashboard</title>
<style>
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 20px; background: #1e1e1e; color: #ccc; }
h1 { color: #4fc3f7; }
.status { padding: 10px; background: #2d2d2d; border-radius: 6px; margin: 10px 0; }
.status.running { border-left: 4px solid #4caf50; }
.status.stopped { border-left: 4px solid #f44336; }
button { background: #0e639c; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; margin: 4px; }
button:hover { background: #1177bb; }
</style>
</head>
<body>
<h1>NJ IDE Copier Dashboard</h1>
<div id="status" class="status stopped">Checking server...</div>
<div>
<button onclick="startServer()">Start Server</button>
<button onclick="stopServer()">Stop Server</button>
<button onclick="refreshStatus()">Refresh</button>
</div>
<script>
const vscode = acquireVsCodeApi();
async function refreshStatus() {
    try {
        const resp = await fetch('http://localhost:8765/status');
        const data = await resp.json();
        document.getElementById('status').className = 'status running';
        document.getElementById('status').innerHTML = '<strong>Server Running</strong><br>IDEs: ' + JSON.stringify(data.ides || []);
    } catch(e) {
        document.getElementById('status').className = 'status stopped';
        document.getElementById('status').innerHTML = '<strong>Server Stopped</strong>';
    }
}
function startServer() { vscode.postMessage({command: 'start'}); refreshStatus(); }
function stopServer() { vscode.postMessage({command: 'stop'}); refreshStatus(); }
refreshStatus();
setInterval(refreshStatus, 5000);
</script>
</body>
</html>`;
    }
}

export function deactivate() {
    if (serverManager) {
        serverManager.stopServer();
    }
}
