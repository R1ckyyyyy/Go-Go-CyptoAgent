# 阶段4: Web界面和可视化系统

## 提示词4.1: Web后端API设计

```
我需要使用Flask或FastAPI开发一个Web后端API,用于前端交互:

**技术选型:**
- 框架: FastAPI (更现代,支持异步,自动生成API文档)
- 数据库: SQLite (已有)
- WebSocket: 实时数据推送

**API端点设计:**

1. **系统状态 (/api/system)**
   - GET /api/system/status - 获取系统运行状态
   - GET /api/system/config - 获取当前配置
   - POST /api/system/config - 更新配置
   - POST /api/system/start - 启动自动交易
   - POST /api/system/stop - 停止自动交易

2. **账户信息 (/api/account)**
   - GET /api/account/balance - 获取账户余额
   - GET /api/account/positions - 获取当前持仓
   - GET /api/account/performance - 获取账户表现

3. **交易相关 (/api/trading)**
   - GET /api/trading/history - 获取交易历史
   - POST /api/trading/manual - 手动下单
   - GET /api/trading/orders - 获取订单列表
   - DELETE /api/trading/order/{id} - 撤销订单

4. **AI决策 (/api/ai)**
   - GET /api/ai/decisions - 获取AI决策历史
   - GET /api/ai/decision/{id} - 获取单个决策详情
   - GET /api/ai/communications - 获取AI通信记录
   - POST /api/ai/trigger - 手动触发AI分析

5. **数据查询 (/api/data)**
   - GET /api/data/market/{symbol} - 获取市场数据
   - GET /api/data/klines - 获取K线数据
   - GET /api/data/memory - 获取记忆数据

6. **回测 (/api/backtest)**
   - POST /api/backtest/run - 运行回测
   - GET /api/backtest/results - 获取回测结果
   - GET /api/backtest/report/{id} - 获取回测报告

7. **WebSocket (/ws)**
   - /ws/market - 实时市场数据推送
   - /ws/positions - 实时持仓更新
   - /ws/ai-activity - 实时AI活动推送

**代码实现要求:**

1. main.py - FastAPI应用主文件
   ```python
   from fastapi import FastAPI, WebSocket
   from fastapi.middleware.cors import CORSMiddleware
   
   app = FastAPI(title="Crypto Trading AI System")
   
   # 配置CORS
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   
   # 路由注册
   # ...
   ```

2. routers/
   - system.py - 系统相关路由
   - account.py - 账户相关路由
   - trading.py - 交易相关路由
   - ai.py - AI相关路由
   - data.py - 数据查询路由
   - backtest.py - 回测相关路由
   - websocket.py - WebSocket处理

3. schemas/ - Pydantic数据模型
   - request_models.py
   - response_models.py

4. 提供API文档和使用示例

请提供完整的FastAPI实现。
```

---

## 提示词4.2: 前端架构设计

```
我需要使用React开发一个现代化的Web前端界面:

**技术栈:**
- React 18 + TypeScript
- Vite (构建工具)
- TailwindCSS (样式)
- Recharts (图表)
- React Query (数据获取)
- Zustand (状态管理)
- React Router (路由)

**页面结构:**

1. **仪表盘 (Dashboard) - /**
   - 账户总览卡片(总资产、今日盈亏、持仓数量)
   - 实时持仓表格
   - 近期交易列表
   - 市场快照(BTC/ETH/SOL价格)

2. **AI决策树 (AI Decision Tree) - /ai-tree**
   - 可视化的AI协作流程图
   - 实时显示AI间通信
   - 点击查看每个AI的详细分析
   - 决策时间轴

3. **交易中心 (Trading) - /trading**
   - 手动交易界面
   - 订单管理
   - 交易历史
   - K线图表(集成TradingView或自建)

4. **AI洞察 (AI Insights) - /insights**
   - 宏观策略展示
   - 各分析AI的最新观点
   - 决策一致性分析
   - 历史决策回顾

5. **回测中心 (Backtesting) - /backtest**
   - 回测配置界面
   - 回测结果展示
   - 性能指标对比
   - 策略优化建议

6. **设置 (Settings) - /settings**
   - 策略配置
   - 风控参数
   - API密钥管理
   - 通知设置

**项目结构:**
```
frontend/
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Navbar.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Layout.tsx
│   │   ├── dashboard/
│   │   │   ├── AccountSummary.tsx
│   │   │   ├── PositionTable.tsx
│   │   │   └── RecentTrades.tsx
│   │   ├── ai/
│   │   │   ├── DecisionTree.tsx
│   │   │   ├── AICard.tsx
│   │   │   └── CommunicationLog.tsx
│   │   ├── trading/
│   │   │   ├── OrderForm.tsx
│   │   │   ├── OrderBook.tsx
│   │   │   └── KLineChart.tsx
│   │   └── common/
│   │       ├── Card.tsx
│   │       ├── Button.tsx
│   │       └── Loading.tsx
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── AITree.tsx
│   │   ├── Trading.tsx
│   │   ├── Insights.tsx
│   │   ├── Backtest.tsx
│   │   └── Settings.tsx
│   ├── hooks/
│   │   ├── useWebSocket.ts
│   │   ├── useAccount.ts
│   │   └── useAIDecisions.ts
│   ├── services/
│   │   └── api.ts
│   ├── store/
│   │   └── useStore.ts
│   ├── types/
│   │   └── index.ts
│   ├── App.tsx
│   └── main.tsx
├── package.json
├── vite.config.ts
└── tailwind.config.js
```

**代码实现要求:**

提供以下关键文件:
1. App.tsx - 应用主文件和路由配置
2. services/api.ts - API调用封装
3. hooks/useWebSocket.ts - WebSocket钩子
4. store/useStore.ts - 全局状态管理
5. types/index.ts - TypeScript类型定义

请提供完整的React项目架构代码。
```

---

## 提示词4.3: AI决策树可视化

```
我需要实现一个交互式的AI决策树可视化组件,这是整个系统的核心:

**可视化需求:**

1. **层次结构展示**
   ```
   [宏观规划AI] (顶层)
        ↓
   [任务分配]
        ↓
   ┌────────┬──────────┬──────────┬──────────┐
   │技术分析││基本面分析││情绪分析  ││风险评估  │ (分析层)
   └────────┴──────────┴──────────┴──────────┘
        ↓
   [结果汇总]
        ↓
   [决策层AI] (决策层)
        ↓
   [交易执行]
   ```

2. **实时状态显示**
   - 空闲状态: 灰色
   - 工作中: 蓝色动画
   - 完成: 绿色
   - 错误: 红色

3. **交互功能**
   - 点击AI节点查看详细信息
   - 鼠标悬停显示AI当前状态
   - 显示AI间的通信消息流
   - 时间轴回放历史决策

4. **详细信息面板**
   点击AI节点后,侧边栏显示:
   - AI角色描述
   - 输入数据
   - 分析过程
   - 输出结果
   - 置信度
   - 处理时间

**技术实现:**

使用React Flow或D3.js实现流程图:

示例代码结构:
```typescript
import ReactFlow, { 
  Node, 
  Edge, 
  Controls, 
  Background 
} from 'reactflow';
import 'reactflow/dist/style.css';

interface AINodeData {
  id: string;
  type: 'macro' | 'analyst' | 'decision';
  status: 'idle' | 'working' | 'completed' | 'error';
  label: string;
  lastOutput?: any;
}

const AIDecisionTree: React.FC = () => {
  const [nodes, setNodes] = useState<Node<AINodeData>[]>([
    {
      id: 'macro',
      type: 'custom',
      position: { x: 400, y: 0 },
      data: { 
        type: 'macro',
        status: 'idle',
        label: '宏观规划AI'
      }
    },
    // ... 其他节点
  ]);

  const [edges, setEdges] = useState<Edge[]>([
    // 定义连线
  ]);

  return (
    <div style={{ height: '100vh' }}>
      <ReactFlow 
        nodes={nodes} 
        edges={edges}
        nodeTypes={nodeTypes}
        onNodeClick={handleNodeClick}
      >
        <Controls />
        <Background />
      </ReactFlow>
      
      {selectedNode && (
        <DetailPanel node={selectedNode} />
      )}
    </div>
  );
};
```

**代码实现要求:**

1. components/ai/DecisionTree.tsx
   - 主可视化组件
   - 节点自定义样式
   - 实时状态更新

2. components/ai/AINode.tsx
   - 自定义AI节点组件
   - 状态指示器
   - 动画效果

3. components/ai/DetailPanel.tsx
   - 详情侧边栏
   - 数据展示
   - 历史记录查看

4. components/ai/MessageFlow.tsx
   - AI通信消息动画
   - 消息路径高亮

5. hooks/useAIFlow.ts
   - AI流程状态管理
   - WebSocket实时更新

请提供完整实现,包含动画效果和交互逻辑。
```

---

## 提示词4.4: 仪表盘组件实现

```
我需要实现一个信息丰富的仪表盘页面:

**仪表盘布局:**

```
┌─────────────────────────────────────────────────┐
│  账户总览                                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │总资产    │ │今日盈亏  │ │总盈亏    │        │
│  │$10,500   │ │+$250     │ │+$1,500   │        │
│  └──────────┘ └──────────┘ └──────────┘        │
└─────────────────────────────────────────────────┘

┌──────────────────────┐  ┌─────────────────────┐
│  当前持仓              │  │  市场快照            │
│  BTC  0.5  $22,500   │  │  BTC  $45,000 ↑2.5%│
│  ETH  5.0  $12,500   │  │  ETH  $2,500  ↑1.8%│
│  SOL  100  $8,500    │  │  SOL  $85     ↓0.5%│
└──────────────────────┘  └─────────────────────┘

┌─────────────────────────────────────────────────┐
│  权益曲线图                                       │
│  (实时更新的账户价值折线图)                        │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  最近交易                                         │
│  时间        币种    类型  价格    数量   盈亏    │
│  10:30:15  BTC    买入  45000  0.1   -       │
│  09:15:22  ETH    卖出  2500   2.0   +$120  │
└─────────────────────────────────────────────────┘
```

**组件实现要求:**

1. **AccountSummary.tsx - 账户总览卡片**
```typescript
interface AccountSummary {
  totalBalance: number;
  todayPnL: number;
  totalPnL: number;
  pnlPercentage: number;
}

const AccountSummary: React.FC = () => {
  const { data, isLoading } = useQuery('account', fetchAccountData);
  
  return (
    <div className="grid grid-cols-3 gap-4">
      <Card>
        <h3>总资产</h3>
        <p className="text-3xl">${data?.totalBalance.toFixed(2)}</p>
      </Card>
      {/* 其他卡片 */}
    </div>
  );
};
```

2. **PositionTable.tsx - 持仓表格**
   - 实时价格更新
   - 盈亏颜色标识
   - 点击查看详情

3. **EquityCurve.tsx - 权益曲线**
   - 使用Recharts绘制
   - 实时数据更新
   - 可缩放时间范围

4. **MarketSnapshot.tsx - 市场快照**
   - WebSocket实时推送价格
   - 涨跌幅颜色指示
   - 简洁的卡片设计

5. **RecentTrades.tsx - 交易列表**
   - 分页展示
   - 筛选功能
   - 导出功能

**样式要求:**
- 使用TailwindCSS
- 暗色主题(背景#1a1a1a)
- 绿色(盈利)和红色(亏损)配色
- 响应式设计

**代码实现要求:**
提供完整的组件代码,包括:
1. 组件实现
2. 数据获取hooks
3. 样式定义
4. 使用示例

请提供完整实现。
```

---

## 提示词4.5: 部署和Docker化

```
我需要将整个系统Docker化,方便部署:

**Docker架构:**

```
┌─────────────────────────────────────┐
│  docker-compose.yml                 │
│                                     │
│  services:                          │
│    - backend (FastAPI)              │
│    - frontend (Nginx + React)       │
│    - redis (缓存)                    │
└─────────────────────────────────────┘
```

**文件要求:**

1. **backend/Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. **frontend/Dockerfile**
```dockerfile
FROM node:18 AS builder

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

3. **docker-compose.yml**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./config:/app/config
    environment:
      - MODE=production
    depends_on:
      - redis
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    restart: unless-stopped

volumes:
  data:
  config:
```

4. **nginx.conf**
```nginx
server {
    listen 80;
    server_name localhost;

    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /ws {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

5. **部署脚本 (deploy.sh)**
```bash
#!/bin/bash

echo "开始部署加密货币交易AI系统..."

# 停止旧容器
docker-compose down

# 构建新镜像
docker-compose build

# 启动服务
docker-compose up -d

echo "部署完成! 访问 http://localhost 查看系统"
```

**代码实现要求:**
1. 提供所有Docker相关文件
2. 提供部署文档(README_DEPLOY.md)
3. 提供环境变量配置示例
4. 提供备份和恢复脚本

请提供完整的Docker化方案。
```

