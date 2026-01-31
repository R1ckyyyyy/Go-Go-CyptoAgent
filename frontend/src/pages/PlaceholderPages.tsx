import React from 'react';
import { Construction } from 'lucide-react';

const Placeholder: React.FC<{ title: string }> = ({ title }) => (
    <div className="h-full flex flex-col items-center justify-center text-gray-500 space-y-4">
        <Construction size={48} className="opacity-50" />
        <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-300">{title}</h2>
            <p className="mt-2">This module is under development.</p>
        </div>
    </div>
);

export const Dashboard: React.FC = () => <Placeholder title="Dashboard" />;
export const AITree: React.FC = () => <Placeholder title="AI Decision Tree" />;
// Note: Dashboard and AITree are actually imported from real files in App.tsx now
// But we keep them here just in case related imports fail or revert

export const Trading: React.FC = () => <Placeholder title="Trading Center" />;
export const Insights: React.FC = () => <Placeholder title="AI Insights" />;
export const Settings: React.FC = () => <Placeholder title="System Settings" />;
