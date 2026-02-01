import React, { useEffect, useState } from 'react';
import { accountApi } from '../../services/api';
import { TrendingUp, TrendingDown, Activity } from 'lucide-react';

interface MarketTicker {
    symbol: string;
    price: number;
    change_24h: number;
    volume_24h: string;
    trend: number[];
}

const MarketSnapshot: React.FC = () => {
    const [data, setData] = useState<MarketTicker[]>([]);

    useEffect(() => {
        const fetchData = () => {
            accountApi.getMarketSummary()
                .then(res => setData(res.data))
                .catch(console.error);
        };

        fetchData(); // Initial load
        const interval = setInterval(fetchData, 3000); // Poll every 3s
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="glass-panel p-6 h-full flex flex-col justify-center">
            <h3 className="text-zinc-500 font-medium text-sm mb-4 flex items-center uppercase tracking-wider">
                <Activity size={14} className="mr-2" />
                Market Overview
            </h3>

            <div className="space-y-5">
                {data.map((item) => (
                    <div key={item.symbol} className="flex items-center justify-between group cursor-pointer hover:bg-zinc-50 rounded-lg p-2 -mx-2 transition-colors">
                        <div className="flex items-center">
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 font-bold text-xs border ${item.symbol === 'BTC' ? 'bg-orange-50 text-orange-500 border-orange-100' :
                                item.symbol === 'ETH' ? 'bg-slate-50 text-slate-500 border-slate-200' :
                                    'bg-purple-50 text-purple-500 border-purple-100'
                                }`}>
                                {item.symbol[0]}
                            </div>
                            <div>
                                <div className="font-bold text-zinc-800">{item.symbol}</div>
                                <div className="text-xs text-zinc-400 font-mono">{item.volume_24h} Vol</div>
                            </div>
                        </div>

                        <div className="text-right">
                            <div className="font-mono font-medium text-zinc-900">${item.price.toLocaleString()}</div>
                            <div className={`text-xs font-bold flex items-center justify-end ${item.change_24h >= 0 ? 'text-emerald-500' : 'text-rose-500'
                                }`}>
                                {item.change_24h >= 0 ? <TrendingUp size={10} className="mr-1" /> : <TrendingDown size={10} className="mr-1" />}
                                {Math.abs(item.change_24h)}%
                            </div>
                        </div>
                    </div>
                ))}

                {/* Sentiment Meter (Static for now, can be dynamic later) */}
                <div className="mt-6 pt-4 border-t border-dashed border-zinc-200">
                    <div className="flex justify-between items-center mb-2">
                        <span className="text-xs text-zinc-400 font-medium">MARKET SENTIMENT</span>
                        <span className="text-xs text-emerald-600 font-bold bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-100">GREED (68)</span>
                    </div>
                    <div className="h-1.5 w-full bg-zinc-100 rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-emerald-400 to-emerald-600 w-[68%] rounded-full shadow-sm"></div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MarketSnapshot;
