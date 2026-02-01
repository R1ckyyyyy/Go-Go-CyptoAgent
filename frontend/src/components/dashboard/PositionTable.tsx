import React, { useEffect, useState } from 'react';
import { accountApi } from '../../services/api';
import type { Position } from '../../types';

const PositionTable: React.FC = () => {
    const [positions, setPositions] = useState<Position[]>([]);

    useEffect(() => {
        accountApi.getPositions()
            .then(res => {
                const mappedData = (res.data as any[]).map(item => ({
                    symbol: item.symbol,
                    amount: item.amount,
                    avgPrice: item.avg_price,
                    currentPrice: item.current_price,
                    pnl: item.pnl
                }));
                setPositions(mappedData);
            })
            .catch(console.error);
    }, []);

    return (
        <div className="glass-panel rounded-2xl overflow-hidden shadow-sm">
            <div className="px-6 py-5 border-b border-black/5 flex justify-between items-center bg-white/50">
                <h3 className="font-bold text-lg text-zinc-900 flex items-center">
                    <span className="w-2 h-6 bg-zinc-800 rounded-full mr-3"></span>
                    当前持仓 (Active Positions)
                </h3>
                <span className="text-xs text-zinc-500 bg-zinc-100 px-2 py-1 rounded border border-zinc-200">Real-time</span>
            </div>
            <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                    <thead className="bg-zinc-50/50 text-zinc-500 text-xs uppercase tracking-wider border-b border-black/5">
                        <tr>
                            <th className="px-6 py-4 font-semibold">交易对 (Symbol)</th>
                            <th className="px-6 py-4 font-semibold">持仓量 (Amount)</th>
                            <th className="px-6 py-4 font-semibold">均价 (Avg)</th>
                            <th className="px-6 py-4 font-semibold">现价 (Mark)</th>
                            <th className="px-6 py-4 font-semibold text-right">未实现盈亏 (PnL)</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-black/5">
                        {positions.length === 0 ? (
                            <tr>
                                <td colSpan={5} className="px-6 py-12 text-center">
                                    <div className="flex flex-col items-center justify-center text-zinc-400">
                                        <div className="w-16 h-16 bg-zinc-100 rounded-full flex items-center justify-center mb-4 text-2xl grayscale opacity-50">🧸</div>
                                        <p>暂无活跃持仓 (Empty)</p>
                                    </div>
                                </td>
                            </tr>
                        ) : (
                            positions.map((pos) => (
                                <tr key={pos.symbol} className="hover:bg-white/60 transition-colors group">
                                    <td className="px-6 py-4 font-medium text-zinc-900">
                                        <div className="flex items-center">
                                            <div className="w-8 h-8 rounded-full bg-zinc-100 text-zinc-600 flex items-center justify-center text-xs font-bold mr-3 border border-zinc-200">
                                                {pos.symbol.substring(0, 1)}
                                            </div>
                                            {pos.symbol}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-zinc-700 font-mono">{pos.amount}</td>
                                    <td className="px-6 py-4 text-zinc-500 font-mono">${pos.avgPrice.toLocaleString()}</td>
                                    <td className="px-6 py-4 text-zinc-900 font-mono font-medium">${pos.currentPrice.toLocaleString()}</td>
                                    <td className="px-6 py-4 text-right">
                                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${pos.pnl >= 0
                                            ? 'bg-emerald-50 text-emerald-600 border-emerald-200'
                                            : 'bg-rose-50 text-rose-600 border-rose-200'
                                            }`}>
                                            {pos.pnl >= 0 ? '+' : ''}{pos.pnl.toFixed(2)}
                                        </span>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default PositionTable;
