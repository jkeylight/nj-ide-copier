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
exports.CodeInserter = void 0;
const vscode = __importStar(require("vscode"));
class CodeInserter {
    constructor(httpClient, config) {
        this.httpClient = httpClient;
        this.config = config;
    }
    async insertLastCode() {
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
                    vscode.window.showInformationMessage(`Code inserted from NJ Copier (${language})`);
                }
            }
            else {
                vscode.window.showWarningMessage('No code available to insert');
            }
        }
        catch (error) {
            vscode.window.showErrorMessage(`Failed to insert code: ${error}`);
        }
    }
    async copyToClipboard() {
        try {
            const response = await this.httpClient.get('/versions');
            if (response && response.blocks && response.blocks.length > 0) {
                const lastBlock = response.blocks[response.blocks.length - 1];
                const currentVersion = lastBlock.versions[lastBlock.versions.length - 1];
                await vscode.env.clipboard.writeText(currentVersion.code);
                vscode.window.showInformationMessage('Code copied to clipboard');
            }
            else {
                vscode.window.showWarningMessage('No code available to copy');
            }
        }
        catch (error) {
            vscode.window.showErrorMessage(`Failed to copy code: ${error}`);
        }
    }
    async formatCode(code, language) {
        try {
            const document = await vscode.workspace.openTextDocument({
                content: code,
                language: language
            });
            const edits = await vscode.commands.executeCommand('vscode.executeFormatDocumentProvider', document.uri);
            if (edits && edits.length > 0) {
                return document.getText();
            }
        }
        catch (error) {
            console.log('Formatting failed, using original code');
        }
        return code;
    }
}
exports.CodeInserter = CodeInserter;
//# sourceMappingURL=codeInserter.js.map