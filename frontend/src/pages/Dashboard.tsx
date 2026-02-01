import React from 'react';
import AccountSummary from '../components/dashboard/AccountSummary';
import PositionTable from '../components/dashboard/PositionTable';
import EquityCurve from '../components/dashboard/EquityCurve';
import MarketSnapshot from '../components/dashboard/MarketSnapshot';
import TradeHistory from '../components/dashboard/TradeHistory';

const Dashboard: React.FC = () => {
    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-zinc-900 mb-4">仪表盘 (Dashboard)</h1>
            <AccountSummary />

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[320px]">
                <div className="lg:col-span-2 h-full">
                    <EquityCurve />
                </div>
                <div className="h-full">
                    <MarketSnapshot />
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[400px]">
                <div className="lg:col-span-2 h-full">
                    <PositionTable />
                </div>
                <div className="h-full">
                    <TradeHistory />
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
