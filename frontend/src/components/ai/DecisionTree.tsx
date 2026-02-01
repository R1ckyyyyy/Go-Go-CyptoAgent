import React, { useEffect, useState } from 'react';
import ReactFlow, {
    Controls,
    Background,
    useNodesState,
    useEdgesState,
    Handle,
    Position,
    BackgroundVariant
} from 'reactflow';
import type { Node, Edge, NodeProps } from 'reactflow';
import 'reactflow/dist/style.css';
import { aiApi } from '../../services/api';
import { Activity, Shield, TrendingUp, Newspaper, Zap } from 'lucide-react';

// --- Custom Glass Node Component ---
const GlassNode = ({ data, selected }: NodeProps) => {
    const isWorking = data.status === 'working';
    const isSuccess = data.status === 'success';

    // Icon Mapping
    let Icon = Activity;
    if (data.type === 'coordinator') Icon = Zap;
    if (data.id === 'risk') Icon = Shield;
    if (data.id === 'technical') Icon = TrendingUp;
    if (data.id === 'fundamental') Icon = Newspaper;

    return (
        <div className={`
            relative overflow-hidden
            rounded-xl p-4 w-56 transition-all duration-500 ease-out
            bg-gradient-to-br from-white via-white to-zinc-50
            border border-white/60
            ${selected
                ? 'shadow-[0_8px_30px_rgb(0,0,0,0.12)] ring-1 ring-black/5 scale-105'
                : 'shadow-[0_4px_20px_rgb(0,0,0,0.04)] hover:shadow-[0_8px_25px_rgb(0,0,0,0.08)] hover:-translate-y-1'
            }
        `}>
            <Handle type="target" position={Position.Top} className="!bg-zinc-200 !w-2.5 !h-2.5 !rounded-full !border-[2px] !border-white opacity-100 -mt-1.5" />

            {/* Status Indicator Line */}
            <div className={`absolute top-0 left-0 w-1 h-full transition-colors duration-500 ${isWorking ? 'bg-blue-500' :
                isSuccess ? 'bg-emerald-500' :
                    'bg-zinc-200'
                }`} />

            <div className="flex items-start mb-3 pl-2">
                <div className={`
                    p-2 rounded-lg mr-2.5 shadow-inner flex-shrink-0
                    ${isWorking ? 'bg-blue-50 text-blue-600' :
                        isSuccess ? 'bg-emerald-50 text-emerald-600' :
                            'bg-zinc-100 text-zinc-500'}
                `}>
                    <Icon size={18} strokeWidth={2} />
                </div>
                <div>
                    <h3 className="text-sm font-bold text-zinc-800 tracking-tight leading-snug">{data.label}</h3>
                    <div className="flex items-center mt-1">
                        <span className={`flex h-1.5 w-1.5 rounded-full mr-1.5 ${isWorking ? 'bg-blue-500 animate-pulse' :
                            isSuccess ? 'bg-emerald-500' : 'bg-zinc-300'
                            }`}></span>
                        <p className={`text-[9px] font-bold uppercase tracking-wider ${isWorking ? 'text-blue-600' :
                            isSuccess ? 'text-emerald-600' : 'text-zinc-400'
                            }`}>
                            {data.current_task || 'STANDBY'}
                        </p>
                    </div>
                </div>
            </div>

            <div className="pl-2 relative">
                <div className="text-[10px] text-zinc-500 leading-relaxed font-medium border-t border-zinc-100 pt-2 opacity-80">
                    {data.description}
                </div>
            </div>

            <Handle type="source" position={Position.Bottom} className="!bg-zinc-200 !w-2.5 !h-2.5 !rounded-full !border-[2px] !border-white opacity-100 -mb-1.5" />
        </div>
    );
};

const nodeTypes = {
    coordinator: GlassNode,
    consultant: GlassNode,
    execution: GlassNode, // Re-use simplified mapping
    default: GlassNode
};

interface DecisionTreeProps {
    onNodeSelect?: (nodeId: string | null) => void;
}

const DecisionTree: React.FC<DecisionTreeProps> = ({ onNodeSelect }) => {
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [statuses, setStatuses] = useState<any[]>([]);

    // 1. Initial Load
    useEffect(() => {
        aiApi.getTreeStructure().then(res => {
            const { nodes: apiNodes, edges: apiEdges } = res.data;

            const flowNodes: Node[] = apiNodes.map((n: any) => ({
                id: n.id,
                type: n.type || 'default', // Use custom types
                position: n.position,
                data: {
                    id: n.id,
                    type: n.type,
                    label: n.label,
                    description: n.description,
                    status: 'idle',
                    current_task: 'Ready'
                },
            }));

            const flowEdges: Edge[] = apiEdges.map((e: any) => ({
                id: e.id,
                source: e.source,
                target: e.target,
                animated: true,
                style: { stroke: '#94a3b8', strokeWidth: 1.5, opacity: 0.5 },
                type: 'smoothstep'
            }));

            setNodes(flowNodes);
            setEdges(flowEdges);
        }).catch(err => console.error("Failed to load tree structure:", err));
    }, []);

    // 2. Poll Status
    useEffect(() => {
        const fetchStatus = () => {
            aiApi.getNodeStatus().then(res => {
                setStatuses(res.data);
            }).catch(console.error);
        };
        fetchStatus();
        const interval = setInterval(fetchStatus, 2000);
        return () => clearInterval(interval);
    }, []);

    // 3. Sync Status to Nodes
    useEffect(() => {
        if (statuses.length === 0) return;
        setNodes((nds) => nds.map((node) => {
            const statusData = statuses.find(s => s.id === node.id);
            if (!statusData) return node;

            // Only update if changed to avoid re-renders
            if (node.data.status === statusData.status && node.data.current_task === statusData.current_task) {
                return node;
            }

            return {
                ...node,
                data: {
                    ...node.data,
                    status: statusData.status,
                    current_task: statusData.current_task
                }
            };
        }));
    }, [statuses, setNodes]);

    return (
        <div className="w-full h-full rounded-2xl overflow-hidden glass-panel border border-white/20 bg-white/40">
            <ReactFlow
                nodes={nodes}
                edges={edges}
                nodeTypes={nodeTypes}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onNodeClick={(_, node) => onNodeSelect && onNodeSelect(node.id)}
                onPaneClick={() => onNodeSelect && onNodeSelect(null)}
                fitView
            >
                <Background color="#cbd5e1" gap={24} size={1} variant={BackgroundVariant.Dots} className="opacity-40" />
                <Controls className="!bg-white !border-slate-200 !fill-slate-600 !shadow-sm" />
            </ReactFlow>
        </div>
    );
};

export default DecisionTree;
