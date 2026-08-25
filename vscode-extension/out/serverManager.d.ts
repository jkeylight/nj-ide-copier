import * as vscode from 'vscode';
import { HttpClient } from './utils/httpClient';
export declare class ServerManager {
    private context;
    private httpClient;
    private statusBarItem;
    private isRunning;
    constructor(context: vscode.ExtensionContext, httpClient: HttpClient);
    startServer(): Promise<void>;
    stopServer(): Promise<void>;
    private updateStatusBar;
}
//# sourceMappingURL=serverManager.d.ts.map