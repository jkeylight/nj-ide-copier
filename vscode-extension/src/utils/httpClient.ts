import axios, { AxiosInstance } from 'axios';

export class HttpClient {
    private client: AxiosInstance;

    constructor(private port: number = 8765) {
        this.client = axios.create({
            baseURL: `http://localhost:${port}`,
            timeout: 5000,
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }

    async checkHealth(): Promise<boolean> {
        try {
            const response = await this.client.get('/status');
            return response.status === 200;
        } catch (error) {
            return false;
        }
    }

    async get(path: string, params?: any): Promise<any> {
        try {
            const response = await this.client.get(path, { params });
            return response.data;
        } catch (error) {
            console.error(`GET ${path} failed:`, error);
            throw error;
        }
    }

    async post(path: string, data?: any): Promise<any> {
        try {
            const response = await this.client.post(path, data);
            return response.data;
        } catch (error) {
            console.error(`POST ${path} failed:`, error);
            throw error;
        }
    }
}
