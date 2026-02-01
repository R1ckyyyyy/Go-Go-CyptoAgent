import React, { useEffect, useRef, useState } from 'react';
import { Terminal, MessageSquare, Bot, BrainCircuit } from 'lucide-react';
// import { cn } from '../../lib/utils'; // Assuming you have utils, if not I'll inline. 
// Actually I don't know if lib/utils exists. Use inline classes.

interface ThoughtLog {
    id: number;
    timestamp: string;
    sender: string;
    content: any;
    type: string;
}

const ThoughtStream: React.FC = () => {
    const [logs, setLogs] = useState<ThoughtLog[]>([]);
    const bottomRef = useRef<HTMLDivElement>(null);
    const [isConnected, setIsConnected] = useState(false);

    useEffect(() => {
        // Connect to WebSocket
        const socketUrl = "ws://localhost:8000/ws";
        let ws: WebSocket;

        const connect = () => {
            ws = new WebSocket(socketUrl);

            ws.onopen = () => {
                setIsConnected(true);
                addLog("System", "Neural Link Established.");
            };

            ws.onclose = () => {
                setIsConnected(false);
                setTimeout(connect, 3000); // Reconnect
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.type === 'THOUGHT_STREAM') {
                        addLog(data.sender, data.content);
                    } else if (data.type === 'SYSTEM_EVENT') {
                        addLog("System", data.message);
                    }
                } catch (e) { }
            };
        };

        connect();

        return () => {
            ws?.close();
        };
    }, []);

    const addLog = (sender: string, content: any) => {
        setLogs(prev => [...prev.slice(-49), {
            id: Date.now() + Math.random(),
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
            sender,
            content,
            type: 'info'
        }]);
    };

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [logs]);

    // Helpers for rendering
    const getAvatar = (sender: string) => {
        if (sender === 'System') return <Terminal size={14} />;
        if (sender === 'coordinator') return <BrainCircuit size={16} />;
        if (sender.includes('consultant')) return <Bot size={16} />;
        return <MessageSquare size={16} />;
    };

    const getSenderName = (sender: string) => {
        if (sender === 'coordinator') return 'Coordinator (决策大脑)';
        if (sender === 'technical') return 'Technical Analyst';
        if (sender === 'fundamental') return 'Fundamental Analyst';
        if (sender === 'risk_management') return 'Risk Manager';
        return sender.toUpperCase();
    };

    const getBubbleColor = (sender: string) => {
        if (sender === 'coordinator') return 'bg-indigo-600 text-white';
        if (sender === 'System') return 'bg-zinc-800 text-zinc-400 border border-zinc-700 font-mono text-xs py-1';
        if (sender === 'technical') return 'bg-emerald-600 text-white';
        if (sender === 'risk_management') return 'bg-rose-600 text-white';
        return 'bg-blue-600 text-white';
    };

    return (
        <div className="flex flex-col h-full bg-zinc-50 dark:bg-zinc-950 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-xl overflow-hidden font-sans">
            {/* Header */}
            <div className="p-3 bg-white dark:bg-zinc-900 border-b border-zinc-200 dark:border-zinc-800 flex items-center justify-between shadow-sm z-10">
                <div className="flex items-center text-zinc-700 dark:text-zinc-200">
                    <MessageSquare size={16} className="mr-2 text-indigo-500" />
                    <span className="font-bold text-sm">AI 协作对话 (Neural Chat)</span>
                </div>
                <div className="flex items-center space-x-2">
                    <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`}></span>
                    <span className="text-[10px] uppercase font-bold text-zinc-400">
                        {isConnected ? 'ONLINE' : 'OFFLINE'}
                    </span>
                </div>
            </div>

            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-zinc-50/50 dark:bg-zinc-950/50 scrollbar-hide">
                {logs.length === 0 && (
                    <div className="h-full flex flex-col items-center justify-center text-zinc-400 space-y-2 opacity-50">
                        <Bot size={48} strokeWidth={1} />
                        <p className="text-sm">Waiting for AI activity...</p>
                    </div>
                )}

                {logs.map((log) => {
                    const isSystem = log.sender === 'System';

                    if (isSystem) {
                        return (
                            <div key={log.id} className="flex justify-center my-2">
                                <span className={`${getBubbleColor(log.sender)} px-3 rounded-full flex items-center gap-2`}>
                                    <Terminal size={10} />
                                    {typeof log.content === 'string' ? log.content : JSON.stringify(log.content)}
                                </span>
                            </div>
                        );
                    }

                    return (
                        <div key={log.id} className="flex flex-col space-y-1 animate-fade-in-up">
                            {/* Sender Info */}
                            <div className="flex items-center gap-2 ml-1">
                                <span className={`p-1 rounded-full bg-zinc-200 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400`}>
                                    {getAvatar(log.sender)}
                                </span>
                                <span className="text-xs font-bold text-zinc-500 dark:text-zinc-400">
                                    {getSenderName(log.sender)}
                                </span>
                                <span className="text-[10px] text-zinc-400 ml-auto mr-2">
                                    {log.timestamp}
                                </span>
                            </div>

                            {/* Bubble */}
                            <div className={`relative px-4 py-3 rounded-2xl rounded-tl-none shadow-sm max-w-[90%] text-sm leading-relaxed ${getBubbleColor(log.sender)}`}>
                                <div className="whitespace-pre-wrap break-words">
                                    {/* Handle Structured Content */}
                                    {typeof log.content === 'object' ? (
                                        <>
                                            {log.content.msg && <div className="font-medium mb-1">{log.content.msg}</div>}
                                            {log.content.thought_process && (
                                                <div className="text-xs opacity-90 italic bg-black/10 p-2 rounded mt-1 border-l-2 border-white/30">
                                                    "{log.content.thought_process}"
                                                </div>
                                            )}
                                            {log.content.data_snapshot && (
                                                <div className="mt-2 text-[10px] font-mono bg-black/20 p-2 rounded">
                                                    {JSON.stringify(log.content.data_snapshot)}
                                                </div>
                                            )}
                                        </>
                                    ) : (
                                        log.content
                                    )}
                                </div>
                            </div>
                        </div>
                    );
                })}
                <div ref={bottomRef} className="h-4" />
            </div>
        </div>
    );
};

export default ThoughtStream;
