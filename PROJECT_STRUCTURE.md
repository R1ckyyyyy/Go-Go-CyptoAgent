# 项目结构和依赖清单

## 📁 完整项目结构

```
crypto_trading_agent/
│
├── README.md                          # 项目说明文档
├── requirements.txt                   # Python依赖
├── docker-compose.yml                 # Docker编排
├── .env.example                       # 环境变量模板
├── .gitignore                         # Git忽略文件
│
├── config/                            # 配置文件目录
│   ├── __init__.py
│   ├── config.yaml                    # 主配置
│   ├── api_keys.yaml.example          # API密钥模板
│   ├── strategies/                    # 策略配置
│   │   ├── conservative.yaml
│   │   ├── moderate.yaml
│   │   └── aggressive.yaml
│   └── logging_config.yaml            # 日志配置
│
├── data/                              # 数据目录
│   ├── database.db                    # SQLite数据库
│   ├── logs/                          # 日志文件
│   │   ├── app.log
│   │   ├── error.log
│   │   ├── ai_decisions.log
│   │   └── trades.log
│   └── backtest_results/              # 回测结果
│
├── src/                               # 源代码目录
│   ├── __init__.py
│   │
│   ├── api/                           # API封装
│   │   ├── __init__.py
│   │   └── binance_api.py
│   │
│   ├── database/                      # 数据库层
│   │   ├── __init__.py
│   │   ├── models.py                  # 数据模型
│   │   ├── operations.py              # 数据库操作
│   │   └── migrations/                # 数据库迁移
│   │
│   ├── collectors/                    # 数据采集
│   │   ├── __init__.py
│   │   ├── market_collector.py        # 市场数据
│   │   ├── news_collector.py          # 新闻采集
│   │   ├── indicators.py              # 技术指标
│   │   └── onchain_collector.py       # 链上数据
│   │
│   ├── ai_agents/                     # AI代理层
│   │   ├── __init__.py
│   │   ├── base_agent.py              # 基类
│   │   ├── agent_manager.py           # 代理管理器
│   │   ├── communication.py           # 通信协议
│   │   ├── macro_planner.py           # 宏观规划AI
│   │   ├── technical_analyst.py       # 技术分析AI
│   │   ├── fundamental_analyst.py     # 基本面分析AI
│   │   ├── sentiment_analyst.py       # 情绪分析AI
│   │   ├── risk_assessor.py           # 风险评估AI
│   │   └── decision_maker.py          # 决策层AI
│   │
│   ├── workflow/                      # 工作流引擎
│   │   ├── __init__.py
│   │   ├── workflow_engine.py
│   │   ├── message_queue.py
│   │   └── workflow_config.yaml
│   │
│   ├── memory/                        # 记忆系统
│   │   ├── __init__.py
│   │   ├── memory_system.py
│   │   ├── memory_retrieval.py
│   │   └── memory_config.yaml
│   │
│   ├── trading/                       # 交易执行层
│   │   ├── __init__.py
│   │   ├── position_manager.py        # 仓位管理
│   │   ├── account_manager.py         # 账户管理
│   │   ├── trade_executor.py          # 交易执行
│   │   ├── safety_checks.py           # 安全检查
│   │   └── order_types.py             # 订单类型
│   │
│   ├── strategy/                      # 策略系统
│   │   ├── __init__.py
│   │   ├── strategy_config.py
│   │   └── config_validator.py
│   │
│   ├── backtest/                      # 回测系统
│   │   ├── __init__.py
│   │   ├── backtester.py
│   │   ├── performance_analyzer.py
│   │   └── backtest_visualizer.py
│   │
│   ├── web/                           # Web后端
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI主应用
│   │   ├── routers/                   # API路由
│   │   │   ├── __init__.py
│   │   │   ├── system.py
│   │   │   ├── account.py
│   │   │   ├── trading.py
│   │   │   ├── ai.py
│   │   │   ├── data.py
│   │   │   ├── backtest.py
│   │   │   └── websocket.py
│   │   ├── schemas/                   # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── request_models.py
│   │   │   └── response_models.py
│   │   └── middleware/                # 中间件
│   │       ├── __init__.py
│   │       ├── authentication.py
│   │       └── rate_limiter.py
│   │
│   ├── monitoring/                    # 监控系统
│   │   ├── __init__.py
│   │   ├── monitoring.py              # Prometheus指标
│   │   ├── alerts.py                  # 告警系统
│   │   └── health_check.py
│   │
│   ├── security/                      # 安全模块
│   │   ├── __init__.py
│   │   ├── encryption.py
│   │   ├── authentication.py
│   │   └── audit.py
│   │
│   └── utils/                         # 工具函数
│       ├── __init__.py
│       ├── logger.py
│       ├── helpers.py
│       ├── error_handlers.py
│       ├── circuit_breaker.py
│       └── graceful_shutdown.py
│
├── frontend/                          # React前端
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── index.html
│   │
│   ├── public/                        # 静态资源
│   │   └── favicon.ico
│   │
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── index.css
│       │
│       ├── components/                # React组件
│       │   ├── layout/
│       │   │   ├── Navbar.tsx
│       │   │   ├── Sidebar.tsx
│       │   │   └── Layout.tsx
│       │   ├── dashboard/
│       │   │   ├── AccountSummary.tsx
│       │   │   ├── PositionTable.tsx
│       │   │   ├── EquityCurve.tsx
│       │   │   ├── MarketSnapshot.tsx
│       │   │   └── RecentTrades.tsx
│       │   ├── ai/
│       │   │   ├── DecisionTree.tsx
│       │   │   ├── AINode.tsx
│       │   │   ├── DetailPanel.tsx
│       │   │   ├── MessageFlow.tsx
│       │   │   └── CommunicationLog.tsx
│       │   ├── trading/
│       │   │   ├── OrderForm.tsx
│       │   │   ├── OrderBook.tsx
│       │   │   ├── KLineChart.tsx
│       │   │   └── OrderHistory.tsx
│       │   ├── backtest/
│       │   │   ├── BacktestConfig.tsx
│       │   │   ├── ResultsChart.tsx
│       │   │   └── PerformanceMetrics.tsx
│       │   └── common/
│       │       ├── Card.tsx
│       │       ├── Button.tsx
│       │       ├── Loading.tsx
│       │       ├── Alert.tsx
│       │       └── Modal.tsx
│       │
│       ├── pages/                     # 页面组件
│       │   ├── Dashboard.tsx
│       │   ├── AITree.tsx
│       │   ├── Trading.tsx
│       │   ├── Insights.tsx
│       │   ├── Backtest.tsx
│       │   └── Settings.tsx
│       │
│       ├── hooks/                     # 自定义Hooks
│       │   ├── useWebSocket.ts
│       │   ├── useAccount.ts
│       │   ├── useAIDecisions.ts
│       │   ├── useAIFlow.ts
│       │   └── useMarketData.ts
│       │
│       ├── services/                  # API服务
│       │   ├── api.ts
│       │   └── websocket.ts
│       │
│       ├── store/                     # 状态管理
│       │   └── useStore.ts
│       │
│       ├── types/                     # TypeScript类型
│       │   └── index.ts
│       │
│       └── utils/
│           ├── formatters.ts
│           └── validators.ts
│
├── tests/                             # 测试目录
│   ├── __init__.py
│   ├── unit/                          # 单元测试
│   │   ├── test_binance_api.py
│   │   ├── test_database.py
│   │   ├── test_collectors.py
│   │   ├── test_ai_agents.py
│   │   ├── test_memory_system.py
│   │   └── test_position_manager.py
│   ├── integration/                   # 集成测试
│   │   ├── test_workflow.py
│   │   ├── test_trading_flow.py
│   │   └── test_api_endpoints.py
│   └── fixtures/                      # 测试数据
│       ├── mock_data.py
│       └── test_config.yaml
│
├── scripts/                           # 脚本目录
│   ├── init_db.py                     # 初始化数据库
│   ├── backup_db.py                   # 备份数据库
│   ├── run_backtest.py                # 运行回测
│   ├── deploy.sh                      # 部署脚本
│   └── run_tests.sh                   # 测试脚本
│
├── docs/                              # 文档目录
│   ├── stage1_infrastructure.md
│   ├── stage2_ai_agents.md
│   ├── stage3_memory_execution.md
│   ├── stage4_web_interface.md
│   ├── stage5_testing_optimization.md
│   ├── API.md                         # API文档
│   ├── DEPLOYMENT.md                  # 部署文档
│   └── SECURITY.md                    # 安全文档
│
└── docker/                            # Docker相关
    ├── backend/
    │   └── Dockerfile
    ├── frontend/
    │   ├── Dockerfile
    │   └── nginx.conf
    └── prometheus/
        └── prometheus.yml
```

---

## 📦 依赖清单

### Python依赖 (requirements.txt)

```txt
# Web框架
fastapi==0.109.0
uvicorn[standard]==0.27.0
websockets==12.0

# 数据库
sqlalchemy==2.0.25
alembic==1.13.1

# API客户端
python-binance==1.0.19
anthropic==0.18.1

# 数据处理
pandas==2.2.0
numpy==1.26.3

# 技术指标
ta-lib==0.4.28
pandas-ta==0.3.14b0

# 新闻/情绪分析
feedparser==6.0.10
requests==2.31.0
beautifulsoup4==4.12.3

# 缓存
redis==5.0.1
hiredis==2.3.2

# 异步
asyncio==3.4.3
aiohttp==3.9.1

# 加密
cryptography==42.0.0
pyjwt==2.8.0

# 监控
prometheus-client==0.19.0
python-dotenv==1.0.0

# 日志
loguru==0.7.2

# 限流
slowapi==0.1.9

# 测试
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
httpx==0.26.0

# 配置
pyyaml==6.0.1
pydantic==2.5.3
pydantic-settings==2.1.0

# 工具
schedule==1.2.1
python-dateutil==2.8.2
pytz==2024.1

# 机器学习(可选)
scikit-learn==1.4.0
sentence-transformers==2.3.1

# 图表
matplotlib==3.8.2
plotly==5.18.0
```

### 前端依赖 (package.json)

```json
{
  "name": "crypto-trading-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "jest"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.21.1",
    "reactflow": "^11.10.4",
    "@tanstack/react-query": "^5.17.9",
    "zustand": "^4.4.7",
    "recharts": "^2.10.3",
    "axios": "^1.6.5",
    "dayjs": "^1.11.10",
    "lucide-react": "^0.309.0",
    "react-window": "^1.8.10",
    "use-debounce": "^10.0.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.48",
    "@types/react-dom": "^18.2.18",
    "@types/react-window": "^1.8.8",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.3.3",
    "vite": "^5.0.11",
    "tailwindcss": "^3.4.1",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.33",
    "@testing-library/react": "^14.1.2",
    "@testing-library/jest-dom": "^6.1.6",
    "jest": "^29.7.0"
  }
}
```

---

## 🔧 环境变量配置

### .env.example

```bash
# 应用配置
APP_NAME=CryptoTradingAI
APP_ENV=development
DEBUG=true

# 服务端口
BACKEND_PORT=8000
FRONTEND_PORT=3000

# 数据库
DATABASE_URL=sqlite:///./data/database.db

# Redis
REDIS_URL=redis://localhost:6379/0

# 币安API
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
BINANCE_TESTNET=true

# Anthropic Claude API
ANTHROPIC_API_KEY=your_claude_api_key_here

# 加密密钥
ENCRYPTION_KEY=your_encryption_key_here_32_bytes

# JWT
JWT_SECRET=your_jwt_secret_here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

# 交易模式
TRADING_MODE=simulated  # simulated 或 live

# 日志
LOG_LEVEL=INFO
LOG_FILE=./data/logs/app.log

# 监控
PROMETHEUS_PORT=9090
```

---

## 🐳 Docker配置

### docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: 
      context: .
      dockerfile: docker/backend/Dockerfile
    container_name: crypto_trading_backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./config:/app/config
      - ./src:/app/src
    environment:
      - APP_ENV=production
      - DATABASE_URL=sqlite:///./data/database.db
      - REDIS_URL=redis://redis:6379/0
    env_file:
      - .env
    depends_on:
      - redis
    restart: unless-stopped
    networks:
      - crypto_network

  frontend:
    build:
      context: ./frontend
      dockerfile: ../docker/frontend/Dockerfile
    container_name: crypto_trading_frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - crypto_network

  redis:
    image: redis:7-alpine
    container_name: crypto_trading_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - crypto_network

  prometheus:
    image: prom/prometheus:latest
    container_name: crypto_trading_prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./docker/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
    restart: unless-stopped
    networks:
      - crypto_network

  grafana:
    image: grafana/grafana:latest
    container_name: crypto_trading_grafana
    ports:
      - "3001:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    depends_on:
      - prometheus
    restart: unless-stopped
    networks:
      - crypto_network

volumes:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  crypto_network:
    driver: bridge
```

---

## ⚙️ 配置文件模板

### config/config.yaml

```yaml
# 应用配置
app:
  name: "Crypto Trading AI"
  version: "1.0.0"
  debug: false

# 交易配置
trading:
  mode: "simulated"  # simulated | live
  symbols: ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
  initial_balance: 10000.0
  
# 策略配置
strategy:
  default: "moderate"
  auto_adjust: true
  
# AI配置
ai:
  model: "claude-sonnet-4-20250514"
  max_tokens: 4000
  temperature: 0.7
  timeout: 30
  
# 工作流配置
workflow:
  trigger:
    scheduled: true
    interval_minutes: 60
    price_change_threshold: 0.05
  timeout_seconds: 60
  max_retries: 3
  
# 风控配置
risk:
  max_daily_loss: 0.05
  max_single_loss: 0.02
  stop_loss_percentage: 0.03
  take_profit_ratio: 2.0
  daily_trade_limit: 20
  max_position_per_symbol: 0.30
  max_total_position: 0.80

# 记忆配置
memory:
  retention:
    short_term_hours: 24
    medium_term_days: 90
    long_term_days: 365
  cleanup_schedule: "0 3 * * 0"  # 每周日凌晨3点
  importance_threshold: 20

# 监控配置
monitoring:
  enabled: true
  prometheus_port: 9090
  metrics_update_interval: 10
  
# 告警配置
alerts:
  enabled: true
  channels: ["log", "email"]
  thresholds:
    loss_percentage: -0.05
    api_error_rate: 0.10
    latency_seconds: 5.0
```

---

## 📋 开发清单

按照以下顺序开发可以确保系统逐步构建：

- [ ] **阶段1: 基础设施** (2-3天)
  - [ ] 项目结构搭建
  - [ ] 币安API封装
  - [ ] 数据库设计和ORM
  - [ ] 数据采集器
  - [ ] 技术指标计算

- [ ] **阶段2: AI代理** (3-4天)
  - [ ] AI基类设计
  - [ ] 宏观规划AI
  - [ ] 4个分析AI
  - [ ] 决策层AI
  - [ ] 工作流引擎

- [ ] **阶段3: 执行和记忆** (2-3天)
  - [ ] 记忆系统
  - [ ] 仓位管理
  - [ ] 交易执行
  - [ ] 策略配置
  - [ ] 回测系统

- [ ] **阶段4: Web界面** (3-5天)
  - [ ] FastAPI后端
  - [ ] React前端框架
  - [ ] AI决策树可视化
  - [ ] 仪表盘组件
  - [ ] Docker部署

- [ ] **阶段5: 优化和测试** (2-3天)
  - [ ] 单元测试
  - [ ] 集成测试
  - [ ] 性能优化
  - [ ] 监控系统
  - [ ] 安全加固

总计: **12-18天**完整开发周期

