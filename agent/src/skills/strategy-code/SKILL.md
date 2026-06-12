---
name: strategy-code
description: Create, modify, and optimize quantitative trading strategies, then backtest and evaluate them. Use this skill whenever the user wants to write a trading strategy, generate strategy code, build a backtest, or asks about quantitative trading logic (e.g., "write a moving average crossover strategy", "generate RSI strategy code", "create a momentum strategy").
category: strategy
---

## Authentication (ai-finance-resource)

The backtest engine at `https://10.2.31.12:21006/ai-finance-resource/` requires cookie-based authentication.

### Required Cookies

| Cookie Name | Test Value (fixed) |
|---|---|
| `admin_login` | `%7B%22uid%22%3A%222816446863325978636%22%2C%22ts%22%3A%221780491660289%22%7D` |
| `baas-authLink-Token` | `eyJKV1QiOiJKV1QiLCJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJiYWFzTG9naW5UaW1lIjoxNzgwNDkxNjYwMjg5LCJsb2dpblZlcnNpb24iOjEsImNsaWVudF90eXBlIjoyLCJ1c2VySWQiOjI4MTY0NDY4NjMzMjU5Nzg2MzYsImlhdCI6MTc4MDQ5MTY2MCwianRpIjoiMTg2OWM2YTYzYjRiNDRjMzk1MGU0ZWIwNmFlY2RiNWYiLCJ1c2VyQWdlbnRNZDUiOiI5MWNhYmEyNGZmNmFlYmEzIiwidG9rZW4iOiIxMDU4MDU4YWFkY2E4NjZiMTk3Y2MxYzJkMGY5ZGI4N2ExNzNmOWRjZjNjOThkZWE3NTJkMWVhZDUxNmZmN2EyYSJ9.ua0zBkYcq2BPrcwQ_ECNg8m_RWpo5gh8pqwOyPUjz2w` |

### Cookie Management

1. **Current (test)**: use the fixed values above for all HTTP requests to `10.2.31.12:21006`.
2. **Future (auto-refresh)**: navigate to the platform via browser automation → extract cookies → cache → refresh on JWT expiry.

---

## Workflow (HITL — Human-in-the-Loop)

```
①需求解析 ──→ ②要素收集 ──→ ③策略解读 ──→ ④策略编码 ──→ ⑤语法检查 ──→ ⑥输出交付
                  ↑               │                                   │
                  │  用户要求修改 │                                   │
                  └───────────────┘                                   │
                                                                      │
                                          用户确认后进入④             │
```

### Step-by-step

1. **需求解析** — parse user intent: extract strategy type and key parameters
2. **要素收集** — collect missing elements via 6-item multiple-choice; loop back on changes
3. **策略解读** — plain-language interpretation; **wait for user confirmation** before coding
4. **策略编码** — write `strategy.py` implementing `on_bar(context, bar_data) -> list[Signal]`
5. **语法检查** — AST check + quality checklist
6. **输出交付** — `emit_inline_artifact` (mime `text/x-python`)

**You only write `strategy.py`.** Stock codes are injected by the platform — iterate `bar_data.keys()`, never hardcode tickers.

### Runtime Execution Architecture (Full Pipeline)

```
用户输入
   │
   ▼
┌─────────────────────────────────────────────────────────────────┐
│ ② 要素收集 Pipeline（最多 2 轮交互）                            │
│                                                                 │
│ ┌──────────────────────────────────┐                            │
│ │ 1. 意图检测 + 要素提取 (LLM)     │ ← 合并 1 次调用            │
│ │    ~50 tokens, < 500ms           │   输出: {intent, filled}   │
│ ├──────────────────────────────────┤                            │
│ │ 2. 缺失判断 (纯逻辑)             │ ← 无 LLM                   │
│ │    filled vs 6 要素全集 → missing│   missing=[] → 跳至 ③      │
│ ├──────────────────────────────────┤                            │
│ │ 3. 生成问题 + 选项 (模板)        │ ← 选项固定枚举             │
│ │    渲染 missing 要素的 emoji 卡片│                            │
│ ├──────────────────────────────────┤                            │
│ │ 4. 解析回答 (LLM)                │ ← 用户回复后触发           │
│ │    数字/关键词/模糊→要素值映射   │ "都行"→默认 "1 2 1"→按位   │
│ └──────────────────────────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
   │ 6 要素集齐
   ▼
┌─────────────────────────────────────────────────────────────────┐
│ ③ 策略解读 (LLM → 前端 emoji 卡片)                              │
│                                                                 │
│ Skill 调 LLM 生成结构化解读文本                                 │
│ 前端按 emoji 渲染为可读卡片:                                    │
│   📊 数据需求  📈 买入条件  📉 卖出条件                         │
│   ⚖️ 仓位管理  🛡️ 大盘过滤  ⚠️ 边界处理                           │
│                                                                 │
│ HITL: 用户确认 → ④ / 修改 → 回 ②                                │
└─────────────────────────────────────────────────────────────────┘
   │ 用户确认
   ▼
┌─────────────────────────────────────────────────────────────────┐
│ ④ 策略编码 (LLM)                                                │
│                                                                 │
│ LLM 生成 on_bar(context, bar_data) 完整 Python 代码             │
│ 遵循 Signal / context / ta 模块 API                             │
└─────────────────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────────────────┐
│ ⑤ 语法校验 (Sandbox)                                            │
│                                                                 │
│ sandbox 中执行: python -c "import ast; ast.parse(...)"          │
│ + 11 项 Quality Checklist 自检                                  │
│ 失败 → 修复 → 重试                                              │
└─────────────────────────────────────────────────────────────────┘
   │
   ▼
⑥ 输出交付 (emit_inline_artifact, AST 自动校验)
```

**Key constraints:**
- Step 1-2 must complete in one turn (no `ask_user` between intent detection and first question)
- Options are fixed per element — never invent new options
- Fuzzy replies resolved with defaults, never re-ask
- ③ interpretation rendered as emoji cards on frontend
- ⑤ syntax check runs in sandbox, not inline

---

## ① Requirements Parsing (需求解析)

Extract from the user's description:
- **Strategy type**: trend-following / mean-reversion / momentum / multi-factor / ...
- **Key parameters**: any specific numbers mentioned (e.g., "MA5", "RSI below 30")

**Stock codes are injected by the platform at runtime** — do NOT ask. Strategy code always iterates `bar_data.keys()`.

If the request is too vague ("build a strategy"), provide 2-3 concrete directions and let the user choose.

## ② Elements Collection (要素收集)

Collect missing elements via **6-item multiple-choice**. Do NOT proceed to interpretation until all are filled.

| # | 要素 | 含义 | 选项 |
|---|---|---|---|
| 1 | **策略风格** | 策略方法论 | ① 趋势跟踪 ② 均值回归 ③ 动量策略 ④ 突破策略 ⑤ 多因子 |
| 2 | **技术指标** | 使用的分析指标 | ① 均线 ② MACD ③ RSI ④ 布林带 ⑤ 多指标组合 |
| 3 | **买入条件** | 什么时候买 | ① 金叉 ② 超卖反弹 ③ 底背离 ④ 突破前高 ⑤ 触及下轨 |
| 4 | **卖出条件** | 什么时候卖 | ① 死叉 ② 超买回落 ③ MACD柱转负 ④ 跌破前低 ⑤ 触及上轨 |
| 5 | **仓位管理** | 每只股票买多少 | ① 固定25% ② 固定30% ③ 固定50% ④ ATR动态 ⑤ 等权分配 |
| 6 | **大盘过滤** | 是否参考大盘 | ① 需要（大盘弱时空仓） ② 不需要 ③ 仅上涨时开仓 |

### Runtime Behavior (aligned with Architecture above)

**First turn:**
1. Intent detection + element extraction merged into one LLM call
2. If all 6 filled → skip to ③
3. If gaps → template-render questions for missing elements only

**Reply turn (用户回复要素):**
1. Parse reply with LLM: map numbers/keywords/fuzzy answers to element values
2. Fuzzy handling:
   - `"都行"` / `"随便"` → use default (① for each unresolved)
   - `"跟第一个差不多"` → reuse previous round selection
   - `"1 2 1 2 2 1"` → positional mapping to elements in ask order
   - `"MACD 金叉 死叉"` → semantic mapping
3. Merge into filled set; if gaps remain → re-render only missing
4. All filled → proceed to ③

### Loop Rule

- Any element missing → `ask_user()`, resume from here
- User says "change X" at any step → back here, update, re-proceed

## ③ Strategy Interpretation (策略解读 · LLM → 前端 emoji 卡片)

Once all 6 elements are collected, write a **plain-language interpretation**. Cover:

1. **Data needs**: how many bars of history? (max 250 for `get_history`)
2. **Signal logic**: entry + exit conditions in plain language
3. **Position sizing**: fixed or dynamic? what value?
4. **Edge cases**: insufficient data / NaN / same-day conflicts
5. **Risk note**: system stop-loss/profit-take runs on top

**Format:**

```
## 策略解读：双均线金叉策略

- 标的：由平台注入，遍历 bar_data.keys()
- 数据：每日行情，需要最近 60 根 K 线
- 买入条件：MA5 上穿 MA20（金叉），无持仓时买入
- 卖出条件：MA5 下穿 MA20（死叉），持仓时卖出
- 仓位：固定 30%（position_ratio=0.3）
- 过滤：无
- 边界处理：历史数据不足 60 条时跳过
- 风控：系统止盈止损叠加生效
```

### HITL Gate

- Present interpretation → **explicitly ask "确认以上解读无误？"**
- User confirms → proceed to ④
- User requests changes → back to ②
- Do NOT write code until confirmed

---

## `on_bar` API Specification

### Entry Function

```python
def on_bar(context, bar_data) -> list:
    """
    Args:
        context: strategy context
        bar_data: dict[str, dict] — {ts_code: {open, high, low, close, pre_close, change, pct_chg, vol, amount, trade_date}}
    Returns:
        list[Signal] — buy/sell signals
    """
    signals = []
    return signals
```

### context Object

| Accessor | Returns | Description |
|---|---|---|
| `context.get_history(ts_code, count)` | `DataFrame` or `None` | Last `count` daily bars (OHLCV), date-ascending |
| `context.get_position(ts_code)` | `Position` or `None` | Current position; `None` = no position |
| `context.get_index_bar(code)` | `dict` or `None` | Today's index bar |
| `context.get_index_history(code, count)` | `DataFrame` | Last `count` index bars |
| `context.benchmark_code` | `str` | Benchmark from task config — **use this, not hardcoded** |
| `context.get_total_value()` | `float` | Total portfolio value |

### Signal Object

```python
Signal(
    ts_code="000001.SZ",       # required
    direction="BUY",           # "BUY" or "SELL"
    position_ratio=0.3,        # 0.0~1.0 (conflicts with quantity)
    quantity=1000,             # takes priority over position_ratio
    reason="MA5金叉MA20"       # optional
)
```

- `position_ratio` / `quantity` are mutually exclusive; `quantity` wins
- Never emit both BUY and SELL for same stock on same day

### Position Object

```python
pos = context.get_position(ts_code)
if pos:
    pos.ts_code / pos.quantity / pos.avg_cost / pos.buy_date
```

### ta Module — Built-in Indicators

**Trend:** `ta.sma` / `ta.ema` / `ta.wma` / `ta.kama` / `ta.adx` / `ta.sar`

**Momentum:** `ta.macd` → `{macd, signal, histogram}` / `ta.rsi` / `ta.stoch` / `ta.awesome_oscillator` / `ta.williams_r` / `ta.cci` / `ta.fisher_transform`

**Channels:** `ta.bbands` → `{mid, upper, lower}` / `ta.atr` / `ta.donchian` / `ta.keltner_channel`

**Statistical:** `ta.zscore` / `ta.bias` / `ta.hurst_exponent`

---

## ④-⑤ Quality Checklist (编码后自检 · Sandbox)

- [ ] Signature: `def on_bar(context, bar_data) -> list:`
- [ ] Returns `list[Signal]`
- [ ] Iterates `bar_data.keys()` — no hardcoded tickers
- [ ] Uses `context.benchmark_code` — no hardcoded index
- [ ] Boundary: `if df is None or len(df) < N: continue`
- [ ] NaN: `pd.isna()` check before using indicator values
- [ ] No BUY+SELL for same stock on same day
- [ ] No `if __name__ == "__main__"`
- [ ] No duplicated stop-loss logic
- [ ] `get_history` count ≤ 250

---

## Complete Examples

### Example 1: Dual MA Crossover

```python
def on_bar(context, bar_data):
    signals = []
    for ts_code, bar in bar_data.items():
        df = context.get_history(ts_code, 60)
        if df is None or len(df) < 60:
            continue
        close = df['close']
        ma5 = ta.sma(close, 5)
        ma20 = ta.sma(close, 20)
        if ma5.iloc[-1] > ma20.iloc[-1] and ma5.iloc[-2] <= ma20.iloc[-2]:
            if context.get_position(ts_code) is None:
                signals.append(Signal(ts_code=ts_code, direction="BUY", position_ratio=0.3, reason="MA5金叉MA20"))
        elif ma5.iloc[-1] < ma20.iloc[-1] and ma5.iloc[-2] >= ma20.iloc[-2]:
            if context.get_position(ts_code) is not None:
                signals.append(Signal(ts_code=ts_code, direction="SELL", reason="MA5死叉MA20"))
    return signals
```

### Example 2: RSI + Bollinger Bands

```python
def on_bar(context, bar_data):
    signals = []
    for ts_code, bar in bar_data.items():
        df = context.get_history(ts_code, 30)
        if df is None or len(df) < 30:
            continue
        close = df['close']
        rsi_val = ta.rsi(close, 14)
        boll = ta.bbands(close, 20, 2.0)
        current_rsi = rsi_val.iloc[-1]
        current_close = close.iloc[-1]
        lower_band = boll['lower'].iloc[-1]
        upper_band = boll['upper'].iloc[-1]
        pos = context.get_position(ts_code)
        if current_rsi < 30 and current_close <= lower_band:
            if pos is None:
                signals.append(Signal(ts_code=ts_code, direction="BUY", position_ratio=0.25, reason=f"RSI={current_rsi:.1f}超卖"))
        elif current_rsi > 70 and current_close >= upper_band:
            if pos is not None:
                signals.append(Signal(ts_code=ts_code, direction="SELL", reason=f"RSI={current_rsi:.1f}超买"))
    return signals
```

### Example 3: MACD Divergence

```python
def on_bar(context, bar_data):
    signals = []
    for ts_code, bar in bar_data.items():
        df = context.get_history(ts_code, 120)
        if df is None or len(df) < 120:
            continue
        close = df['close']
        macd_df = ta.macd(close, 12, 26, 9)
        histogram = macd_df['histogram']
        recent_close = close.iloc[-30:]
        recent_hist = histogram.iloc[-30:]
        prev_close = close.iloc[-60:-30]
        prev_hist = histogram.iloc[-60:-30]
        if len(prev_close) > 0 and len(prev_hist) > 0:
            if recent_close.min() < prev_close.min() and recent_hist.min() > prev_hist.min():
                if context.get_position(ts_code) is None:
                    signals.append(Signal(ts_code=ts_code, direction="BUY", position_ratio=0.2, reason="MACD底背离"))
        pos = context.get_position(ts_code)
        if pos and histogram.iloc[-1] < 0 and histogram.iloc[-2] >= 0:
            signals.append(Signal(ts_code=ts_code, direction="SELL", reason="MACD柱转负"))
    return signals
```

---

## Common Patterns

### Market Regime Filter

```python
index_bar = context.get_index_bar(context.benchmark_code)
if index_bar and index_bar['pct_chg'] < -2.0:
    return []
```

### ATR Dynamic Position Sizing

```python
atr_val = ta.atr(df['high'], df['low'], df['close'], 14).iloc[-1]
volatility_ratio = atr_val / bar['close']
adjusted = min(max(0.3 * (0.02 / max(volatility_ratio, 0.01)), 0.1), 0.5)
```

---

## Key Constraints

1. Always check `df is not None and len(df) >= N` before computing indicators
2. NaN: indicators produce NaN early — use `.iloc[-1]` or `pd.isna()`
3. Never emit BUY+SELL for same stock on same bar
4. `get_history` count ≤ 250
5. No duplicated stop-loss (system handles it)
6. Output only `strategy.py`

## ⑥ Delivery (输出交付)

```
emit_inline_artifact(
    content=<strategy.py content>,
    mime="text/x-python",
    title="<strategy name with key params>",
    description="<one-line summary>",
    file_name="strategy.py"
)
```

- `title`: e.g., "RSI(14)+BB(20,2)组合策略"
- `description`: e.g., "RSI<30且触及布林下轨买入25%; RSI>70且触及上轨卖出"
- AST validation runs automatically; fix any `violations` before final delivery.
