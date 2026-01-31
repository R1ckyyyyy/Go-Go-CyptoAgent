import React, { useEffect, useState } from 'react';
import { accountApi } from '../../services/api';
import type { AccountSummary as AccountSummaryType } from '../../types';

const AccountSummary: React.FC = () => {
    const [data, setData] = useState<AccountSummaryType | null>(null);

    useEffect(() => {
        accountApi.getBalance().then(res => setData(res.data)).catch(err => {
            console.error(err);
            // Fallback mock data if API fails or is empty for demo
            setData({
                totalBalance: 0,
                availableBalance: 0,
                todayPnL: 0,
                totalPnL: 0,
                currency: 'USDT'
            } as any);
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
                <h3 className="text-gray-400 text-sm font-medium">Total Balance</h3>
                <p className="text-3xl font-bold mt-2 text-white">
                    ${data.totalBalance?.toLocaleString()}
                    <span className="text-sm font-normal text-gray-500 ml-2">USDT</span>
                </p>
            </div>
            <div className="bg-zinc-900 p-6 rounded-xl border border-gray-800">
                <h3 className="text-gray-400 text-sm font-medium">Available</h3>
                <p className="text-3xl font-bold mt-2 text-white">
                    ${data.availableBalance?.toLocaleString()}
                </p>
            </div>
            <div className="bg-zinc-900 p-6 rounded-xl border border-gray-800">
                <h3 className="text-gray-400 text-sm font-medium">Today PnL</h3>
                <p className={`text-3xl font-bold mt-2 ${data.todayPnL >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    {data.todayPnL >= 0 ? '+' : ''}{data.todayPnL?.toLocaleString()}
                </p>
            </div>
        </div>
    );
};

export default AccountSummary;
