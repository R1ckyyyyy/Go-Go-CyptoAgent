import React, { useEffect, useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { accountApi } from '../../services/api';
import { TrendingUp, Maximize2 } from 'lucide-react';

interface EquityData {
    date: string;
    value: number;
}

const EquityCurve: React.FC = () => {
    const [data, setData] = useState<EquityData[]>([]);
    const [totalEquity, setTotalEquity] = useState<number>(0);
    const [pnlPercent, setPnlPercent] = useState<number>(0);

    useEffect(() => {
        const fetchData = () => {
            accountApi.getEquityHistory()
                .then(res => {
                    setData(res.data);
                    if (res.data.length > 0) {
                        const current = res.data[res.data.length - 1].value;
                        const start = res.data[0].value;
                        setTotalEquity(current);
                        setPnlPercent(((current - start) / start) * 100);
                    }
                })
                .catch(console.error);
        };

        fetchData();
        const interval = setInterval(fetchData, 60000); // Poll every 60s
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="glass-panel p-6 h-full flex flex-col relative overflow-hidden group">
            {/* Header */}
            <div className="flex justify-between items-start mb-6">
                <div>
                    <h3 className="text-zinc-500 font-medium text-sm flex items-center mb-1">
                        <TrendingUp size={16} className="mr-2 text-indigo-500" />
                        总资产趋势 (Equity Curve)
                    </h3>
                    <div className="flex items-baseline">
                        <span className="text-3xl font-bold text-zinc-900 tracking-tight mr-3">
                            ${totalEquity.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                        </span>
                        <span className={`text-sm font-bold px-2 py-0.5 rounded-full ${pnlPercent >= 0
                            ? 'bg-emerald-50 text-emerald-600 border border-emerald-100'
                            : 'bg-rose-50 text-rose-600 border border-rose-100'
                            }`}>
                            {pnlPercent >= 0 ? '+' : ''}{pnlPercent.toFixed(2)}% (30d)
                        </span>
                    </div>
                </div>
                <button className="p-2 text-zinc-400 hover:text-zinc-600 hover:bg-zinc-100 rounded-lg transition-colors opacity-0 group-hover:opacity-100">
                    <Maximize2 size={16} />
                </button>
            </div>

            {/* Chart */}
            <div className="flex-1 w-full min-h-[200px]">
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={data}>
                        <defs>
                            <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.2} />
                                <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <XAxis
                            dataKey="date"
                            axisLine={false}
                            tickLine={false}
                            tick={{ fontSize: 10, fill: '#a1a1aa' }}
                            minTickGap={30}
                        />
                        <YAxis
                            hide
                            domain={['auto', 'auto']}
                        />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: 'rgba(255, 255, 255, 0.9)',
                                borderRadius: '8px',
                                border: '1px solid #e4e4e7',
                                boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                                fontSize: '12px'
                            }}
                            itemStyle={{ color: '#18181b', fontWeight: 'bold' }}
                            formatter={(value: number | undefined) => [`$${(value || 0).toLocaleString()}`, 'Equity']}
                        />
                        <Area
                            type="monotone"
                            dataKey="value"
                            stroke="#6366f1"
                            strokeWidth={2}
                            fillOpacity={1}
                            fill="url(#colorValue)"
                            animationDuration={1500}
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default EquityCurve;
