import React from 'react';
import { LineChart, Newspaper, ShieldAlert, Activity } from 'lucide-react';

interface ConsultantCardProps {
    role: 'technical' | 'fundamental' | 'risk_management';
    content: any; // Flexible for JSON or string
    status: 'pending' | 'thinking' | 'done';
}

export const ConsultantCard: React.FC<ConsultantCardProps> = ({ role, content, status }) => {
    const getIcon = () => {
        switch (role) {
            case 'technical': return <LineChart className="w-4 h-4 text-green-600" />;
            case 'fundamental': return <Newspaper className="w-4 h-4 text-blue-600" />;
            case 'risk_management': return <ShieldAlert className="w-4 h-4 text-red-600" />;
            default: return <Activity className="w-4 h-4 text-gray-600" />;
        }
    };

    const getTitle = () => {
        switch (role) {
            case 'technical': return '技术分析 (Technical)';
            case 'fundamental': return '基本面分析 (Fundamental)';
            case 'risk_management': return '风控评估 (Risk)';
            default: return role;
        }
    };

    const getStyle = () => {
        switch (role) {
            case 'technical': return 'border-green-200 bg-green-50';
            case 'fundamental': return 'border-blue-200 bg-blue-50';
            case 'risk_management': return 'border-red-200 bg-red-50';
            default: return 'border-gray-200 bg-gray-50';
        }
    };

    // Helper to parse content if it's a string
    const parseContent = (data: any) => {
        if (typeof data === 'string') return data;
        if (typeof data === 'object') {
            // If it's a structured object, try to render key fields
            return (
                <ul className="text-xs space-y-1 mt-2">
                    {Object.entries(data).map(([k, v]) => (
                        <li key={k} className="flex justify-between">
                            <span className="opacity-70 capitalize">{k.replace(/_/g, ' ')}:</span>
                            <span className="font-medium">{String(v)}</span>
                        </li>
                    ))}
                </ul>
            );
        }
        return JSON.stringify(data);
    };

    return (
        <div className={`border rounded-lg p-3 ${getStyle()} transition-all duration-300`}>
            <div className="flex items-center gap-2 mb-2">
                {getIcon()}
                <span className="font-bold text-gray-800 text-sm">{getTitle()}</span>
            </div>

            {status === 'thinking' && (
                <div className="flex items-center gap-1 text-xs text-gray-500 animate-pulse">
                    <div className="w-1.5 h-1.5 bg-gray-400 rounded-full"></div>
                    <span>思考中...</span>
                </div>
            )}

            {status === 'done' && (
                <div className="text-sm text-gray-700">
                    {parseContent(content)}
                </div>
            )}
        </div>
    );
};
