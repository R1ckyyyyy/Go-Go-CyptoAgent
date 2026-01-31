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
        // Prevent multiple connections in React Strict Mode
        if (socketRef.current?.readyState === WebSocket.OPEN || status === 'connected' || status === 'connecting') {
            return;
        }

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

                // Only reconnect if component is still mounted
                // Simple exponential backoff or static delay
                setTimeout(() => {
                    if (transactionRef.current) {
                        // Ideally we check if we are already connected, but the connectWs function has a guard at top.
                        connectWs();
                    }
                }, 3000);
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
                    console.debug("Received non-JSON message:", event.data);
                }
            };
        };

        // Use a ref to track if effect is active to prevent reconnect during unmount cleanup race
        const transactionRef = { current: true };

        connectWs();

        return () => {
            transactionRef.current = false;
            // In Strict Mode, we might want to keep the connection if it was just established?
            // Actually standard practice is to close. The issue is usually the 'connect' running twice.
            // But we added the guard at the top.

            if (socketRef.current) {
                socketRef.current.close();
                socketRef.current = null;
            }
        };
    }, [url]);

    return { status, socket: socketRef.current };
};
