import React, { useRef, useEffect } from 'react';
import { ConsultantCard } from './ConsultantCard';
import { Zap, Brain, CheckCircle, Clock } from 'lucide-react';

interface Session {
    id: string;
    timestamp: string;
    triggerReason: string;
    strategy?: string;
    data?: any; // [NEW] Input Data
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

interface DecisionTimelineProps {
    sessions: Session[];
}

export const DecisionTimeline: React.FC<DecisionTimelineProps> = ({ sessions }) => {
    const bottomRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom when new session arrives
    useEffect(() => {
        if (bottomRef.current) {
            bottomRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [sessions]);

    if (sessions.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-gray-400 opacity-60">
                <Brain className="w-16 h-16 mb-4" />
                <p>等待神经元激活...</p>
                <p className="text-sm">点击 "立即触发分析" 唤醒 AI</p>
            </div>
        );
    }

    return (
        <div className="flex-1 p-8 space-y-8 overflow-y-auto">
            {sessions.map((session, index) => (
                <div key={session.id} className="animate-in fade-in slide-in-from-bottom-4 duration-500">

                    {/* 1. Trigger Node */}
                    <div className="relative pl-8 border-l-2 border-gray-200 pb-6">
                        <div className="absolute -left-[9px] top-0 w-4 h-4 rounded-full bg-gray-300 border-2 border-white"></div>
                        <div className="mb-1 text-xs text-gray-400 flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {new Date(session.timestamp).toLocaleTimeString()}
                        </div>
                        <div className="bg-gray-50 p-3 rounded border border-gray-200 inline-block">
                            <div className="flex items-center gap-2">
                                <Zap className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                                <span className="font-bold text-gray-700">触发原因:</span>
                                <span className="text-gray-600">{session.triggerReason}</span>
                            </div>
                            {session.data && (
                                <div className="mt-2 pt-2 border-t border-gray-200 text-xs font-mono text-gray-500 bg-gray-100 p-2 rounded">
                                    <div className="font-semibold mb-1">Input Data:</div>
                                    <pre className="whitespace-pre-wrap break-all">
                                        {JSON.stringify(session.data, null, 2)}
                                    </pre>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* 2. Coordinator Strategy */}
                    {session.strategy && (
                        <div className="relative pl-8 border-l-2 border-blue-200 pb-6">
                            <div className="absolute -left-[9px] top-0 w-4 h-4 rounded-full bg-blue-500 ring-4 ring-blue-50"></div>
                            <h3 className="font-bold text-gray-800 mb-2 flex items-center gap-2">
                                <Brain className="w-4 h-4 text-blue-600" />
                                协调中枢策略 (Coordinator Strategy)
                            </h3>
                            <div className="text-gray-600 italic border-l-4 border-blue-400 pl-4 py-2 bg-blue-50 rounded-r text-sm">
                                "{session.strategy}"
                            </div>
                        </div>
                    )}

                    {/* 3. Consultants Grid */}
                    {(session.consultants.technical || session.consultants.fundamental || session.consultants.risk) && (
                        <div className="relative pl-8 border-l-2 border-purple-200 pb-6">
                            <div className="absolute -left-[9px] top-0 w-4 h-4 rounded-full bg-purple-500 ring-4 ring-purple-50"></div>
                            <h3 className="font-bold text-gray-800 mb-4 text-sm uppercase tracking-wider">专家顾问团分析</h3>

                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <ConsultantCard
                                    role="technical"
                                    content={session.consultants.technical}
                                    status={session.consultants.technical ? 'done' : 'thinking'}
                                />
                                <ConsultantCard
                                    role="fundamental"
                                    content={session.consultants.fundamental}
                                    status={session.consultants.fundamental ? 'done' : 'thinking'}
                                />
                                <ConsultantCard
                                    role="risk_management"
                                    content={session.consultants.risk}
                                    status={session.consultants.risk ? 'done' : 'thinking'}
                                />
                            </div>
                        </div>
                    )}

                    {/* 4. Final Verdict */}
                    {session.verdict && (
                        <div className="relative pl-8">
                            <div className="absolute -left-[9px] top-0 w-4 h-4 rounded-full bg-yellow-500 ring-4 ring-yellow-50"></div>
                            <div className="bg-gradient-to-r from-gray-900 to-gray-800 text-white p-6 rounded-xl shadow-xl flex justify-between items-center border border-gray-700">
                                <div>
                                    <div className="text-gray-400 text-xs uppercase tracking-widest mb-1">最终决策 (Final Verdict)</div>
                                    <div className={`text-4xl font-black ${session.verdict.action === 'BUY' ? 'text-green-400' :
                                        session.verdict.action === 'SELL' ? 'text-red-400' : 'text-yellow-400'
                                        }`}>
                                        {session.verdict.action}
                                    </div>
                                    <p className="text-gray-300 text-sm mt-2 max-w-md">
                                        <span className="opacity-70">理由:</span> {session.verdict.reason}
                                    </p>
                                </div>
                                <div className="text-right">
                                    <div className="text-3xl font-mono font-bold">{Math.round(session.verdict.confidence * 100)}%</div>
                                    <div className="text-xs text-gray-500 uppercase">置信度</div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            ))}
            <div ref={bottomRef} />
        </div>
    );
};
