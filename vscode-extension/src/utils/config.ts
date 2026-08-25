import * as vscode from 'vscode';

export class Config {
    private config = vscode.workspace.getConfiguration('nj-ide-copier');

    getServerPort(): number {
        return this.config.get('serverPort', 8765);
    }

    shouldAutoStart(): boolean {
        return this.config.get('autoStart', true);
    }

    shouldAutoInsert(): boolean {
        return this.config.get('autoInsert', true);
    }

    shouldTrackVersions(): boolean {
        return this.config.get('trackVersions', true);
    }

    shouldShowNotifications(): boolean {
        return this.config.get('showNotifications', true);
    }

    shouldFormatOnInsert(): boolean {
        return this.config.get('formatOnInsert', true);
    }

    getDefaultLanguage(): string {
        return this.config.get('defaultLanguage', 'auto');
    }

    getSaveLocation(): string {
        return this.config.get('saveLocation', '~/.nj-ide-copier');
    }
}
