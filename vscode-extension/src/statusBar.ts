import * as vscode from 'vscode';

export class StatusBarManager {
    private statusBarItem: vscode.StatusBarItem;

    constructor() {
        this.statusBarItem = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Right,
            100
        );
        this.statusBarItem.show();
    }

    setRunning(running: boolean) {
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

    dispose() {
        this.statusBarItem.dispose();
    }
}
