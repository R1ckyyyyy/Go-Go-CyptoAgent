import React, { useEffect, useState } from 'react';
import { RefreshCw, ArrowUpRight, ArrowDownLeft } from 'lucide-react';
import { tradingApi } from '../../services/api';

interface Trade {
    id: number;
    symbol: string;
    side: string;
    amount: number;
    price: number;
    timestamp: string;
    status: string;
}

const TradeHistory: React.FC = () => {
    const [trades, setTrades] = useState<Trade[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchTrades = () => {
        tradingApi.getTradeHistory()
            .then(res => {
                setTrades(res.data);
                setLoading(false);
            })
            .catch(err => {
                console.error("Failed to fetch trades:", err);
                setLoading(false);
            });
    };

    useEffect(() => {
        fetchTrades();
        const interval = setInterval(fetchTrades, 5000); // Poll every 5s
        return () => clearInterval(interval);
    }, []);

    const formatTime = (isoString: string) => {
        const date = new Date(isoString);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    };

    return (
        <div className="glass-panel p-6 overflow-hidden flex flex-col h-full">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-zinc-500 font-medium text-sm flex items-center uppercase tracking-wider">
                    <RefreshCw size={14} className={`mr-2 ${loading ? 'animate-spin' : ''}`} />
                    Recent Activity
                </h3>
                <span className="text-xs text-zinc-400 bg-zinc-100 px-2 py-1 rounded-full">
                    {trades.length} Trades
                </span>
            </div>

            <div className="overflow-y-auto pr-2 custom-scrollbar flex-1">
                {trades.length === 0 ? (
                    <div className="text-center py-8 text-zinc-400 text-sm">
                        No recent trades
                    </div>
                ) : (
                    <div className="space-y-3">
                        {trades.map((trade) => (
                            <div key={trade.id} className="flex items-center justify-between p-3 rounded-lg hover:bg-zinc-50/80 transition-colors border border-transparent hover:border-zinc-100 group">
                                <div className="flex items-center space-x-3">
                                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${trade.side.includes('BUY')
                                            ? 'bg-emerald-50 text-emerald-500'
                                            : 'bg-rose-50 text-rose-500'
                                        }`}>
                                        {trade.side.includes('BUY') ? <ArrowDownLeft size={16} /> : <ArrowUpRight size={16} />}
                                    </div>
                                    <div>
                                        <div className="font-bold text-zinc-800 text-sm">{trade.symbol}</div>
                                        <div className="text-xs text-zinc-400">{formatTime(trade.timestamp)}</div>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className="font-mono text-sm font-medium text-zinc-900">
                                        {trade.amount} @ {trade.price.toLocaleString()}
                                    </div>
                                    <div className={`text-xs font-bold ${trade.side.includes('BUY') ? 'text-emerald-500' : 'text-rose-500'
                                        }`}>
                                        {trade.side.replace('TradeSide.', '')}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default TradeHistory;
