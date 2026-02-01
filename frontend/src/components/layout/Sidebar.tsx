import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Network, CandlestickChart, BrainCircuit, Settings } from 'lucide-react';

const Sidebar: React.FC = () => {
    const navItems = [
        { path: '/', icon: LayoutDashboard, label: '仪表盘' },
        { path: '/ai-tree', icon: Network, label: 'AI 决策树' },
        { path: '/trading', icon: CandlestickChart, label: '交易终端' },
        { path: '/insights', icon: BrainCircuit, label: '市场洞察' },
        { path: '/settings', icon: Settings, label: '系统设置' },
    ];

    return (
        <aside className="w-64 border-r border-gray-200 h-[calc(100vh-4rem)] bg-zinc-50/50 backdrop-blur-xl flex flex-col p-4">
            <div className="space-y-2 flex-1">
                {navItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        className={({ isActive }) =>
                            `flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${isActive
                                ? 'bg-zinc-200 text-zinc-900 font-medium'
                                : 'text-zinc-500 hover:bg-zinc-100 hover:text-zinc-900'
                            }`
                        }
                    >
                        <item.icon size={20} />
                        <span>{item.label}</span>
                    </NavLink>
                ))}
            </div>
        </aside>
    );
};

export default Sidebar;
