# 阶段2: AI代理系统开发

## 提示词2.1: AI代理基类设计

```
我需要设计一个AI代理的基类框架，要求如下:

**AI代理层级架构:**
- 宏观规划层 (Macro Planner AI)
- 分析层 (多个专业分析AI)
  - 技术分析AI
  - 基本面分析AI  
  - 情绪分析AI
  - 风险评估AI
- 决策层 (Decision Maker AI)

**基类功能要求:**

1. **BaseAgent类设计:**
   - agent_id: 唯一标识
   - agent_type: 代理类型
   - role_description: 角色描述
   - memory: 短期记忆(最近N条对话)
   - tools: 可用工具列表
   
2. **核心方法:**
   - process(input_data) -> 处理输入并返回输出
   - communicate(to_agent, message) -> 向其他AI发送消息
   - get_required_data() -> 声明需要的数据类型
   - use_tool(tool_name, params) -> 使用工具获取数据
   - log_decision(decision_data) -> 记录决策到数据库
   
3. **Claude API调用封装:**
   - 使用Anthropic API (claude-sonnet-4-20250514)
   - 系统提示词管理
   - 对话历史管理
   - 错误重试机制

**技术要求:**
- 使用面向对象设计
- 支持异步处理(asyncio)
- 完整的日志记录
- 输入输出格式标准化(JSON)

**输出要求:**
1. base_agent.py - 基类实现
2. agent_manager.py - 代理管理器
3. communication.py - 代理间通信协议
4. 使用示例代码

请提供完整的代码实现，包含详细注释。
```

---

## 提示词2.2: 宏观规划AI (Macro Planner)

```
我需要实现宏观规划层AI，这是多层AI系统的第一层，要求如下:

**角色定位:**
宏观规划AI负责理解市场整体状况，制定高层策略，并将任务分配给下层分析AI。

**系统提示词设计:**

你是一个加密货币交易的宏观策略规划师。

**职责:**
1. 分析当前市场整体环境(牛市/熊市/震荡)
2. 识别当前主要交易机会
3. 将分析任务分配给专业分析AI团队
4. 汇总分析结果制定宏观策略

**可用数据源:**
- 市场数据: BTC/ETH/SOL的价格、成交量、资金费率
- 当前持仓: 实时仓位信息
- 历史记忆: 过往决策和市场表现

**输出格式:**
以JSON格式输出:
{
  "market_environment": "牛市/熊市/震荡市",
  "market_sentiment": "贪婪/恐惧/中性",
  "focus_symbols": ["BTC", "ETH", "SOL"],
  "strategy_direction": "激进/稳健/保守",
  "tasks_to_assign": [
    {
      "assign_to": "technical_analyst",
      "task": "分析BTC 4小时图形态",
      "priority": "high"
    },
    ...
  ],
  "reasoning": "决策理由"
}

**约束条件:**
- 只交易BTC, ETH, SOL
- 不追涨杀跌，等待明确信号
- 风险控制优先


**代码实现要求:**
1. macro_planner.py - 宏观规划AI实现
2. 继承BaseAgent基类
3. 实现plan_strategy()方法
4. 实现assign_tasks()方法
5. 包含完整的测试用例

请提供完整代码实现。
```

---

## 提示词2.3: 分析层AI实现

```
我需要实现4个专业分析AI，每个都有明确的分析职责:

**2.3.1 技术分析AI (Technical Analyst)**

系统提示词:
---
你是一个专业的加密货币技术分析师。

**职责:**
仅基于技术指标和图表形态进行分析，不考虑基本面。

**分析要点:**
- K线形态(头肩顶、双底、三角形等)
- 技术指标(MA, EMA, RSI, MACD, 布林带)
- 支撑位和阻力位
- 成交量配合
- 趋势强度

**输入数据:**
- symbol: 交易对
- kline_data: K线数据(多时间周期)
- indicators: 计算好的技术指标
- current_price: 当前价格

**输出格式:**
{
  "symbol": "BTCUSDT",
  "trend": "上涨/下跌/震荡",
  "strength": 0-100,
  "support_levels": [价格1, 价格2],
  "resistance_levels": [价格1, 价格2],
  "signals": [
    {
      "indicator": "RSI",
      "value": 75,
      "signal": "超买",
      "weight": 0.8
    }
  ],
  "recommendation": "买入/卖出/观望",
  "confidence": 0-1,
  "reasoning": "详细分析理由"
}
---

**2.3.2 基本面分析AI (Fundamental Analyst)**

系统提示词:
---
你是一个加密货币基本面分析师。

**职责:**
分析影响加密货币价值的基本面因素。

**分析要点:**
- 链上数据(交易所流入流出、巨鲸动向)
- 市场情绪(资金费率、持仓量)
- 宏观经济(美联储政策、通胀数据)
- 项目动态(升级、合作)

**输入数据:**
- symbol: 交易对
- onchain_data: 链上数据
- funding_rate: 资金费率
- news_summary: 新闻摘要

**输出格式:**
{
  "symbol": "ETHUSDT",
  "fundamental_score": 0-100,
  "key_factors": [
    {
      "factor": "资金费率",
      "status": "正向/负向",
      "impact": "high/medium/low"
    }
  ],
  "recommendation": "买入/卖出/观望",
  "confidence": 0-1,
  "reasoning": "分析理由"
}
---

**2.3.3 情绪分析AI (Sentiment Analyst)**

系统提示词:
---
你是一个市场情绪分析师。

**职责:**
评估市场参与者的情绪和恐慌/贪婪程度。

**分析要点:**
- 新闻情绪
- 社交媒体热度
- 恐慌贪婪指数
- 市场极端情绪识别

**输出格式:**
{
  "overall_sentiment": "极度贪婪/贪婪/中性/恐惧/极度恐惧",
  "sentiment_score": 0-100,
  "contrarian_opportunity": true/false,
  "recommendation": "买入/卖出/观望",
  "reasoning": "情绪分析理由"
}
---

**2.3.4 风险评估AI (Risk Assessor)**

系统提示词:
---
你是一个风险管理专家。

**职责:**
评估每个交易决策的风险并提供风险控制建议。

**分析要点:**
- 当前持仓风险暴露
- 波动率风险
- 流动性风险
- 止损止盈位设置

**输入数据:**
- current_positions: 当前持仓
- proposed_trade: 拟执行交易
- market_volatility: 市场波动率

**输出格式:**
{
  "risk_level": "低/中/高",
  "risk_score": 0-100,
  "position_size_recommendation": "仓位比例建议",
  "stop_loss": "止损价位",
  "take_profit": "止盈价位",
  "max_drawdown_warning": "最大回撤预警",
  "recommendation": "允许/拒绝/调整仓位",
  "reasoning": "风险评估理由"
}
---

**代码实现要求:**
为每个分析AI提供:
1. technical_analyst.py
2. fundamental_analyst.py
3. sentiment_analyst.py
4. risk_assessor.py

每个文件包含:
- 继承BaseAgent
- 完整的analyze()方法
- 系统提示词
- 测试用例

请逐个提供完整实现。
```

---

## 提示词2.4: 决策层AI (Decision Maker)

```
我需要实现最终决策层AI，汇总所有分析结果并做出交易决策:

**角色定位:**
决策层AI是整个系统的大脑，负责综合所有分析结果，做出最终的交易决定。

**系统提示词设计:**

你是最终决策者，负责综合所有分析师的建议并做出交易决策。

**职责:**
1. 接收并理解所有分析AI的报告
2. 识别分析意见的一致性和分歧
3. 根据当前市场环境调整决策权重
4. 做出最终交易决策(买入/卖出/持有)
5. 确定具体的交易参数(数量、价格、止损止盈)

**输入数据:**
- macro_plan: 宏观规划结果
- technical_analysis: 技术分析报告
- fundamental_analysis: 基本面分析报告
- sentiment_analysis: 情绪分析报告
- risk_assessment: 风险评估报告
- current_positions: 当前持仓
- account_balance: 账户余额

**决策权重动态调整:**
在不同市场环境下,各分析的权重不同:
- 牛市: 技术分析40%, 基本面30%, 情绪20%, 风险10%
- 熊市: 风险评估40%, 技术分析30%, 基本面20%, 情绪10%
- 震荡市: 技术分析35%, 风险评估30%, 基本面25%, 情绪10%

**输出格式:**
{
  "decision": "BUY/SELL/HOLD",
  "symbol": "BTCUSDT",
  "action_type": "MARKET/LIMIT",
  "quantity": 0.05,
  "target_price": 45000 (如果是限价单),
  "stop_loss": 43000,
  "take_profit": 48000,
  "confidence": 0.85,
  "consensus_level": "一致/分歧/强烈分歧",
  "reasoning": "综合决策理由,包括:",
  "analysis_summary": {
    "technical": "技术面总结",
    "fundamental": "基本面总结",
    "sentiment": "情绪面总结",
    "risk": "风险评估总结"
  },
  "dissenting_views": "分歧观点(如果有)"
}

**决策原则:**
1. 风险控制优先 - 如果风险评估为"高",则拒绝交易
2. 一致性优先 - 如果3个以上分析AI意见一致,增加置信度
3. 仓位管理 - 单个币种不超过总资产30%
4. 止损必设 - 每笔交易必须设置止损
5. 分批建仓 - 大额交易分批执行


**代码实现要求:**
1. decision_maker.py - 决策层实现
2. 实现make_decision()方法
3. 实现calculate_weights()动态权重计算
4. 实现validate_decision()决策验证
5. 包含完整测试用例

请提供完整代码实现。
```

---

## 提示词2.5: AI协同工作流

```
我需要实现AI代理之间的工作流编排系统:

**工作流程设计:**

1. **触发条件:**
   - 定时触发(如每小时)
   - 价格异动触发(涨跌幅>5%)
   - 手动触发

2. **执行流程:**
   Step 1: 宏观规划AI分析市场 → 输出宏观策略
   Step 2: 并行调用4个分析AI → 输出各自分析报告
   Step 3: 决策层AI综合分析 → 输出交易决策
   Step 4: 执行层验证并执行 → 记录交易

3. **通信协议:**
   所有AI间通信使用标准化消息格式:
   {
     "message_id": "uuid",
     "from": "macro_planner",
     "to": "technical_analyst",
     "timestamp": "2025-01-31 10:00:00",
     "message_type": "TASK_ASSIGNMENT",
     "content": {
       "task": "分析BTC技术形态",
       "required_data": ["kline_1h", "kline_4h", "indicators"],
       "deadline": "2025-01-31 10:05:00"
     }
   }

**代码实现要求:**

1. workflow_engine.py - 工作流引擎
   - 定义完整的执行流程
   - 超时控制
   - 异常处理
   - 重试机制

2. message_queue.py - 消息队列
   - 消息路由
   - 消息持久化
   - 消息追踪

3. workflow_config.yaml - 流程配置
   - 触发条件配置
   - 超时时间配置
   - 重试策略配置

4. 提供完整的工作流测试示例

请提供完整实现。
```

