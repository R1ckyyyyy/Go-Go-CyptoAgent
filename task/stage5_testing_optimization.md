# 阶段5: 测试、优化和监控

## 提示词5.1: 单元测试和集成测试

```
我需要为整个系统编写完整的测试用例:

**测试框架:**
- Python: pytest
- React: Jest + React Testing Library

**Python测试结构:**

```
tests/
├── unit/
│   ├── test_binance_api.py
│   ├── test_database.py
│   ├── test_collectors.py
│   ├── test_ai_agents.py
│   ├── test_memory_system.py
│   └── test_position_manager.py
├── integration/
│   ├── test_workflow.py
│   ├── test_trading_flow.py
│   └── test_api_endpoints.py
└── fixtures/
    ├── mock_data.py
    └── test_config.yaml
```

**测试用例示例:**

1. **test_binance_api.py**
```python
import pytest
from unittest.mock import Mock, patch
from src.api.binance_api import BinanceAPI

class TestBinanceAPI:
    @pytest.fixture
    def api(self):
        return BinanceAPI(
            api_key="test_key",
            api_secret="test_secret",
            testnet=True
        )
    
    def test_get_account_balance(self, api):
        """测试获取账户余额"""
        with patch.object(api.client, 'get_account') as mock:
            mock.return_value = {
                'balances': [
                    {'asset': 'USDT', 'free': '10000.00'}
                ]
            }
            balance = api.get_account_balance()
            assert balance['USDT'] == 10000.00
    
    def test_place_order_success(self, api):
        """测试成功下单"""
        with patch.object(api.client, 'create_order') as mock:
            mock.return_value = {
                'orderId': 12345,
                'status': 'FILLED'
            }
            result = api.place_order(
                symbol='BTCUSDT',
                side='BUY',
                order_type='MARKET',
                quantity=0.001
            )
            assert result['orderId'] == 12345
    
    def test_place_order_insufficient_balance(self, api):
        """测试余额不足"""
        with patch.object(api.client, 'create_order') as mock:
            mock.side_effect = Exception("Insufficient balance")
            with pytest.raises(Exception):
                api.place_order(
                    symbol='BTCUSDT',
                    side='BUY',
                    order_type='MARKET',
                    quantity=100
                )
```

2. **test_ai_agents.py**
```python
import pytest
from src.ai_agents.technical_analyst import TechnicalAnalyst
from tests.fixtures.mock_data import get_mock_kline_data

class TestTechnicalAnalyst:
    @pytest.fixture
    def analyst(self):
        return TechnicalAnalyst()
    
    def test_analyze_uptrend(self, analyst):
        """测试上涨趋势识别"""
        mock_data = get_mock_kline_data(trend='up')
        result = analyst.analyze(
            symbol='BTCUSDT',
            kline_data=mock_data
        )
        assert result['trend'] == '上涨'
        assert result['recommendation'] in ['买入', '观望']
    
    def test_analyze_oversold(self, analyst):
        """测试超卖信号"""
        mock_data = get_mock_kline_data(rsi=25)
        result = analyst.analyze(
            symbol='BTCUSDT',
            kline_data=mock_data
        )
        # 验证RSI超卖信号
        rsi_signal = next(
            s for s in result['signals'] 
            if s['indicator'] == 'RSI'
        )
        assert rsi_signal['signal'] == '超卖'
```

3. **test_workflow.py (集成测试)**
```python
import pytest
from src.workflow_engine import WorkflowEngine
from src.ai_agents import *

class TestWorkflow:
    @pytest.fixture
    def engine(self):
        return WorkflowEngine()
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self, engine):
        """测试完整的AI决策流程"""
        # 触发工作流
        result = await engine.run_analysis_cycle(
            symbols=['BTCUSDT']
        )
        
        # 验证所有AI都被调用
        assert 'macro_plan' in result
        assert 'technical_analysis' in result
        assert 'fundamental_analysis' in result
        assert 'sentiment_analysis' in result
        assert 'risk_assessment' in result
        assert 'final_decision' in result
        
        # 验证决策格式
        decision = result['final_decision']
        assert 'decision' in decision
        assert 'symbol' in decision
        assert 'confidence' in decision
        assert decision['confidence'] >= 0 and decision['confidence'] <= 1
```

**前端测试示例:**

4. **AccountSummary.test.tsx**
```typescript
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import AccountSummary from '@/components/dashboard/AccountSummary';

describe('AccountSummary', () => {
  const queryClient = new QueryClient();
  
  it('displays account balance correctly', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <AccountSummary />
      </QueryClientProvider>
    );
    
    // 等待数据加载
    const balance = await screen.findByText(/\$10,000/);
    expect(balance).toBeInTheDocument();
  });
  
  it('shows profit in green color', () => {
    const { container } = render(
      <QueryClientProvider client={queryClient}>
        <AccountSummary />
      </QueryClientProvider>
    );
    
    const profitElement = container.querySelector('.text-green-500');
    expect(profitElement).toBeTruthy();
  });
});
```

**测试覆盖率要求:**
- 目标: 80%以上代码覆盖率
- 关键模块: 90%以上覆盖率

**代码实现要求:**
1. 完整的测试套件
2. Mock数据生成器
3. 测试配置文件(pytest.ini, jest.config.js)
4. CI/CD配置(.github/workflows/test.yml)
5. 测试运行脚本(run_tests.sh)

请提供完整的测试实现。
```

---

## 提示词5.2: 性能优化

```
我需要优化系统性能,确保高效运行:

**优化领域:**

1. **数据库优化**

问题识别和解决:
```python
# 问题: N+1查询
# 优化前
for decision in decisions:
    communications = db.query(Communication).filter(
        Communication.decision_id == decision.id
    ).all()

# 优化后: 使用JOIN
decisions = db.query(Decision).options(
    joinedload(Decision.communications)
).all()

# 添加索引
# migrations/add_indexes.py
def upgrade():
    op.create_index(
        'idx_decisions_timestamp',
        'ai_decisions',
        ['timestamp']
    )
    op.create_index(
        'idx_trades_symbol_timestamp',
        'trades',
        ['symbol', 'timestamp']
    )
```

2. **API响应缓存**
```python
from functools import lru_cache
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache

@app.get("/api/data/market/{symbol}")
@cache(expire=60)  # 缓存60秒
async def get_market_data(symbol: str):
    # 获取市场数据
    return await fetch_market_data(symbol)

# 使用Redis缓存
from redis import Redis
redis_client = Redis(host='localhost', port=6379)

def get_cached_klines(symbol: str, interval: str):
    cache_key = f"klines:{symbol}:{interval}"
    cached = redis_client.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    data = fetch_klines_from_api(symbol, interval)
    redis_client.setex(cache_key, 300, json.dumps(data))  # 5分钟过期
    return data
```

3. **异步处理优化**
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

# 并行调用多个分析AI
async def run_parallel_analysis(symbols):
    tasks = [
        technical_analyst.analyze(symbol),
        fundamental_analyst.analyze(symbol),
        sentiment_analyst.analyze(symbol),
        risk_assessor.analyze(symbol)
    ]
    results = await asyncio.gather(*tasks)
    return results

# 使用线程池处理CPU密集任务
executor = ThreadPoolExecutor(max_workers=4)

def calculate_indicators(kline_data):
    # CPU密集的指标计算
    loop = asyncio.get_event_loop()
    return loop.run_in_executor(
        executor,
        _calculate_indicators_sync,
        kline_data
    )
```

4. **前端性能优化**
```typescript
// 使用React.memo避免不必要的重渲染
const PositionRow = React.memo(({ position }) => {
  return (
    <tr>
      <td>{position.symbol}</td>
      <td>{position.amount}</td>
    </tr>
  );
});

// 虚拟滚动处理大列表
import { FixedSizeList } from 'react-window';

const TradeList = ({ trades }) => {
  return (
    <FixedSizeList
      height={600}
      itemCount={trades.length}
      itemSize={50}
    >
      {({ index, style }) => (
        <div style={style}>
          {trades[index].symbol} - {trades[index].price}
        </div>
      )}
    </FixedSizeList>
  );
};

// 防抖处理频繁更新
import { useDebouncedCallback } from 'use-debounce';

const Search = () => {
  const debounced = useDebouncedCallback(
    (value) => {
      searchAPI(value);
    },
    500
  );
  
  return <input onChange={(e) => debounced(e.target.value)} />;
};
```

5. **Claude API调用优化**
```python
# 批量处理减少API调用
class BatchProcessor:
    def __init__(self, batch_size=5):
        self.batch = []
        self.batch_size = batch_size
    
    async def add_task(self, task):
        self.batch.append(task)
        
        if len(self.batch) >= self.batch_size:
            await self.process_batch()
    
    async def process_batch(self):
        # 构建批量请求
        messages = [
            {"role": "user", "content": task.prompt}
            for task in self.batch
        ]
        
        # 一次API调用处理多个任务
        results = await anthropic.messages.batch_create(
            model="claude-sonnet-4-20250514",
            messages=messages
        )
        
        self.batch.clear()
        return results
```

**性能监控指标:**
- API响应时间: <200ms (P95)
- 数据库查询: <50ms (P95)
- AI决策完整流程: <30秒
- WebSocket延迟: <100ms
- 前端首屏加载: <2秒

**代码实现要求:**
1. performance_optimizer.py - 性能优化工具集
2. 数据库迁移脚本(添加索引)
3. 缓存配置和管理
4. 性能监控仪表盘
5. 优化前后对比报告

请提供完整的优化实现和测试结果。
```

---

## 提示词5.3: 日志和监控系统

```
我需要实现完善的日志和监控系统:

**日志系统设计:**

1. **日志级别和格式**
```python
import logging
from logging.handlers import RotatingFileHandler
import json

# 自定义JSON格式化器
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # 添加额外字段
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'trade_id'):
            log_data['trade_id'] = record.trade_id
            
        return json.dumps(log_data, ensure_ascii=False)

# 配置日志
def setup_logging():
    logger = logging.getLogger('crypto_trading')
    logger.setLevel(logging.INFO)
    
    # 文件处理器 - 按大小轮转
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(JSONFormatter())
    
    # 错误日志单独记录
    error_handler = RotatingFileHandler(
        'logs/error.log',
        maxBytes=10*1024*1024,
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(JSONFormatter())
    
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    
    return logger
```

2. **不同模块的日志记录**
```python
# AI决策日志
class AILogger:
    def __init__(self):
        self.logger = logging.getLogger('ai_decisions')
    
    def log_decision(self, ai_name, input_data, output, duration):
        self.logger.info(
            'AI决策完成',
            extra={
                'ai_name': ai_name,
                'input_hash': hash(str(input_data)),
                'output_decision': output.get('decision'),
                'confidence': output.get('confidence'),
                'duration_ms': duration * 1000
            }
        )

# 交易日志
class TradeLogger:
    def __init__(self):
        self.logger = logging.getLogger('trades')
    
    def log_order(self, order_data):
        self.logger.info(
            '订单提交',
            extra={
                'trade_id': order_data['id'],
                'symbol': order_data['symbol'],
                'side': order_data['side'],
                'price': order_data['price'],
                'quantity': order_data['quantity']
            }
        )
    
    def log_execution(self, trade_id, status, pnl=None):
        self.logger.info(
            '订单执行',
            extra={
                'trade_id': trade_id,
                'status': status,
                'pnl': pnl
            }
        )
```

3. **监控指标收集**
```python
from prometheus_client import Counter, Histogram, Gauge
import time

# 定义指标
api_requests = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

api_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration',
    ['endpoint']
)

active_positions = Gauge(
    'active_positions_count',
    'Number of active positions'
)

total_balance = Gauge(
    'account_balance_usd',
    'Account balance in USD'
)

ai_decision_time = Histogram(
    'ai_decision_duration_seconds',
    'AI decision making duration',
    ['ai_type']
)

# 使用装饰器记录指标
def monitor_api_call(endpoint):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                api_requests.labels(
                    method='GET',
                    endpoint=endpoint,
                    status='success'
                ).inc()
                return result
            except Exception as e:
                api_requests.labels(
                    method='GET',
                    endpoint=endpoint,
                    status='error'
                ).inc()
                raise
            finally:
                duration = time.time() - start
                api_duration.labels(endpoint=endpoint).observe(duration)
        return wrapper
    return decorator

# 定期更新指标
async def update_metrics():
    while True:
        positions = await get_current_positions()
        active_positions.set(len(positions))
        
        account = await get_account_info()
        total_balance.set(account['total_balance'])
        
        await asyncio.sleep(10)  # 每10秒更新
```

4. **告警系统**
```python
class AlertSystem:
    def __init__(self):
        self.logger = logging.getLogger('alerts')
        self.thresholds = {
            'loss': -0.05,  # 5%亏损
            'api_error_rate': 0.1,  # 10%错误率
            'latency': 5.0  # 5秒延迟
        }
    
    async def check_alerts(self):
        # 检查亏损
        account = await get_account_info()
        if account['today_pnl_pct'] < self.thresholds['loss']:
            await self.send_alert(
                level='CRITICAL',
                message=f"当日亏损超过{abs(self.thresholds['loss'])*100}%",
                data={'pnl': account['today_pnl_pct']}
            )
        
        # 检查API错误率
        error_rate = await self.get_error_rate()
        if error_rate > self.thresholds['api_error_rate']:
            await self.send_alert(
                level='WARNING',
                message=f"API错误率过高: {error_rate*100}%",
                data={'error_rate': error_rate}
            )
    
    async def send_alert(self, level, message, data):
        # 记录日志
        self.logger.warning(f"[{level}] {message}", extra=data)
        
        # 发送通知(邮件/Telegram/企业微信)
        # await send_telegram_message(message)
        # await send_email_alert(level, message, data)
```

5. **Grafana监控仪表盘配置**
```json
{
  "dashboard": {
    "title": "Crypto Trading AI监控",
    "panels": [
      {
        "title": "账户余额",
        "targets": [
          {
            "expr": "account_balance_usd"
          }
        ],
        "type": "graph"
      },
      {
        "title": "API请求成功率",
        "targets": [
          {
            "expr": "rate(api_requests_total{status='success'}[5m]) / rate(api_requests_total[5m])"
          }
        ],
        "type": "stat"
      },
      {
        "title": "AI决策耗时分布",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, ai_decision_duration_seconds)"
          }
        ],
        "type": "heatmap"
      }
    ]
  }
}
```

**代码实现要求:**
1. logging_config.py - 日志配置
2. monitoring.py - 监控指标定义
3. alerts.py - 告警系统
4. prometheus.yml - Prometheus配置
5. grafana_dashboard.json - Grafana仪表盘
6. 日志分析脚本(log_analyzer.py)

请提供完整的日志和监控实现。
```

---

## 提示词5.4: 错误处理和容错机制

```
我需要实现健壮的错误处理和容错机制:

**错误处理策略:**

1. **分层错误处理**
```python
# 自定义异常类
class TradingSystemError(Exception):
    """基础异常类"""
    pass

class APIError(TradingSystemError):
    """API调用错误"""
    pass

class InsufficientBalanceError(TradingSystemError):
    """余额不足"""
    pass

class RiskLimitExceededError(TradingSystemError):
    """超过风险限制"""
    pass

class AIDecisionError(TradingSystemError):
    """AI决策错误"""
    pass

# 错误处理装饰器
def handle_errors(retries=3, backoff=2):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(retries):
                try:
                    return await func(*args, **kwargs)
                
                except APIError as e:
                    last_exception = e
                    wait_time = backoff ** attempt
                    logger.warning(
                        f"API错误,第{attempt+1}次重试,等待{wait_time}秒",
                        extra={'error': str(e)}
                    )
                    await asyncio.sleep(wait_time)
                
                except InsufficientBalanceError as e:
                    # 余额不足不重试
                    logger.error("余额不足,停止交易")
                    raise
                
                except RiskLimitExceededError as e:
                    # 风险超限不重试
                    logger.error("超过风险限制,拒绝交易")
                    raise
                
                except Exception as e:
                    last_exception = e
                    logger.error(f"未知错误: {str(e)}")
                    if attempt == retries - 1:
                        raise
                    await asyncio.sleep(backoff ** attempt)
            
            raise last_exception
        
        return wrapper
    return decorator
```

2. **API调用容错**
```python
class ResilientAPIClient:
    def __init__(self, max_retries=3, timeout=10):
        self.max_retries = max_retries
        self.timeout = timeout
        self.circuit_breaker = CircuitBreaker()
    
    @handle_errors(retries=3)
    async def call_with_circuit_breaker(self, func, *args, **kwargs):
        if self.circuit_breaker.is_open():
            raise APIError("Circuit breaker开启,暂停API调用")
        
        try:
            result = await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=self.timeout
            )
            self.circuit_breaker.record_success()
            return result
        
        except asyncio.TimeoutError:
            self.circuit_breaker.record_failure()
            raise APIError("API调用超时")
        
        except Exception as e:
            self.circuit_breaker.record_failure()
            raise

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = 'CLOSED'
    
    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
            logger.warning("Circuit breaker开启")
    
    def record_success(self):
        self.failure_count = 0
        self.state = 'CLOSED'
    
    def is_open(self):
        if self.state == 'OPEN':
            # 检查是否可以半开
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'
                return False
            return True
        return False
```

3. **数据库事务处理**
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def transaction():
    """数据库事务上下文管理器"""
    session = get_db_session()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error(f"事务回滚: {str(e)}")
        raise
    finally:
        await session.close()

# 使用示例
async def execute_trade(order_data):
    async with transaction() as session:
        # 记录订单
        order = Order(**order_data)
        session.add(order)
        
        # 更新仓位
        position = await session.query(Position).filter_by(
            symbol=order.symbol
        ).first()
        
        if position:
            position.update(order)
        else:
            position = Position.from_order(order)
            session.add(position)
        
        # 记录交易历史
        trade = Trade.from_order(order)
        session.add(trade)
```

4. **优雅关闭**
```python
import signal

class GracefulShutdown:
    def __init__(self):
        self.is_shutting_down = False
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
    
    def shutdown(self, signum, frame):
        if self.is_shutting_down:
            logger.warning("强制退出")
            sys.exit(1)
        
        logger.info("开始优雅关闭...")
        self.is_shutting_down = True
        
        # 停止接受新任务
        workflow_engine.stop_accepting_tasks()
        
        # 等待当前任务完成
        logger.info("等待当前任务完成...")
        workflow_engine.wait_for_completion(timeout=30)
        
        # 关闭WebSocket连接
        logger.info("关闭WebSocket连接...")
        websocket_manager.close_all()
        
        # 关闭数据库连接
        logger.info("关闭数据库连接...")
        database.close()
        
        logger.info("系统已安全关闭")
        sys.exit(0)
```

5. **健康检查端点**
```python
@app.get("/health")
async def health_check():
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "checks": {}
    }
    
    # 检查数据库
    try:
        await database.execute("SELECT 1")
        health_status["checks"]["database"] = "ok"
    except Exception as e:
        health_status["checks"]["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # 检查币安API
    try:
        await binance_api.ping()
        health_status["checks"]["binance_api"] = "ok"
    except Exception as e:
        health_status["checks"]["binance_api"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # 检查Redis
    try:
        await redis_client.ping()
        health_status["checks"]["redis"] = "ok"
    except Exception as e:
        health_status["checks"]["redis"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status
```

**代码实现要求:**
1. error_handlers.py - 错误处理器集合
2. circuit_breaker.py - 熔断器实现
3. graceful_shutdown.py - 优雅关闭
4. health_check.py - 健康检查
5. 错误恢复策略文档

请提供完整的容错机制实现。
```

---

## 提示词5.5: 安全性加固

```
我需要加强系统的安全性:

**安全措施:**

1. **API密钥管理**
```python
from cryptography.fernet import Fernet
import os

class SecureConfig:
    def __init__(self):
        # 从环境变量读取加密密钥
        self.encryption_key = os.getenv('ENCRYPTION_KEY')
        if not self.encryption_key:
            raise ValueError("未设置ENCRYPTION_KEY环境变量")
        
        self.cipher = Fernet(self.encryption_key.encode())
    
    def encrypt_api_key(self, api_key: str) -> str:
        """加密API密钥"""
        encrypted = self.cipher.encrypt(api_key.encode())
        return encrypted.decode()
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        """解密API密钥"""
        decrypted = self.cipher.decrypt(encrypted_key.encode())
        return decrypted.decode()
    
    def load_credentials(self):
        """从环境变量或加密文件加载凭据"""
        return {
            'binance_api_key': self.decrypt_api_key(
                os.getenv('BINANCE_API_KEY_ENCRYPTED')
            ),
            'binance_api_secret': self.decrypt_api_key(
                os.getenv('BINANCE_API_SECRET_ENCRYPTED')
            )
        }

# 密钥轮转
def rotate_api_keys():
    """定期轮转API密钥"""
    # 生成新密钥
    new_key, new_secret = create_new_binance_keys()
    
    # 验证新密钥有效
    if verify_keys(new_key, new_secret):
        # 更新系统配置
        update_config(new_key, new_secret)
        
        # 删除旧密钥
        revoke_old_keys()
```

2. **访问控制**
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """验证JWT token"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token已过期"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的Token"
        )

# 受保护的路由
@app.post("/api/trading/manual")
async def manual_trade(
    order: OrderRequest,
    user = Depends(verify_token)
):
    # 只有验证通过的用户才能手动交易
    return await execute_trade(order)
```

3. **输入验证**
```python
from pydantic import BaseModel, validator, Field

class OrderRequest(BaseModel):
    symbol: str = Field(..., regex='^[A-Z]{3,10}USDT$')
    side: str = Field(..., regex='^(BUY|SELL)$')
    quantity: float = Field(..., gt=0, lt=1000)
    price: Optional[float] = Field(None, gt=0)
    
    @validator('symbol')
    def validate_symbol(cls, v):
        allowed_symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
        if v not in allowed_symbols:
            raise ValueError(f'只允许交易{allowed_symbols}')
        return v
    
    @validator('quantity')
    def validate_quantity(cls, v, values):
        # 根据币种限制最大数量
        symbol = values.get('symbol')
        max_quantities = {
            'BTCUSDT': 10,
            'ETHUSDT': 100,
            'SOLUSDT': 1000
        }
        if v > max_quantities.get(symbol, 0):
            raise ValueError(f'数量超过限制')
        return v
```

4. **SQL注入防护**
```python
# 使用参数化查询
from sqlalchemy import text

# ❌ 危险 - SQL注入风险
def get_trades_unsafe(symbol):
    query = f"SELECT * FROM trades WHERE symbol = '{symbol}'"
    return db.execute(query).fetchall()

# ✅ 安全 - 参数化查询
def get_trades_safe(symbol):
    query = text("SELECT * FROM trades WHERE symbol = :symbol")
    return db.execute(query, {'symbol': symbol}).fetchall()

# 或使用ORM
def get_trades_orm(symbol):
    return db.query(Trade).filter(Trade.symbol == symbol).all()
```

5. **Rate Limiting**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/trading/manual")
@limiter.limit("10/minute")  # 每分钟最多10次
async def manual_trade(request: Request, order: OrderRequest):
    return await execute_trade(order)

@app.post("/api/ai/trigger")
@limiter.limit("5/hour")  # 每小时最多5次
async def trigger_analysis(request: Request):
    return await run_analysis()
```

6. **审计日志**
```python
class AuditLogger:
    def __init__(self):
        self.logger = logging.getLogger('audit')
    
    def log_action(self, user_id, action, details):
        self.logger.info(
            'USER_ACTION',
            extra={
                'user_id': user_id,
                'action': action,
                'details': details,
                'timestamp': datetime.now().isoformat(),
                'ip': get_client_ip()
            }
        )

# 记录关键操作
audit_logger.log_action(
    user_id=user.id,
    action='MANUAL_TRADE',
    details={
        'symbol': order.symbol,
        'side': order.side,
        'quantity': order.quantity
    }
)
```

**代码实现要求:**
1. security.py - 安全工具集
2. authentication.py - 认证系统
3. encryption.py - 加密工具
4. audit.py - 审计日志
5. 安全配置清单(SECURITY.md)

请提供完整的安全加固实现。
```

