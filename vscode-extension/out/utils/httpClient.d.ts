export declare class HttpClient {
    private port;
    private client;
    constructor(port?: number);
    checkHealth(): Promise<boolean>;
    get(path: string, params?: any): Promise<any>;
    post(path: string, data?: any): Promise<any>;
}
//# sourceMappingURL=httpClient.d.ts.map