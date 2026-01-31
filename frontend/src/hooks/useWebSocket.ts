import { useEffect, useRef, useState } from 'react';
import { create } from 'zustand';

interface WebSocketState {
    isConnected: boolean;
    lastMessage: any;
    connect: () => void;
    disconnect: () => void;
}

export const useWebSocketStore = create<WebSocketState>((set) => ({
    isConnected: false,
    lastMessage: null,
    connect: () => { }, // Placeholder, set in component
    disconnect: () => { },
}));

export const useWebSocket = (url: string = '/ws') => {
    const socketRef = useRef<WebSocket | null>(null);
    const { isConnected } = useWebSocketStore();
    const [status, setStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected');

    useEffect(() => {
        const connectWs = () => {
            // Bypass Vite proxy for WebSocket to avoid 403/HMR issues
            // In production, this should use window.location.host if served by Nginx on same port
            // For local dev, backend is reliably at 127.0.0.1:8000
            const wsUrl = `ws://127.0.0.1:8000${url}`;

            setStatus('connecting');
            const ws = new WebSocket(wsUrl);
            socketRef.current = ws;

            ws.onopen = () => {
                console.log('WS Connected');
                setStatus('connected');
                useWebSocketStore.setState({ isConnected: true });
            };

            ws.onclose = () => {
                console.log('WS Disconnected');
                setStatus('disconnected');
                useWebSocketStore.setState({ isConnected: false });
                // Reconnect logic could go here
                setTimeout(connectWs, 5000);
            };

            ws.onerror = (err) => {
                console.error('WS Error', err);
                setStatus('error');
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    useWebSocketStore.setState({ lastMessage: data });
                } catch (e) {
                    // Ignore non-json
                }
            };
        };

        connectWs();

        return () => {
            socketRef.current?.close();
        };
    }, [url]);

    return { status, socket: socketRef.current };
};
