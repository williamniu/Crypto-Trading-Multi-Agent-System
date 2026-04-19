# Architecture Notes

## Goal

This repository implements a deterministic MVP for a multi-agent crypto trading system.
The current slice remains synchronous and policy-constrained, with mock providers still available by default and optional read-only live provider integrations for market data, sentiment search, and account state.

## Main Roles

- `master_agent`: orchestrates the workflow and combines role outputs into one draft trade plan.
- `ta_analyst`: produces only technical-analysis fields.
- `sentiment_analyst`: produces only sentiment-analysis fields.
- `risk_officer`: acts as the final approval gate and can force the final action to `HOLD`.

## Data Flow

1. A `Task` enters `MasterWorkflow`.
2. `MasterWorkflow` validates the input against `app/schemas/task.py`.
3. `MasterOrchestrator` creates an `ExecutionTrace`.
4. `MasterAgent` runs the three role-specific agents in fixed order:
   - TA
   - Sentiment
   - Risk
5. The master layer synthesizes a draft trade plan from TA and sentiment outputs.
6. The risk layer sizes the position, checks exposure, and approves or rejects the plan.
7. `MasterWorkflow` validates the final reports and trade plan against schema contracts.

## Why The Design Looks This Way

- Deterministic tools make unit tests stable.
- Role-specific toolsets prevent cross-agent leakage.
- Explicit decision policies keep business logic centralized instead of hidden inside prompts.
- Execution trace records stage transitions and tool I/O for offline replay.
- Stable service interfaces (`market_data_service`, `news_service`, `risk_service`) make provider upgrades easier without changing agent contracts.

## Node Mapping For Future LangGraph Migration

The current workflow already maps cleanly to a later LangGraph graph:

- `task_input`
- `ta_analysis`
- `sentiment_analysis`
- `draft_plan`
- `risk_review`
- `final_trade_plan`

The repository does not yet depend on LangGraph because the current project governance prioritizes a minimum executable vertical slice first. The orchestration order, boundaries, and state contracts are already aligned with a later graph-based migration.

## Boundaries That Must Stay Intact

- Agent-local tools live only under each agent's own `tools/` directory.
- Tool registration happens in the owning `toolset.py`.
- No agent mutates another agent's internal state.
- Risk approval is the final gate and overrides directional action when needed.
- Services can run in `mock` mode or read-only live-provider mode via configuration.
- Order placement is still out of scope; the live integrations only read market, news, and account data.
