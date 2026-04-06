# Crypto Trading MAS (MVP)

A controllable and testable multi-agent crypto trading system built with an MVP-first approach.

## Project Goal

Build a minimum executable vertical slice for crypto trade planning with clear role boundaries and deterministic behavior.

Core flow:

1. TA analyst
2. Sentiment analyst
3. Risk officer
4. Final trade plan

## MVP Principles

- Deterministic first, intelligence later.
- Mock tools before external APIs.
- Policy-constrained decisions over unconstrained prompt-only logic.
- Full execution trace for replay and audit.

Detailed governance is defined in AGENTS.md.

## Current Structure

- README.md: project overview and development workflow.
- AGENTS.md: architecture boundaries, constraints, and quality gates.
- pyproject.toml: Python project metadata.
- .env.example: required runtime environment keys.
- app/main.py: application entrypoint.
- app/config/settings.py: central settings.
- app/schemas/: task and report contracts.
- app/agents/base/: base abstractions and trace.
- app/agents/master/: orchestration logic.
- app/agents/ta_analyst/: TA role modules and tools.
- app/agents/sentiment_analyst/: sentiment role modules and tools.
- app/agents/risk_officer/: risk role modules and tools.
- app/services/: service interfaces and mock implementations.
- app/workflows/master_workflow.py: top-level workflow.
- app/audits/tool_calls/: tool call logs.
- app/audits/agent_runs/: agent run traces.
- tests/: unit and workflow tests.
- docs/architecture.md: architecture notes.

## Agent Responsibilities

- Master agent orchestrates stage order and result composition.
- TA agent outputs TA-focused report fields only.
- Sentiment agent outputs sentiment-focused report fields only.
- Risk officer is the final approval gate and can force HOLD.

## Tool Boundary Rules

- Each agent owns a private toolset.
- No cross-agent tool sharing.
- Agent-local tools stay under that agent tools directory.
- Tool selection is task-aware, not exhaustive by default.
- Every tool validates payload and returns serializable output.

## Definition of Done

- Code compiles.
- Unit tests pass.
- Execution trace records tool selection and tool calls.
- No cross-agent tool leakage.

## Do Not

- Do not introduce shared global tools.
- Do not connect real exchange APIs in MVP stage.
- Do not skip tests.
- Do not let one prompt decide everything without policy constraints.

## Development Workflow

1. Implement deterministic policy and mock tools.
2. Add or update unit tests.
3. Run workflow-level happy path.
4. Verify trace completeness for one full run.
5. Update docs when boundaries or data flow changes.

## Roadmap

### Phase 1: Executable MVP

- Base agent, base tool, registry, trace.
- Deterministic toolsets for TA, sentiment, and risk.
- Master orchestrator with final trade plan.

### Phase 2: Hardening

- Expand failure-path tests.
- Standardize error and response shapes.
- Improve trace schema consistency.

### Phase 3: Controlled Intelligence

- Introduce constrained LLM assistance.
- Keep deterministic policy as hard guardrail.

## Non-Negotiable Principle

Safety and controllability are more important than feature speed.

