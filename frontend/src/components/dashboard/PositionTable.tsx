import React, { useEffect, useState } from 'react';
import { accountApi } from '../../services/api';
import type { Position } from '../../types';

const PositionTable: React.FC = () => {
    const [positions, setPositions] = useState<Position[]>([]);

    useEffect(() => {
        accountApi.getPositions().then(res => setPositions(res.data)).catch(console.error);
    }, []);

    return (
        <div className="bg-zinc-900 rounded-xl border border-gray-800 overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-800">
                <h3 className="font-semibold text-lg">Active Positions</h3>
            </div>
            <div className="overflow-x-auto">
                <table className="w-full text-left">
                    <thead className="bg-black/20 text-gray-400 text-sm">
                        <tr>
                            <th className="px-6 py-3">Symbol</th>
                            <th className="px-6 py-3">Amount</th>
                            <th className="px-6 py-3">Avg Price</th>
                            <th className="px-6 py-3">Current</th>
                            <th className="px-6 py-3">PnL</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-800">
                        {positions.length === 0 ? (
                            <tr><td colSpan={5} className="px-6 py-8 text-center text-gray-500">No active positions (API connected)</td></tr>
                        ) : (
                            positions.map((pos) => (
                                <tr key={pos.symbol} className="hover:bg-white/5 transition-colors">
                                    <td className="px-6 py-4 font-medium">{pos.symbol}</td>
                                    <td className="px-6 py-4">{pos.amount}</td>
                                    <td className="px-6 py-4">${pos.avgPrice}</td>
                                    <td className="px-6 py-4">${pos.currentPrice}</td>
                                    <td className={`px-6 py-4 ${pos.pnl >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                                        {pos.pnl >= 0 ? '+' : ''}{pos.pnl.toFixed(2)}
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
