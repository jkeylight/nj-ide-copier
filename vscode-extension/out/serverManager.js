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
exports.ServerManager = void 0;
const vscode = __importStar(require("vscode"));
class ServerManager {
    constructor(context, httpClient) {
        this.context = context;
        this.httpClient = httpClient;
        this.isRunning = false;
        this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
        this.statusBarItem.command = 'nj-ide-copier.dashboard';
        this.updateStatusBar(false);
        this.statusBarItem.show();
    }
    async startServer() {
        try {
            const isRunning = await this.httpClient.checkHealth();
            if (isRunning) {
                this.isRunning = true;
                this.updateStatusBar(true);
                vscode.window.showInformationMessage('NJ Copier server is already running');
                return;
            }
            vscode.window.showWarningMessage('NJ Copier server is not running. Please start it with: start_server.bat');
        }
        catch (error) {
            vscode.window.showErrorMessage(`Failed to connect to server: ${error}`);
        }
    }
    async stopServer() {
        this.isRunning = false;
        this.updateStatusBar(false);
        vscode.window.showInformationMessage('NJ Copier disconnected');
    }
    updateStatusBar(running) {
        this.isRunning = running;
        if (running) {
            this.statusBarItem.text = '$(radio-tower) NJ Copier';
            this.statusBarItem.tooltip = 'NJ IDE Copier server is running';
            this.statusBarItem.backgroundColor = undefined;
        }
        else {
            this.statusBarItem.text = '$(stop) NJ Copier';
            this.statusBarItem.tooltip = 'NJ IDE Copier server is stopped';
            this.statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
        }
    }
}
exports.ServerManager = ServerManager;
//# sourceMappingURL=serverManager.js.map