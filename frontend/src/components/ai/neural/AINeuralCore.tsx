import React, { useState, useEffect, useRef } from 'react';
import { DecisionTimeline } from './DecisionTimeline';
import { Zap, Activity, Wifi } from 'lucide-react';
import api from '../../../services/api';

// --- Types ---
interface ThoughtMessage {
    type: string;
    sender: string;
    receiver: string;
    content: any;
    timestamp: string;
}

interface Session {
    id: string;
    symbol?: string;
    timestamp: string;
    triggerReason: string;
    data?: any; // [NEW] Input Data Field
    strategy?: string;
    consultants: {
        technical?: any;
        fundamental?: any;
        risk?: any;
    };
    verdict?: {
        action: string;
        confidence: number;
        reason: string;
    };
}

export const AINeuralCore: React.FC = () => {
    const [isConnected, setIsConnected] = useState(false);
    const [sessions, setSessions] = useState<Session[]>([]);
    const [activeSymbols, setActiveSymbols] = useState<string[]>(["BTCUSDT"]);
    const wsRef = useRef<WebSocket | null>(null);

    const SUPPORTED_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "DOGEUSDT"];

    // --- WebSocket Logic ---
    useEffect(() => {
        // [NEW] 1. Load History on Mount
        const loadHistory = async () => {
            try {
                const res = await api.get('/api/ai/decisions?limit=10');
                if (Array.isArray(res.data)) {
                    // Force cast or map to Session
                    const historySessions: Session[] = res.data.map((d: any) => {
                        const output = d.details || {};
                        const input = d.details?.input_data || {};
                        return {
                            id: d.id.toString(),
                            timestamp: d.timestamp,
                            symbol: d.symbol || "BTCUSDT",
                            triggerReason: "Historical Record",
                            strategy: listEmoji(output.thought_process || "Loaded from history"),
                            data: input,
                            consultants: {},
                            verdict: {
                                action: d.action,
                                confidence: d.confidence || 0.9,
                                reason: d.reason
                            }
                        };
                    });

                    // Sort by timestamp
                    setSessions(prev => {
                        // Merge prevents duplicates if needed, but simple prepend is fine for now
                        return [...historySessions.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())];
                    });
                }
            } catch (e) {
                console.error("Failed to load history:", e);
            }
        };
        loadHistory();

        const connect = () => {
            const ws = new WebSocket('ws://127.0.0.1:8000/ws');

            ws.onopen = () => {
                setIsConnected(true);
                console.log('Neural Core connected to Cortex.');
            };

            ws.onclose = () => {
                setIsConnected(false);
                setTimeout(connect, 3000); // Reconnect
            };

            ws.onmessage = (event) => {
                try {
                    const msg = JSON.parse(event.data);
                    if (msg.type === 'THOUGHT_STREAM') {
                        processThought(msg);
                    }
                } catch (e) {
                    console.error("Failed to parse thought:", e);
                }
            };

            wsRef.current = ws;
        };

        connect();
        return () => wsRef.current?.close();
    }, []);

    // --- Message Processing Logic ---
    const processThought = (msg: ThoughtMessage) => {
        setSessions(prev => {
            const newSessions = [...prev];
            let currentSession = newSessions[newSessions.length - 1];

            // 1. Detect New Session Start (Trigger)
            // If message is from Watchdog or User (MANUAL_INTERVENTION)
            // Or if content contains specific Keywords
            const isNewTrigger =
                (typeof msg.content === 'object' && msg.content.type === 'MANUAL_INTERVENTION') ||
                (typeof msg.content === 'object' && msg.content.type === 'PROXIMITY_ALERT');

            if (isNewTrigger || !currentSession) {
                const triggerReason = typeof msg.content === 'object' ? msg.content.reason : "Thinking...";
                // Attempt to find symbol in message content
                const triggerSymbol = (typeof msg.content === 'object' && msg.content.symbol)
                    ? msg.content.symbol
                    : (msg.content && msg.content.trigger === 'MANUAL' ? 'BTCUSDT' : undefined);

                // [NEW] Capture relevant input data
                let inputData = null;
                if (typeof msg.content === 'object') {
                    if (msg.content.technical_summary) inputData = msg.content.technical_summary;
                    else if (msg.content.data) inputData = msg.content.data;
                    else inputData = msg.content; // Fallback to full content
                }

                currentSession = {
                    id: Date.now().toString(),
                    timestamp: new Date().toISOString(),
                    triggerReason: triggerReason,
                    symbol: triggerSymbol,
                    data: inputData, // Assign to session
                    consultants: {}
                };
                newSessions.push(currentSession);
            }

            // 2. Coordinator Strategy (Initial Thought)
            // Backend sends: "content": { "thought_process": "...", "msg": "..." }
            if (msg.sender === 'coordinator' && typeof msg.content === 'object' && msg.content.thought_process) {
                currentSession.strategy = listEmoji(msg.content.thought_process);
            }
            // Fallback for ANALYSIS_REPORT type
            if (msg.type === 'ANALYSIS_REPORT' && typeof msg.content === 'object' && msg.content.thought_process) {
                currentSession.strategy = listEmoji(msg.content.thought_process);
            }

            // 3. Consultant Responses
            if (msg.sender === 'technical_consultant') {
                currentSession.consultants.technical = msg.content;
            }
            if (msg.sender === 'fundamental_consultant') {
                currentSession.consultants.fundamental = msg.content;
            }
            if (msg.sender === 'risk_consultant') {
                currentSession.consultants.risk = msg.content;
            }

            // 5. Verdict (Action)
            // Backend sends ACTION_REQUEST with content = the full result dict
            const isAction = (msg.type === 'ACTION_REQUEST') ||
                (msg.content && msg.content.action && msg.content.action.type);

            if (isAction && typeof msg.content === 'object') {
                const actionObj = msg.content.action || (msg.content.result && msg.content.result.action);
                if (actionObj) {
                    currentSession.verdict = {
                        action: actionObj.type,
                        confidence: 0.9, // Hardcoded in backend currently
                        reason: msg.content.thought_process || "Based on analysis."
                    };
                }
            }

            return newSessions;
        });
    };

    const toggleSymbol = (symbol: string) => {
        setActiveSymbols(prev =>
            prev.includes(symbol)
                ? prev.filter(s => s !== symbol) // Remove
                : [...prev, symbol] // Add
        );
    };

    const handleTrigger = async () => {
        try {
            await api.post('/ai/analyze');
            // Optimistic UI update could happen here, but we wait for WS
        } catch (error) {
            console.error("Failed to trigger analysis", error);
        }
    };

    return (
        <div className="flex h-screen bg-gray-50 text-gray-800 font-sans">
            {/* Main Content */}
            <div className="flex-1 flex flex-col min-w-0">
                {/* Header Toolbar */}
                <div className="h-16 border-b border-gray-200 bg-white flex items-center justify-between px-6 shadow-sm z-10">
                    <div className="flex items-center gap-4">
                        <span className="font-semibold text-lg text-gray-700">实时决策流 (Live Decision Stream)</span>
                        <div className="flex gap-1">
                            {activeSymbols.map(s => (
                                <span key={s} className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded text-xs font-mono">
                                    {s.replace('USDT', '')}
                                </span>
                            ))}
                            {activeSymbols.length === 0 && <span className="text-gray-400 text-xs italic">No Active Streams</span>}
                        </div>
                    </div>
                    <button
                        onClick={handleTrigger}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg shadow-sm flex items-center gap-2 transition-all active:scale-95"
                    >
                        <Zap className="w-4 h-4 fill-white" />
                        立即触发分析 (Trigger)
                    </button>
                </div>

                {/* Timeline Area (Filtered) */}
                <div className="flex-1 bg-gray-50/50 overflow-hidden relative">
                    {/* Only show sessions for current symbol OR system messages */}
                    <DecisionTimeline sessions={sessions.filter(s => !s.symbol || activeSymbols.includes(s.symbol))} />
                </div>
            </div>

            {/* Sidebar (Moved to Right) */}
            <div className="w-64 bg-white border-l border-gray-200 p-4 flex flex-col">
                <div className="mb-8">
                    <h1 className="text-xl font-bold flex items-center gap-2 text-gray-900">
                        <Brain className="w-6 h-6 text-blue-600" />
                        神经中枢
                    </h1>
                    <p className="text-xs text-gray-500 mt-1 uppercase tracking-wider">AI Neural Core v2.0</p>
                </div>

                <div className="space-y-4">
                    <h2 className="text-xs font-semibold text-gray-400 uppercase">活跃单元 (Agents)</h2>

                    {SUPPORTED_SYMBOLS.map(symbol => {
                        const isActive = activeSymbols.includes(symbol);
                        return (
                            <div
                                key={symbol}
                                onClick={() => toggleSymbol(symbol)}
                                className={`border rounded-lg p-3 cursor-pointer transition-all ${isActive
                                    ? 'bg-blue-50 border-blue-200 shadow-sm'
                                    : 'bg-white border-gray-100 hover:border-blue-100 hover:bg-gray-50'
                                    }`}
                            >
                                <div className="flex justify-between items-center mb-1">
                                    <span className={`font-bold ${isActive ? 'text-gray-800' : 'text-gray-500'}`}>
                                        {symbol.replace('USDT', '')}
                                    </span>
                                    {isActive && <Activity className="w-4 h-4 text-green-500" />}
                                </div>
                                <div className={`text-xs ${isActive ? 'text-blue-600' : 'text-gray-400'}`}>
                                    {isActive ? '正在监控中...' : 'Idle'}
                                </div>
                            </div>
                        );
                    })}
                </div>

                <div className="mt-auto">
                    <div className={`flex items-center gap-2 text-xs ${isConnected ? 'text-green-600' : 'text-red-500'}`}>
                        <Wifi className="w-3 h-3" />
                        {isConnected ? 'Neural Link Online' : 'Disconnected'}
                    </div>
                </div>
            </div>
        </div>
    );
};

// Helper to cleanup text
function listEmoji(text: string) {
    return text.replace(/[:：]/g, ': ');
}

// Icon helper
function Brain(props: React.SVGProps<SVGSVGElement>) {
    return (
        <svg
            {...props}
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
        >
            <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z" />
            <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z" />
        </svg>
    );
}
