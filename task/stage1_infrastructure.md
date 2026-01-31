# 阶段1: 基础架构和数据层开发

## 提示词1.1: 币安API封装工具

```
我需要开发一个Python模块来封装币安API，要求如下:

**核心功能:**
1. 账户信息获取(余额、持仓)
2. 市场数据获取(K线、ticker、深度)
3. 订单管理(下单、撤单、查询订单)
4. 模拟盘和实盘的统一接口

**技术要求:**
- 使用python-binance库
- 支持testnet和mainnet切换
- 完整的错误处理和重试机制
- 返回标准化的JSON格式数据
- 添加rate limit保护

**接口设计:**
- get_account_balance() -> 返回所有币种余额
- get_current_positions() -> 返回当前持仓(BTC/ETH/SOL)
- get_kline_data(symbol, interval, limit) -> 返回K线数据
- get_ticker(symbol) -> 返回最新价格
- get_order_book(symbol, limit) -> 返回订单簿深度
- place_order(symbol, side, type, quantity, price) -> 下单
- cancel_order(symbol, order_id) -> 撤单
- get_order_status(symbol, order_id) -> 查询订单

**输出要求:**
1. 完整的binance_api.py文件
2. config.py配置文件模板(API密钥管理)
3. 使用示例代码
4. 详细的中文注释

请提供完整代码实现。
```

---

## 提示词1.2: 数据库设计

```
我需要设计一个SQLite数据库来存储交易系统的所有数据，要求如下:

**数据表需求:**

1. **positions表** - 当前持仓
   - id, symbol, amount, avg_price, current_price, pnl, update_time
   
2. **trades表** - 交易历史
   - id, symbol, side(buy/sell), price, quantity, fee, timestamp, order_id, status
   
3. **market_data表** - 市场数据快照
   - id, symbol, price, volume_24h, change_24h, timestamp
   
4. **ai_decisions表** - AI决策记录
   - id, decision_type, input_data, output_recommendation, confidence, timestamp, layer(宏观/分析/决策)
   
5. **ai_communications表** - AI间通信记录
   - id, from_ai, to_ai, message_type, content, timestamp
   
6. **memory表** - 系统记忆
   - id, memory_type, content, importance_score, timestamp, expiry_date
   
7. **config表** - 配置信息
   - id, config_key, config_value, update_time

**技术要求:**
- 使用SQLAlchemy ORM
- 完整的CRUD操作封装
- 支持事务处理
- 添加索引优化查询性能

**输出要求:**
1. database.py - 数据库模型定义
2. db_operations.py - 数据库操作类
3. init_db.py - 数据库初始化脚本
4. 使用示例代码

请提供完整代码实现，包含中文注释。
```

---

## 提示词1.3: 数据采集工具

```
我需要开发多个数据采集工具来为AI提供信息，要求如下:

**工具清单:**

1. **市场数据采集器(market_collector.py)**
   - 实时价格监控
   - K线数据获取(1m, 5m, 15m, 1h, 4h, 1d)
   - 成交量分析
   - 资金费率(永续合约)
   - 持仓量变化

2. **新闻情绪采集器(news_collector.py)**
   - 加密货币新闻RSS抓取
   - Twitter关键词监控(可选)
   - 情绪分析(使用简单的NLP)

3. **技术指标计算器(indicators.py)**
   - MA(移动平均线)
   - EMA(指数移动平均)
   - RSI(相对强弱指数)
   - MACD
   - 布林带
   - 成交量指标

4. **链上数据采集器(onchain_collector.py)**
   - 交易所流入流出
   - 巨鲸地址监控
   - 使用免费API(如CoinGlass, Glassnode免费层)

**技术要求:**
- 定时任务支持(使用schedule库)
- 数据存入数据库
- 异常处理和日志记录
- 返回标准化JSON格式

**输出要求:**
为每个采集器提供:
1. 完整的Python代码
2. 依赖库列表(requirements.txt)
3. 配置文件示例
4. 使用说明

请逐个提供每个采集器的完整实现。
```

---

## 提示词1.4: 项目基础结构

```
请帮我创建一个完整的Python项目结构，用于加密货币交易AI系统:

**项目结构要求:**

```
crypto_trading_agent/
├── config/
│   ├── __init__.py
│   ├── config.yaml          # 主配置文件
│   └── api_keys.yaml.example # API密钥模板
├── data/
│   ├── database.db          # SQLite数据库
│   └── logs/                # 日志目录
├── src/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── binance_api.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── operations.py
│   ├── collectors/
│   │   ├── __init__.py
│   │   ├── market_collector.py
│   │   ├── news_collector.py
│   │   ├── indicators.py
│   │   └── onchain_collector.py
│   ├── ai_agents/          # 后续阶段开发
│   │   └── __init__.py
│   ├── web/                # 后续阶段开发
│   │   └── __init__.py
│   └── utils/
│       ├── __init__.py
│       ├── logger.py
│       └── helpers.py
├── tests/
│   └── __init__.py
├── requirements.txt
├── README.md
└── main.py
```
**

**输出要求:**
1. 提供每个__init__.py的内容
2. config.yaml的完整配置示例
3. requirements.txt包含所有依赖
4. README.md项目说明文档
5. 一个简单的main.py来测试基础功能

请提供所有文件的完整内容。
```

