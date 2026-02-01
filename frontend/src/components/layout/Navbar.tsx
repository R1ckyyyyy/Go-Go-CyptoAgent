import React from 'react';
import { Activity } from 'lucide-react';

import { useWebSocket } from '../../hooks/useWebSocket';

const Navbar: React.FC = () => {
    const { status } = useWebSocket();

    return (
        <nav className="h-16 border-b border-gray-200 flex items-center px-6 justify-between bg-zinc-50/50 backdrop-blur-xl">
            <div className="flex items-center space-x-2 text-zinc-900">
                <Activity size={24} />
                <span className="font-bold text-xl tracking-tight">CryptoAgent</span>
            </div>
            <div className="flex items-center space-x-6">
                <div className="flex items-center space-x-2 text-sm">
                    <div className={`w-2 h-2 rounded-full ${status === 'connected' ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`}></div>
                    <span className="text-zinc-500 capitalize font-medium">{status}</span>
                </div>
                <div className="w-8 h-8 rounded-full bg-zinc-200 border border-zinc-300"></div>
            </div>
        </nav>
    );
};

export default Navbar;
