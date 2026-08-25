import * as vscode from 'vscode';
import { HttpClient } from './utils/httpClient';
export declare class VersionViewer {
    private context;
    private httpClient;
    constructor(context: vscode.ExtensionContext, httpClient: HttpClient);
    showHistory(): Promise<void>;
    revertVersion(): Promise<void>;
    private generateHistoryHtml;
    private getStatusClass;
    private escapeHtml;
}
//# sourceMappingURL=versionViewer.d.ts.map