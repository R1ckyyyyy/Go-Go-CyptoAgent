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
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-zinc-900 p-6 rounded-xl border border-gray-800">
                <h3 className="text-gray-400 text-sm font-medium">总资产 (Total Balance)</h3>
                <p className="text-3xl font-bold mt-2 text-white">
                    ${data.totalBalance?.toLocaleString()}
                    <span className="text-sm font-normal text-gray-500 ml-2">USDT</span>
                </p>
            </div>
            <div className="bg-zinc-900 p-6 rounded-xl border border-gray-800">
                <h3 className="text-gray-400 text-sm font-medium">可用余额 (Available)</h3>
                <p className="text-3xl font-bold mt-2 text-white">
                    ${data.availableBalance?.toLocaleString()}
                </p>
            </div>
            <div className="bg-zinc-900 p-6 rounded-xl border border-gray-800">
                <h3 className="text-gray-400 text-sm font-medium">今日盈亏 (Today PnL)</h3>
                <p className={`text-3xl font-bold mt-2 ${data.todayPnL >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    {data.todayPnL >= 0 ? '+' : ''}{data.todayPnL?.toLocaleString()}
                </p>
            </div>
        </div>
    );
};

export default AccountSummary;
