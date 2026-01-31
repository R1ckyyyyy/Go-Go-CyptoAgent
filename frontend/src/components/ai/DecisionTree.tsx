import React, { useEffect, useState, useCallback } from 'react';
import ReactFlow, {
    Controls,
    Background,
    useNodesState,
    useEdgesState
} from 'reactflow';
import type { Node, Edge } from 'reactflow';
import 'reactflow/dist/style.css';
import { aiApi } from '../../services/api';

const statusColors = {
    idle: '#64748b',   // slate-500
    working: '#3b82f6', // blue-500
    success: '#10b981', // emerald-500
    error: '#ef4444'    // red-500
};

const DecisionTree: React.FC = () => {
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [statuses, setStatuses] = useState<any[]>([]);

    // Fetch Structure
    useEffect(() => {
        aiApi.getTreeStructure().then(res => {
            const { nodes: apiNodes, edges: apiEdges } = res.data;

            const flowNodes: Node[] = apiNodes.map((n: any) => ({
                id: n.id,
                position: n.position,
                data: { label: n.label, originalLabel: n.label }, // Store original label to append task
                style: {
                    background: '#1e293b',
                    color: 'white',
                    border: '2px solid #64748b',
                    borderRadius: '8px',
                    padding: '10px',
                    width: 180,
                    fontSize: '12px'
                },
                type: 'default'
            }));

            const flowEdges: Edge[] = apiEdges.map((e: any) => ({
                id: e.id,
                source: e.source,
                target: e.target,
                animated: true,
                style: { stroke: '#475569' }
            }));

            setNodes(flowNodes);
            setEdges(flowEdges);
        }).catch(err => console.error("Failed to load tree structure:", err));
    }, []);

    // Poll Status
    useEffect(() => {
        const fetchStatus = () => {
            aiApi.getNodeStatus().then(res => {
                setStatuses(res.data);
            }).catch(console.error);
        };

        fetchStatus();
        const interval = setInterval(fetchStatus, 3000); // Poll every 3s
        return () => clearInterval(interval);
    }, []);

    // Update Nodes based on Status
    useEffect(() => {
        if (statuses.length === 0) return;

        setNodes((nds) =>
            nds.map((node) => {
                const statusData = statuses.find(s => s.id === node.id);
                if (!statusData) return node;

                const color = statusColors[statusData.status as keyof typeof statusColors] || statusColors.idle;
                const isWorking = statusData.status === 'working';

                return {
                    ...node,
                    data: {
                        ...node.data,
                        label: (
                            <div className="flex flex-col items-center">
                                <div className="font-bold mb-1">{node.data.originalLabel}</div>
                                {statusData.current_task && (
                                    <div className="text-[10px] opacity-80 italic truncate w-full text-center">
                                        {statusData.current_task}
                                    </div>
                                )}
                            </div>
                        )
                    },
                    style: {
                        ...node.style,
                        borderColor: color,
                        boxShadow: isWorking ? `0 0 15px ${color}40` : 'none',
                        transition: 'all 0.3s ease'
                    }
                };
            })
        );
    }, [statuses, setNodes]);

    return (
        <div style={{ height: '70vh', border: '1px solid #333', borderRadius: '12px', overflow: 'hidden', background: '#0f172a' }}>
            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                fitView
            >
                <Background color="#333" gap={20} />
                <Controls />
            </ReactFlow>
        </div>
    );
};

export default DecisionTree;
