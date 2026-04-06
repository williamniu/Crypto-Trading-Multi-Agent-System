# AGENTS.md

This document defines the operational rules for the multi-agent crypto trading MVP.
All contributors and automation should follow these constraints.

## Project rules

### Architecture constraints
- Each agent has its own private toolset.
- Tools must not be shared across agents.
- Agent-local tools live only under that agent's tools/ directory.
- Tool selection must be task-aware, not exhaustive by default.

### Current implementation stage
- Build the minimum executable vertical slice first.
- Use mock tools before integrating external APIs.
- Prefer deterministic decision_policy.py before LLM-driven selection.

### Done definition
- Code compiles.
- Unit tests pass.
- Execution trace records tool selection and tool calls.
- No cross-agent tool leakage.

### Do-not rules
- Do not introduce shared global tools.
- Do not connect real exchange APIs yet.
- Do not skip tests.
- Do not make one prompt decide everything without policy constraints.

## Extended governance

### Agent boundary contract
- Master agent can orchestrate but cannot bypass role boundaries.
- TA agent only outputs TA-focused report fields.
- Sentiment agent only outputs sentiment-focused report fields.
- Risk agent is the final approval gate for plan acceptance.
- No agent can mutate another agent's internal state directly.

### Tooling policy
- Keep tools deterministic for MVP: same input should produce same output.
- Every tool must validate input payload and return a serializable dict.
- Tool names must be unique within one agent toolset.
- Toolset registration must happen in the owning agent's toolset module.
- If a tool fails, return explicit error context or raise a typed exception.

### Orchestration policy
- Execution order for MVP: TA -> Sentiment -> Risk -> Final plan.
- Risk rejection must override directional signal and force HOLD.
- No silent fallbacks: orchestration must log skipped or failed stages.
- Keep orchestration side effects isolated from core decision logic.

### Decision policy rules
- decision_policy.py should contain explicit thresholds and branching logic.
- Avoid hidden heuristics spread across multiple files.
- If an LLM is introduced later, it must be constrained by policy outputs.
- Policy changes must include test updates in the same change set.

### Testing gates
- Add or update unit tests for every new tool and policy change.
- At least one workflow-level test must cover end-to-end happy path.
- Add failure-path tests for invalid payloads and rejection scenarios.
- No merge if tests are missing for newly added behavior.

### Trace and audit requirements
- Trace must include run_id, stage transitions, selected tools, and tool I/O.
- Tool calls should record agent name, tool name, input payload, and output.
- Audits should be sufficient to replay and debug one full run offline.
- Avoid storing secrets in trace payloads.

### Configuration and environment rules
- Use .env.example as the source of truth for required environment keys.
- Default settings should support local execution without external services.
- Keep configuration centralized in app/config/settings.py.

### API and external integration policy (MVP)
- External API clients stay as stubs or mocks in this stage.
- No real order placement, no live account connectivity.
- Market/news/risk services should expose stable interfaces first.

### Performance and reliability baseline
- Keep workflows synchronous and simple until behavior is stable.
- Fail fast on invalid inputs; do not continue with corrupted state.
- Prefer clear code paths over premature optimization.

### Documentation standards
- Update docs/architecture.md when boundaries or data flow change.
- Keep AGENTS.md aligned with actual code behavior.
- Document major policy thresholds in code comments or README.

### Change management checklist
Before merging a change:
- Confirm architecture constraints are still respected.
- Confirm no cross-agent imports of tool implementations.
- Confirm tests pass locally.
- Confirm execution trace remains complete.
- Confirm no real external trading connectivity was added.

## Practical implementation roadmap

### Phase 1: Executable MVP slice
- Implement base agent, base tool, tool registry, and execution trace.
- Implement TA, sentiment, and risk toolsets using deterministic mock tools.
- Implement master orchestrator and produce one final trade plan output.

### Phase 2: Hardening
- Expand unit test coverage and failure-path assertions.
- Standardize error types and response shapes.
- Improve trace schema consistency and audit readability.

### Phase 3: Controlled intelligence
- Introduce constrained LLM assistance only after deterministic baseline is stable.
- Keep policy as the non-negotiable guardrail around model outputs.

## Non-negotiable principle
- Safety and controllability are more important than feature speed.
- If there is a conflict, choose deterministic and testable behavior.
