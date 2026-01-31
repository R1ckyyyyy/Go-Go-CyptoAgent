import React from 'react';
import DecisionTree from '../components/ai/DecisionTree';

const AITree: React.FC = () => {
    return (
        <div className="h-full flex flex-col">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold text-white">AI Decision Logic</h1>
                <div className="flex space-x-2">
                    <span className="flex items-center text-sm text-gray-400">
                        <span className="w-2 h-2 rounded-full bg-green-500 mr-2"></span>
                        Active
                    </span>
                </div>
            </div>
            <div className="flex-1">
                <DecisionTree />
            </div>
        </div>
    );
};

export default AITree;
