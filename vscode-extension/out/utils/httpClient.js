"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.HttpClient = void 0;
const axios_1 = __importDefault(require("axios"));
class HttpClient {
    constructor(port = 8765) {
        this.port = port;
        this.client = axios_1.default.create({
            baseURL: `http://localhost:${port}`,
            timeout: 5000,
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }
    async checkHealth() {
        try {
            const response = await this.client.get('/status');
            return response.status === 200;
        }
        catch (error) {
            return false;
        }
    }
    async get(path, params) {
        try {
            const response = await this.client.get(path, { params });
            return response.data;
        }
        catch (error) {
            console.error(`GET ${path} failed:`, error);
            throw error;
        }
    }
    async post(path, data) {
        try {
            const response = await this.client.post(path, data);
            return response.data;
        }
        catch (error) {
            console.error(`POST ${path} failed:`, error);
            throw error;
        }
    }
}
exports.HttpClient = HttpClient;
//# sourceMappingURL=httpClient.js.map