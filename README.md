# Crypto Trading MAS

一个面向加密货币交易场景的多智能体 MVP 项目。
它的目标不是一开始就“接交易所、上大模型、全自动下单”，而是先把一个可执行、可测试、可审计、可扩展的最小垂直切片做扎实。

当前版本围绕 4 个角色构建：

1. `Master Agent`
2. `TA Analyst Agent`
3. `Sentiment Analyst Agent`
4. `Risk Officer Agent`

完整执行顺序固定为：

`TA -> Sentiment -> Risk -> Final Trade Plan`

## 这个项目在做什么

我在构建一个“可控”的多智能体交易系统，而不是一个把所有事情都交给单个 prompt 的黑盒。

系统会接收一个交易任务 `Task`，然后：

- 技术分析智能体读取行情数据，输出技术面报告
- 新闻情绪面智能体读取新闻搜索结果，输出情绪面报告
- 主智能体融合两者结果，生成草案交易计划
- 风控智能体根据风险参数、仓位暴露和盈亏比做最终审批
- 如果风控拒绝，最终动作会被强制改成 `HOLD`

最终输出包括：

- `ta_report`
- `sentiment_report`
- `risk_report`
- `trade_plan`
- `trace`

## 为什么这样设计

很多交易系统会过早追求“智能”，但真正难的是：

- 角色边界是否清晰
- 策略逻辑是否显式
- 工具调用是否可追踪
- 风控是否真的能覆盖前面的方向性判断
- 出错时能不能复盘

所以这个项目当前阶段坚持几个原则：

- `Deterministic first`：先确定性，再智能化
- `Mock before external APIs`：默认保留 mock，但允许按模块切换到真实只读数据源
- `Policy over prompt-only logic`：关键决策放在显式 policy 中
- `Trace everything important`：记录阶段流转和工具调用

## 当前项目价值

这个 MVP 的价值不在“预测涨跌有多准”，而在于它提供了一个真正可继续往上搭建的骨架：

- 它把多智能体职责切开了，避免一个 agent 包办所有决策
- 它把工具边界锁住了，避免 cross-agent tool leakage
- 它把风险控制放到了最后一道硬门槛
- 它把以后接入 LangGraph、真实市场数据、真实新闻源、甚至约束式 LLM 的路径提前留好了

如果后续要继续扩展，这套结构比“单文件 demo”更适合作为长期项目基础。

## 当前架构

### 1. Schema 层

位于 `app/schemas/`，定义所有输入输出契约：

- `Task`
- `TAReport`
- `SentimentReport`
- `RiskReport`
- `TradePlan`

这些 schema 的作用是把系统约束提前，不让 agent 随意输出格式漂移的数据。

### 2. Base 层

位于 `app/agents/base/`，提供：

- `BaseTool`
- `ToolRegistry`
- `BaseAgent`
- `ExecutionTrace`

这是整个多智能体框架的最小基础设施。

### 3. Agent 层

每个 agent 都有自己独立的：

- `agent.py`
- `toolset.py`
- `decision_policy.py`
- `tools/`

这保证了：

- 工具不共享
- 逻辑边界清晰
- policy 独立可测
- 未来替换单个 agent 更容易

### 4. Service 层

位于 `app/services/`，目前提供稳定接口以及可切换 provider：

- `market_data_service.py`：mock 或 WEEX 行情
- `news_service.py`：mock 或 Tavily 新闻搜索
- `risk_service.py`：mock 或 WEEX 账户快照
- `storage_service.py`
- `llm_client.py`：stub 或 OpenAI-compatible 解释增强

这里的重点不是“能力强”，而是“接口稳定”，方便未来逐步替换成真实实现。

### 5. Workflow / Orchestration 层

- `app/agents/master/agent.py`
- `app/agents/master/orchestrator.py`
- `app/workflows/master_workflow.py`

这一层负责：

- 固定执行顺序
- 整合多 agent 输出
- 生成最终 trade plan
- 验证结果是否满足 schema

## 和 LangGraph 的关系

我的整体目标是把它发展为一个基于 LangGraph 的多智能体交易系统。

但当前这个仓库刻意没有直接把复杂框架依赖塞进 MVP，原因是：

- 当前阶段最重要的是验证角色边界和决策链路
- 先把 deterministic policy 和 mock tool 跑通，测试会更稳定
- 一旦 schema、node 边界、状态流明确了，再迁移到 LangGraph 会更自然

当前工作流已经是 LangGraph-ready 的节点形态：

- `task_input`
- `ta_analysis`
- `sentiment_analysis`
- `draft_trade_plan`
- `risk_review`
- `final_trade_plan`

也就是说，现在不是“没朝 LangGraph 方向做”，而是在为 LangGraph 迁移先把底层边界打稳。

## 当前用了哪些方法和工具

### 方法

- 显式 `decision_policy.py`
- agent-local `toolset.py`
- mock service interface
- schema validation
- execution trace
- workflow-level orchestration
- optional constrained LLM explanation layer

### 技术栈

- Python 3.11+
- Pydantic v2
- Pytest

## 当前最小可行产品做到了什么

现在项目已经可以完成以下最小闭环：

1. 接收一个结构化交易任务
2. 运行 TA 工具链
3. 运行新闻情绪面工具链
4. 生成草案交易计划
5. 运行风控审批
6. 输出最终交易建议
7. 记录本次执行 trace
8. 通过单元测试和 workflow 测试

## 当前主要难点与解决思路

### 1. 多智能体容易变成“一个大脚本”

问题：
如果所有逻辑都写在一个 orchestrator 里，表面上叫多智能体，实际上很难维护。

解决：
把每个 agent 的工具、policy、agent 类和 toolset 拆开，主智能体只负责编排，不直接越权执行其他角色内部逻辑。

### 2. prompt-only 决策不可控

问题：
如果完全依赖 LLM 输出方向和仓位，结果很难稳定测试，也不利于后续审计。

解决：
把关键阈值放进 `decision_policy.py`，比如：

- TA signal thresholds
- sentiment impact thresholds
- risk/reward 审批阈值

### 3. 真实外部 API 集成需要与边界解耦

问题：
交易所 API、新闻 API、账户 API 一旦直接写进 agent/tool，会迅速把职责边界打乱。

解决：
把真实集成下沉到 `service`/provider 层，让 tool 和 agent 继续消费稳定 contract。

### 4. 风控容易沦为“建议”而不是“硬约束”

问题：
如果风险模块只是返回一句提示，主策略层可能绕过去。

解决：
明确规定 `Risk Officer` 是 final approval gate，一旦拒绝，最终 action 强制变成 `HOLD`。

## 目前还有哪些更好的思路

当前方案是一个很稳的 MVP，但后续还可以继续优化：

- 用 LangGraph 管理状态流和 node retry
- 引入更细粒度的市场 regime 判断
- 让 sentiment 不只做词典打分，而是做事件级别归因
- 让 risk 模块加入波动率、相关性和组合层约束
- 增加 backtest / replay 模块，直接用 trace 做离线回放
- 为 agent 输出增加 explainability 字段，方便展示和人工复核

## 下一步拓展方向

### Phase 1: 已完成的 MVP 基座

- Base agent / tool / registry / trace
- 三个子智能体的私有工具集
- 主智能体编排
- 风控最终审批
- Schema 验证
- 单元测试与工作流测试

### Phase 2: 强化与工程化

- 扩充失败路径测试
- 统一异常类型和错误响应
- 增强 trace 结构
- 加入可选的持久化审计目录

### Phase 3: 智能增强

- 引入受约束的 LLM 辅助，而不是放开式生成
- 用 LangGraph 管理复杂状态和分支
- 接入真实行情、新闻搜索与账户数据源
- 加入历史回测与模拟执行

## 当前 LLM 接入方式

当前版本已经支持把 LLM 接到每个 agent，但位置是“受约束分析层”，不是“直接决策层”。

- `TA agent` 会把 candles、指标、levels、deterministic signal 发送给 LLM，生成 `llm_summary`
- `Sentiment agent` 会把 headlines、source items、sentiment score、event impact 发送给 LLM，生成 `llm_summary`
- `Risk agent` 会把风险画像、draft plan、deterministic risk report 发送给 LLM，生成 `llm_summary`
- `Master agent` 会把三个 report 和 final plan 发给 LLM，生成最终 `trade_plan.llm_summary`

LLM 当前不会：

- 覆盖 TA signal
- 覆盖 sentiment score
- 覆盖 risk approval
- 直接决定 `BUY/SELL/HOLD`

这意味着当前系统里 LLM 带来的价值主要是：

- 提升分析解释能力
- 提供更灵活的文本化结论
- 为后续引入更强的模型/机器学习层预留接入口

### Phase 4: 真实交易前的最后一层

- 沙盒账户联调
- 风险监控告警
- 组合级仓位控制
- 下单前人工审批机制

## 项目结构

```text
app/
  agents/
    base/
    master/
    ta_analyst/
    sentiment_analyst/
    risk_officer/
  config/
  schemas/
  services/
  workflows/
tests/
docs/
AGENTS.md
README.md
```

## 如何运行

### 安装依赖

```bash
python -m pip install -e ".[dev]"
```

### 运行测试

```bash
pytest
```

### 跑一个本地示例

```bash
python -m app.main
```

## 示例输出特点

你会看到系统返回：

- 每个 agent 的独立报告
- 一个经过风控审批后的最终 `trade_plan`
- 一份完整 `trace`

其中 `trace` 会记录：

- `run_id`
- stage transitions
- tool calls
- tool input / output

## 项目原则

- 不共享全局工具
- 不接真实交易所 API
- 不跳过测试
- 不让单个 prompt 决定所有事情
- 安全性和可控性优先于功能速度

## 补充说明

如果你把这个项目看作“一个已经能赚钱的交易系统”，那它还不是。
如果你把它看作“一个已经有明确边界、能跑通、能测试、能继续往真实系统演化的多智能体交易架构基座”，那它已经成立了。
