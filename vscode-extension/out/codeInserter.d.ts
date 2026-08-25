import { HttpClient } from './utils/httpClient';
import { Config } from './utils/config';
export declare class CodeInserter {
    private httpClient;
    private config;
    constructor(httpClient: HttpClient, config: Config);
    insertLastCode(): Promise<void>;
    copyToClipboard(): Promise<void>;
    private formatCode;
}
//# sourceMappingURL=codeInserter.d.ts.map