import React from 'react';
import AccountSummary from '../components/dashboard/AccountSummary';
import PositionTable from '../components/dashboard/PositionTable';

const Dashboard: React.FC = () => {
    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-white mb-4">仪表盘 (Dashboard)</h1>
            <AccountSummary />
            <PositionTable />
            {/* Recent Trades ... */}
        </div>
    );
};

export default Dashboard;
