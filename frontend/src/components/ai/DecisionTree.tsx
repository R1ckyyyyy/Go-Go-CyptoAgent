import React, { useState } from 'react';
import ReactFlow, {
    Controls,
    Background
} from 'reactflow';
import type { Node, Edge } from 'reactflow';
import 'reactflow/dist/style.css';

const initialNodes: Node[] = [
    { id: '1', position: { x: 250, y: 0 }, data: { label: 'Macro Strategy AI' }, style: { background: '#1e293b', color: 'white', border: '1px solid #3b82f6' } },
    { id: '2', position: { x: 100, y: 150 }, data: { label: 'Tech Analyst' }, style: { background: '#1e293b', color: 'white', border: '1px solid #10b981' } },
    { id: '3', position: { x: 400, y: 150 }, data: { label: 'Risk Manager' }, style: { background: '#1e293b', color: 'white', border: '1px solid #ef4444' } },
    { id: '4', position: { x: 250, y: 300 }, data: { label: 'Execution Engine' }, style: { background: '#1e293b', color: 'white', border: '1px solid #eab308' } },
];

const initialEdges: Edge[] = [
    { id: 'e1-2', source: '1', target: '2', animated: true },
    { id: 'e1-3', source: '1', target: '3', animated: true },
    { id: 'e2-4', source: '2', target: '4' },
    { id: 'e3-4', source: '3', target: '4' },
];

const DecisionTree: React.FC = () => {
    const [nodes] = useState(initialNodes);
    const [edges] = useState(initialEdges);

    return (
        <div style={{ height: '80vh', border: '1px solid #333', borderRadius: '8px', overflow: 'hidden' }}>
            <ReactFlow
                nodes={nodes}
                edges={edges}
                fitView
            >
                <Background color="#333" gap={16} />
                <Controls />
            </ReactFlow>
        </div>
    );
};

export default DecisionTree;
