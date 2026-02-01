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
    getEquityHistory: () => api.get('/account/equity-history'),
    getMarketSummary: () => api.get('/account/market-summary'),
};

export const tradingApi = { // 获取历史成交
    getTradeHistory: () => api.get('/trading/history'),

    // 获取活动订单
    getOpenOrders: () => api.get('/trading/orders'),
    // manualOrder...
};

export const aiApi = {
    getDecisions: () => api.get('/ai/decisions'),
    getCommunications: () => api.get('/ai/communications'),
    getTreeStructure: () => api.get('/ai/tree-structure'),
    getNodeStatus: () => api.get('/ai/status'),
    getTriggers: () => api.get('/ai/triggers'),
    triggerAnalysis: () => api.post('/ai/analyze'),
};

export default api;
