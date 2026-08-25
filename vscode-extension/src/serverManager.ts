import * as vscode from 'vscode';
import { HttpClient } from './utils/httpClient';

export class ServerManager {
    private statusBarItem: vscode.StatusBarItem;
    private isRunning = false;

    constructor(
        private context: vscode.ExtensionContext,
        private httpClient: HttpClient
    ) {
        this.statusBarItem = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Right,
            100
        );
        this.statusBarItem.command = 'nj-ide-copier.dashboard';
        this.updateStatusBar(false);
        this.statusBarItem.show();
    }

    async startServer(): Promise<void> {
        try {
            const isRunning = await this.httpClient.checkHealth();
            if (isRunning) {
                this.isRunning = true;
                this.updateStatusBar(true);
                vscode.window.showInformationMessage('NJ Copier server is already running');
                return;
            }
            vscode.window.showWarningMessage(
                'NJ Copier server is not running. Please start it with: start_server.bat'
            );
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to connect to server: ${error}`);
        }
    }

    async stopServer(): Promise<void> {
        this.isRunning = false;
        this.updateStatusBar(false);
        vscode.window.showInformationMessage('NJ Copier disconnected');
    }

    private updateStatusBar(running: boolean) {
        this.isRunning = running;
        if (running) {
            this.statusBarItem.text = '$(radio-tower) NJ Copier';
            this.statusBarItem.tooltip = 'NJ IDE Copier server is running';
            this.statusBarItem.backgroundColor = undefined;
        } else {
            this.statusBarItem.text = '$(stop) NJ Copier';
            this.statusBarItem.tooltip = 'NJ IDE Copier server is stopped';
            this.statusBarItem.backgroundColor = new vscode.ThemeColor(
                'statusBarItem.warningBackground'
            );
        }
    }
}
