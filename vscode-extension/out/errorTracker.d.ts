import * as vscode from 'vscode';
import { HttpClient } from './utils/httpClient';
export declare class ErrorTracker {
    private context;
    private httpClient;
    constructor(context: vscode.ExtensionContext, httpClient: HttpClient);
    showErrorTracker(): Promise<void>;
    private generateErrorHtml;
}
//# sourceMappingURL=errorTracker.d.ts.map