import React, { useEffect, useState } from 'react';
import { accountApi } from '../../services/api';
import type { AccountSummary as AccountSummaryType } from '../../types';

const AccountSummary: React.FC = () => {
    const [data, setData] = useState<AccountSummaryType | null>(null);

    useEffect(() => {
        accountApi.getBalance()
            .then(res => {
                // Map snake_case from API to camelCase for frontend
                const apiData = res.data as any;
                setData({
                    totalBalance: apiData.total_balance,
                    availableBalance: apiData.available_balance,
                    todayPnL: apiData.today_pnl,
                    totalPnL: apiData.total_pnl
                });
            })
            .catch(err => {
                console.error("Failed to fetch account balance:", err);
            });
    }, []);

    if (!data) return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6 animate-pulse">
            {[1, 2, 3].map(i => <div key={i} className="h-32 bg-gray-900 rounded-xl border border-gray-800"></div>)}
        </div>
    );

    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="glass-card p-6 rounded-2xl relative overflow-hidden group">
                <h3 className="text-zinc-500 text-sm font-medium uppercase tracking-wider">总资产 (Total Balance)</h3>
                <p className="text-4xl font-light mt-2 text-zinc-800 tracking-tight">
                    <span className="text-2xl text-zinc-400 mr-1">$</span>
                    {data.totalBalance?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    <span className="text-sm font-normal text-zinc-500 ml-2">USDT</span>
                </p>
            </div>

            <div className="glass-card p-6 rounded-2xl relative overflow-hidden group">
                <h3 className="text-zinc-500 text-sm font-medium uppercase tracking-wider">可用余额 (Available)</h3>
                <p className="text-4xl font-light mt-2 text-zinc-800 tracking-tight">
                    <span className="text-2xl text-zinc-400 mr-1">$</span>
                    {data.availableBalance?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
            </div>

            <div className="glass-card p-6 rounded-2xl relative overflow-hidden group">
                <h3 className="text-zinc-500 text-sm font-medium uppercase tracking-wider">今日盈亏 (24h PnL)</h3>
                <p className={`text-4xl font-light mt-2 tracking-tight ${data.todayPnL >= 0 ? 'text-zinc-800' : 'text-zinc-800'}`}>
                    <span className={`text-sm mr-2 px-1.5 py-0.5 rounded border ${data.todayPnL >= 0
                            ? 'border-emerald-200 text-emerald-600 bg-emerald-50'
                            : 'border-rose-200 text-rose-600 bg-rose-50'
                        }`}>
                        {data.todayPnL >= 0 ? '▲' : '▼'}
                    </span>
                    {data.todayPnL?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    <span className="text-sm font-normal text-zinc-500 ml-2">USDT</span>
                </p>
            </div>
        </div>
    );
};

export default AccountSummary;
