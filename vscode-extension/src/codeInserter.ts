import * as vscode from 'vscode';
import { HttpClient } from './utils/httpClient';
import { Config } from './utils/config';

export class CodeInserter {
    constructor(
        private httpClient: HttpClient,
        private config: Config
    ) {}

    async insertLastCode(): Promise<void> {
        const editor = vscode.window.activeTextEditor;

        if (!editor) {
            vscode.window.showWarningMessage('No active editor found');
            return;
        }

        try {
            const response = await this.httpClient.get('/versions');

            if (response && response.blocks && response.blocks.length > 0) {
                const lastBlock = response.blocks[response.blocks.length - 1];
                const currentVersion = lastBlock.versions[lastBlock.versions.length - 1];
                const code = currentVersion.code;
                const language = lastBlock.language || 'text';

                let formattedCode = code;
                if (this.config.shouldFormatOnInsert()) {
                    formattedCode = await this.formatCode(code, language);
                }

                const position = editor.selection.active;

                await editor.edit((editBuilder) => {
                    editBuilder.insert(position, formattedCode);
                });

                if (this.config.shouldShowNotifications()) {
                    vscode.window.showInformationMessage(
                        `Code inserted from NJ Copier (${language})`
                    );
                }
            } else {
                vscode.window.showWarningMessage('No code available to insert');
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to insert code: ${error}`);
        }
    }

    async copyToClipboard(): Promise<void> {
        try {
            const response = await this.httpClient.get('/versions');

            if (response && response.blocks && response.blocks.length > 0) {
                const lastBlock = response.blocks[response.blocks.length - 1];
                const currentVersion = lastBlock.versions[lastBlock.versions.length - 1];
                await vscode.env.clipboard.writeText(currentVersion.code);
                vscode.window.showInformationMessage('Code copied to clipboard');
            } else {
                vscode.window.showWarningMessage('No code available to copy');
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to copy code: ${error}`);
        }
    }

    private async formatCode(code: string, language: string): Promise<string> {
        try {
            const document = await vscode.workspace.openTextDocument({
                content: code,
                language: language
            });

            const edits = await vscode.commands.executeCommand<vscode.TextEdit[]>(
                'vscode.executeFormatDocumentProvider',
                document.uri
            );

            if (edits && edits.length > 0) {
                return document.getText();
            }
        } catch (error) {
            console.log('Formatting failed, using original code');
        }

        return code;
    }
}
