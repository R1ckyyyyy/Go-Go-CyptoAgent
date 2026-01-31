import React from 'react';
import { Activity } from 'lucide-react';

import { useWebSocket } from '../../hooks/useWebSocket';

const Navbar: React.FC = () => {
    const { status } = useWebSocket();

    return (
        <nav className="h-16 border-b border-gray-800 flex items-center px-6 justify-between bg-zinc-950">
            <div className="flex items-center space-x-2 text-blue-500">
                <Activity size={24} />
                <span className="font-bold text-xl">CryptoAgent</span>
            </div>
            <div className="flex items-center space-x-6">
                <div className="flex items-center space-x-2 text-sm">
                    <div className={`w-2 h-2 rounded-full ${status === 'connected' ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
                    <span className="text-gray-400 capitalize">{status}</span>
                </div>
                <div className="w-8 h-8 rounded-full bg-gray-700"></div>
            </div>
        </nav>
    );
};

export default Navbar;
