import React, { useEffect, useState } from 'react';
import { aiApi } from '../../services/api';
import { Activity, Radio, Cpu } from 'lucide-react';

interface KnowledgePanelProps {
    selectedNodeId: string | null;
}

// Simple Modal Component
const Modal: React.FC<{ isOpen: boolean; onClose: () => void; title: string; content: any }> = ({ isOpen, onClose, title, content }) => {
    if (!isOpen) return null;
    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={onClose}>
            <div className="bg-zinc-900 border border-slate-700 rounded-xl w-[600px] max-h-[80vh] flex flex-col shadow-2xl" onClick={e => e.stopPropagation()}>
                <div className="flex justify-between items-center p-4 border-b border-slate-700">
                    <h3 className="font-bold text-white">{title}</h3>
                    <button onClick={onClose} className="text-slate-400 hover:text-white">✕</button>
                </div>
                <div className="p-4 overflow-y-auto font-mono text-xs text-slate-300 whitespace-pre-wrap">
                    {typeof content === 'object' ? JSON.stringify(content, null, 2) : content}
                </div>
            </div>
        </div>
    );
};

const KnowledgePanel: React.FC<KnowledgePanelProps> = ({ selectedNodeId }) => {
    const [decisions, setDecisions] = useState<any[]>([]);
    const [triggers, setTriggers] = useState<any[]>([]);
    const [modalData, setModalData] = useState<{ title: string, content: any } | null>(null);

    const fetchData = async () => {
        try {
            // Parallel fetch
            const [decisionsRes, triggersRes] = await Promise.all([
                aiApi.getDecisions(),
                aiApi.getTriggers()
            ]);
            setDecisions(decisionsRes.data);
            setTriggers(triggersRes.data);
        } catch (error) {
            console.error("Failed to fetch knowledge panel data:", error);
        }
    };

    useEffect(() => {
        if (selectedNodeId === 'coordinator' || selectedNodeId === null) {
            fetchData();
            const interval = setInterval(fetchData, 3000); // Real-time update
            return () => clearInterval(interval);
        }
    }, [selectedNodeId]);

    if (selectedNodeId && selectedNodeId !== 'coordinator') {
        return (
            <div className="glass-panel w-full h-full p-6 text-zinc-800 overflow-y-auto">
                <h2 className="text-xl font-medium mb-4 flex items-center text-zinc-700">
                    <Cpu className="mr-2" />
                    顾问节点 (Consultant Node)
                </h2>
                <div className="p-4 bg-white/50 rounded border border-black/5">
                    <p className="text-sm text-zinc-600">
                        该节点处于 <span className="text-zinc-900 font-bold">被动响应模式</span>。仅在 Coordinator 请求时工作。
                    </p>
                </div>
            </div>
        );
    }

    return (
        <>
            <Modal
                isOpen={!!modalData}
                onClose={() => setModalData(null)}
                title={modalData?.title || ''}
                content={modalData?.content}
            />

            <div className="glass-panel w-full h-full p-4 text-zinc-800 overflow-y-auto custom-scrollbar flex flex-col">
                <h2 className="text-xl font-medium mb-6 flex items-center text-zinc-800">
                    <Activity className="mr-2 text-zinc-500" />
                    系统意识流 (System Consciousness)
                </h2>

                {/* Section 1: Watchdog Triggers */}
                <div className="mb-8 flex-shrink-0">
                    <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-wider mb-3 flex items-center">
                        <Radio className="w-3 h-3 mr-2" /> 活跃触发器 (Active Triggers)
                    </h3>

                    {triggers.length === 0 ? (
                        <div className="p-4 bg-zinc-50/50 rounded border border-dashed border-zinc-200 text-zinc-400 text-sm text-center italic">
                            暂无活跃触发器 (No Triggers)
                        </div>
                    ) : (
                        <div className="space-y-2">
                            {triggers.map((t) => (
                                <div
                                    key={t.id}
                                    onClick={() => setModalData({ title: `触发器详情: ${t.description}`, content: t })}
                                    className="p-3 bg-white/40 rounded border border-black/5 hover:bg-white hover:border-zinc-300 transition-all cursor-pointer group shadow-sm"
                                >
                                    <div className="flex justify-between items-start mb-1">
                                        <span className="text-zinc-600 font-mono text-[10px] font-bold px-1.5 py-0.5 bg-zinc-100 rounded">
                                            {t.type}
                                        </span>
                                        <span className="text-[10px] text-zinc-400">{new Date(t.created_at).toLocaleTimeString()}</span>
                                    </div>
                                    <p className="text-sm text-zinc-700 mt-1 line-clamp-1 group-hover:text-zinc-900 transition-colors">{t.description}</p>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Section 2: Thinking Chain */}
                <div className="flex-1 overflow-y-auto custom-scrollbar">
                    <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-wider mb-3 flex items-center sticky top-0 bg-white/80 backdrop-blur py-2 z-10">
                        <Cpu className="w-3 h-3 mr-2" /> 决策日志 (Decision Log)
                    </h3>

                    <div className="space-y-4 px-1">
                        {decisions.map((d) => (
                            <div key={d.id} className="relative pl-4 border-l border-zinc-200 pb-1 group hover:border-zinc-400 transition-colors">
                                <div className={`absolute -left-[5px] top-1.5 w-2.5 h-2.5 rounded-full border border-white shadow-sm ${d.action === 'BUY' ? 'bg-emerald-500' : d.action === 'SELL' ? 'bg-rose-500' : 'bg-blue-500'
                                    }`}></div>

                                <div
                                    onClick={() => setModalData({ title: `决策详情 #${d.id}`, content: d })}
                                    className="hover:bg-white/60 rounded-lg p-2 text-sm cursor-pointer transition-all"
                                >
                                    <div className="flex justify-between items-center mb-1">
                                        <span className={`font-bold ${d.action === 'BUY' ? 'text-emerald-600' :
                                                d.action === 'SELL' ? 'text-rose-600' :
                                                    'text-blue-600'
                                            }`}>
                                            {d.action}
                                        </span>
                                        <span className="text-[10px] text-zinc-400 font-mono">
                                            {new Date(d.timestamp).toLocaleTimeString()}
                                        </span>
                                    </div>
                                    <p className="text-zinc-600 mb-2 leading-relaxed text-xs opacity-90 group-hover:text-zinc-800">{d.reason}</p>

                                    {d.details && d.details.technical_summary && (
                                        <div className="grid grid-cols-2 gap-2 text-[10px] bg-zinc-50 p-2 rounded border border-black/5 text-zinc-500 font-mono">
                                            <div>RSI: <span className="text-zinc-700">{d.details.technical_summary.rsi_1h}</span></div>
                                            <div>Trend: <span className="text-zinc-700">{d.details.technical_summary.trend_1h}</span></div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </>
    );
};

export default KnowledgePanel;
