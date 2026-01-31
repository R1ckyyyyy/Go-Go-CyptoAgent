# 阶段3: 记忆系统和交易执行层

## 提示词3.1: 记忆系统设计

```
我需要实现一个智能记忆系统,让AI能够学习和改进:

**记忆类型:**

1. **短期记忆 (Short-term Memory)**
   - 存储范围: 最近24小时
   - 内容: 市场快照、决策记录、执行结果
   - 用途: 快速上下文理解

2. **长期记忆 (Long-term Memory)**
   - 存储范围: 永久存储(带清理机制)
   - 内容: 成功/失败的交易策略、市场规律、经验教训
   - 用途: 策略优化和学习

3. **情景记忆 (Episodic Memory)**
   - 存储范围: 重要市场事件
   - 内容: 暴涨暴跌、黑天鹅事件、关键转折点
   - 用途: 识别相似情景

**记忆重要性评分:**
根据以下因素计算记忆的重要性(0-100):
- 交易结果(盈利>10%: 高分, 亏损>5%: 高分)
- 市场异常(波动率>正常2倍: 高分)
- 决策一致性(所有AI一致: 中分, 强烈分歧: 高分)
- 时效性(最近7天: +20分)

**清理机制:**
- 重要性<20的记忆: 30天后删除
- 重要性20-50: 90天后删除
- 重要性50-80: 180天后删除
- 重要性>80: 永久保留
- 每周执行一次清理任务

**检索机制:**
- 时间检索: 获取特定时间段的记忆
- 相似度检索: 基于当前市场状况检索类似情景
- 主题检索: 检索特定币种/策略的记忆

**代码实现要求:**

1. memory_system.py
   - MemoryManager类
   - add_memory(content, memory_type, importance)
   - retrieve_similar(current_context, top_k=5)
   - calculate_importance(memory_data)
   - cleanup_old_memories()
   
2. memory_retrieval.py
   - 实现向量化检索(使用sentence-transformers)
   - 实现时间衰减算法
   
3. memory_config.yaml
   - 各类记忆的保留时长
   - 重要性评分规则
   
4. 使用示例和测试用例

请提供完整实现,包含详细注释。
```

---

## 提示词3.2: 仓位管理系统

```
我需要实现一个仓位管理系统,让AI能准确了解当前持仓:

**核心功能:**

1. **实时仓位追踪**
   - 持仓数量
   - 平均成本
   - 当前市值
   - 未实现盈亏
   - 已实现盈亏

2. **仓位计算**
   - 可用余额
   - 已用保证金
   - 仓位占比
   - 风险暴露度

3. **模拟盘与实盘统一接口**
   - AI不知道当前是实盘还是模拟盘
   - 两种模式使用相同的数据格式
   - 通过配置文件切换模式

**数据格式标准:**

仓位信息JSON格式:
{
  "account_summary": {
    "total_balance": 10000.00,
    "available_balance": 7000.00,
    "unrealized_pnl": 500.00,
    "realized_pnl": 1200.00,
    "mode": "不显示给AI"
  },
  "positions": [
    {
      "symbol": "BTCUSDT",
      "amount": 0.5,
      "avg_entry_price": 42000.00,
      "current_price": 45000.00,
      "market_value": 22500.00,
      "unrealized_pnl": 1500.00,
      "pnl_percentage": 7.14,
      "position_ratio": 0.225
    }
  ],
  "daily_stats": {
    "total_trades": 15,
    "winning_trades": 9,
    "win_rate": 0.60,
    "avg_profit": 2.3,
    "max_drawdown": -5.2
  }
}

**模拟盘实现:**
- 使用内存中的虚拟账户
- 模拟订单撮合(以最新价成交)
- 计算手续费(0.1%)
- 记录所有交易到数据库

**代码实现要求:**

1. position_manager.py
   - PositionManager类(实盘)
   - SimulatedPositionManager类(模拟盘)
   - get_positions() -> 返回标准格式
   - update_position(trade_data)
   - calculate_pnl()
   
2. account_manager.py
   - AccountManager类
   - get_account_info() -> 返回标准格式
   - validate_balance(order) -> 验证余额充足
   
3. 提供模拟盘和实盘的切换示例

请提供完整实现。
```

---

## 提示词3.3: 交易执行层

```
我需要实现交易执行层,负责实际下单和订单管理:

**核心功能:**

1. **订单验证**
   - 余额验证
   - 风险验证(单笔交易不超过总资产的30%)
   - 参数验证(价格、数量合法性)
   - 止损止盈合理性检查

2. **订单执行**
   - 市价单执行
   - 限价单执行
   - 止损止盈单设置
   - 订单追踪

3. **执行反馈**
   - 实时订单状态更新
   - 成交通知
   - 失败处理和重试

4. **安全机制**
   - 日内交易次数限制(最多20次)
   - 单日亏损熔断(亏损>5%暂停交易)
   - 异常检测(价格异常波动)
   - 人工确认模式(可选)

**执行流程:**

Decision AI输出 → 执行层验证 → 风险检查 → 下单 → 追踪 → 反馈

**代码实现要求:**

1. trade_executor.py
   - TradeExecutor类
   - validate_order(decision)
   - execute_order(order_params)
   - track_order(order_id)
   - handle_execution_result(result)
   
2. safety_checks.py
   - check_daily_limit()
   - check_loss_threshold()
   - check_price_abnormal()
   - emergency_stop()
   
3. order_types.py
   - MarketOrder类
   - LimitOrder类
   - StopLossOrder类
   - TakeProfitOrder类
   
4. 提供完整的执行示例和测试用例

请提供完整实现。
```

---

## 提示词3.4: 策略配置系统

```
我需要实现一个策略配置系统,让我能够灵活调整交易偏好:

**配置项:**

1. **交易偏好**
   ```yaml
   trading_preference:
     risk_level: "medium"  # low/medium/high
     trading_style: "swing" # scalping/day/swing/position
     max_position_per_symbol: 0.30  # 单币种最大仓位比例
     max_total_position: 0.80  # 总仓位上限
     prefer_symbols: ["BTC", "ETH", "SOL"]
     forbidden_symbols: []  # 禁止交易的币种
   ```

2. **风控参数**
   ```yaml
   risk_control:
     max_daily_loss: 0.05  # 单日最大亏损5%
     max_single_loss: 0.02  # 单笔最大亏损2%
     stop_loss_percentage: 0.03  # 默认止损3%
     take_profit_ratio: 2.0  # 盈亏比2:1
     daily_trade_limit: 20  # 日内最大交易次数
   ```

3. **AI权重调整**
   ```yaml
   ai_weights:
     bull_market:
       technical: 0.40
       fundamental: 0.30
       sentiment: 0.20
       risk: 0.10
     bear_market:
       technical: 0.30
       fundamental: 0.20
       sentiment: 0.10
       risk: 0.40
     sideways_market:
       technical: 0.35
       fundamental: 0.25
       sentiment: 0.10
       risk: 0.30
   ```

4. **执行模式**
   ```yaml
   execution:
     mode: "simulated"  # simulated/live
     manual_confirm: false  # 是否需要人工确认
     auto_trading: true  # 是否自动交易
     notification: true  # 是否发送通知
   ```

**动态策略调整:**
AI可以根据市场环境自动建议策略调整:
- 检测到市场转向 → 建议切换风控参数
- 连续亏损3次 → 建议降低风险等级
- 胜率>70% → 建议适当提高仓位

**代码实现要求:**

1. strategy_config.py
   - StrategyConfig类
   - load_config()
   - update_config(new_params)
   - get_current_strategy()
   - suggest_adjustment(market_condition)
   
2. config_validator.py
   - 配置参数合法性验证
   - 参数冲突检测
   
3. strategies/
   - conservative_strategy.yaml  # 保守策略
   - moderate_strategy.yaml  # 稳健策略
   - aggressive_strategy.yaml  # 激进策略
   
4. 提供策略切换示例

请提供完整实现。
```

---

## 提示词3.5: 回测系统

```
我需要实现一个回测系统,验证AI策略的有效性:

**回测功能:**

1. **历史数据回放**
   - 加载历史K线数据
   - 模拟时间流逝
   - 重现市场环境

2. **策略回测**
   - 运行完整的AI决策流程
   - 模拟订单执行
   - 记录所有决策和交易

3. **性能评估**
   - 总收益率
   - 夏普比率
   - 最大回撤
   - 胜率
   - 盈亏比
   - 交易次数
   - 日均收益

4. **可视化报告**
   - 权益曲线
   - 回撤曲线
   - 交易分布
   - 胜率统计

**回测配置:**
```yaml
backtest:
  start_date: "2024-01-01"
  end_date: "2025-01-01"
  initial_balance: 10000
  symbols: ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
  timeframe: "1h"
  strategy: "moderate_strategy.yaml"
```

**代码实现要求:**

1. backtester.py
   - Backtester类
   - run_backtest(config)
   - simulate_trading_day()
   - calculate_metrics()
   
2. performance_analyzer.py
   - 计算各项指标
   - 生成性能报告
   
3. backtest_visualizer.py
   - 生成图表(使用matplotlib)
   - 导出HTML报告
   
4. 提供完整的回测示例

请提供完整实现。
```

