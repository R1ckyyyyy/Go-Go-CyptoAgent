import axios from 'axios';

const api = axios.create({
    baseURL: '/api', // Nginx proxy handles this
    timeout: 10000,
});

export const systemApi = {
    getStatus: () => api.get('/system/status'),
    startSystem: () => api.post('/system/start'),
    stopSystem: () => api.post('/system/stop'),
};

export const accountApi = {
    getBalance: () => api.get('/account/balance'),
    getPositions: () => api.get('/account/positions'),
    getPerformance: () => api.get('/account/performance'),
};

export const tradingApi = {
    getHistory: () => api.get('/trading/history'),
    // manualOrder...
};

export const aiApi = {
    getDecisions: () => api.get('/ai/decisions'),
    getCommunications: () => api.get('/ai/communications'),
};

export default api;
