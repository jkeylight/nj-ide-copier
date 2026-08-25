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
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const serverManager_1 = require("./serverManager");
const codeInserter_1 = require("./codeInserter");
const versionViewer_1 = require("./versionViewer");
const errorTracker_1 = require("./errorTracker");
const statusBar_1 = require("./statusBar");
const httpClient_1 = require("./utils/httpClient");
const config_1 = require("./utils/config");
let serverManager;
let codeInserter;
let versionViewer;
let errorTracker;
let statusBar;
let httpClient;
let config;
function activate(context) {
    console.log('NJ IDE Copier extension is now active');
    config = new config_1.Config();
    httpClient = new httpClient_1.HttpClient(config.getServerPort());
    serverManager = new serverManager_1.ServerManager(context, httpClient);
    codeInserter = new codeInserter_1.CodeInserter(httpClient, config);
    versionViewer = new versionViewer_1.VersionViewer(context, httpClient);
    errorTracker = new errorTracker_1.ErrorTracker(context, httpClient);
    statusBar = new statusBar_1.StatusBarManager();
    registerCommands(context);
    if (config.shouldAutoStart()) {
        serverManager.startServer();
    }
    vscode.window.showInformationMessage('NJ IDE Copier is ready!');
}
function registerCommands(context) {
    context.subscriptions.push(vscode.commands.registerCommand('nj-ide-copier.start', async () => {
        await serverManager.startServer();
    }));
    context.subscriptions.push(vscode.commands.registerCommand('nj-ide-copier.stop', async () => {
        await serverManager.stopServer();
    }));
    context.subscriptions.push(vscode.commands.registerCommand('nj-ide-copier.dashboard', () => {
        DashboardPanel.createOrShow(context.extensionUri, httpClient);
    }));
    context.subscriptions.push(vscode.commands.registerCommand('nj-ide-copier.insertCode', async () => {
        await codeInserter.insertLastCode();
    }));
    context.subscriptions.push(vscode.commands.registerCommand('nj-ide-copier.showHistory', async () => {
        await versionViewer.showHistory();
    }));
    context.subscriptions.push(vscode.commands.registerCommand('nj-ide-copier.revertVersion', async () => {
        await versionViewer.revertVersion();
    }));
    context.subscriptions.push(vscode.commands.registerCommand('nj-ide-copier.copyToClipboard', async () => {
        await codeInserter.copyToClipboard();
    }));
    context.subscriptions.push(vscode.commands.registerCommand('nj-ide-copier.showErrors', async () => {
        await errorTracker.showErrorTracker();
    }));
    context.subscriptions.push(vscode.commands.registerCommand('nj-ide-copier.configure', async () => {
        await vscode.commands.executeCommand('workbench.action.openSettings', 'nj-ide-copier');
    }));
}
class DashboardPanel {
    static createOrShow(extensionUri, httpClient) {
        if (DashboardPanel.currentPanel) {
            DashboardPanel.currentPanel.panel.reveal(vscode.ViewColumn.One);
            return;
        }
        const panel = vscode.window.createWebviewPanel(DashboardPanel.viewType, 'NJ Copier Dashboard', vscode.ViewColumn.One, { enableScripts: true, retainContextWhenHidden: true });
        DashboardPanel.currentPanel = new DashboardPanel(panel, extensionUri, httpClient);
    }
    constructor(panel, extensionUri, httpClient) {
        this.panel = panel;
        this.extensionUri = extensionUri;
        this.httpClient = httpClient;
        this.panel.webview.html = this.getHtml();
        this.panel.onDidDispose(() => { DashboardPanel.currentPanel = undefined; });
    }
    getHtml() {
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
DashboardPanel.viewType = 'njIdeCopierDashboard';
function deactivate() {
    if (serverManager) {
        serverManager.stopServer();
    }
}
//# sourceMappingURL=extension.js.map