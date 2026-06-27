# Policies & actions

TokenOps policies are **(detect, fix)** pairs. A detector reads the ledger and emits a signal; the policy maps that signal to an **action**. Detectors never mutate state — that keeps enforcement testable and deterministic.

## Enforcement moments

| Moment | When it runs |
|---|---|
| **pre_call** | Before dispatching an LLM call |
| **observe** | After each boundary crossing completes |
| **tick** | On a timer (optional; e.g. hang detection) |

## Action types

| Action | What it does | Typical use |
|---|---|---|
| **ALLOW** | Proceed unchanged | Default when no signal |
| **MUTATE** | Change the next call (output cap, model, prompt shape) | Prevention, steering |
| **INJECT** | Insert a message or substitute payload | Corrections, offloads, budget nudges |
| **REJECT** | Refuse with retry hint (HTTP 429 style) | Distributed backpressure |
| **QUEUE** | Hold until capacity frees | Single-process backpressure |
| **RETRY** | Re-run with stricter generation settings | Output runaway recovery |
| **CANCEL** | Stop an in-flight stream | Stop token bleed mid-generation |
| **HALT** | End the run; refuse all later calls | Spend backstop, stuck loops |

**HALT is sticky** — once set, every subsequent crossing for that `run_id` is refused until an operator explicitly resumes (if your deployment supports resume).

---

## Currently supported policies

Default demo configuration includes all ten policies below plus one run budget (`run_llm_cap`, $2.00 per run in the seed config).

### Spend & budgets

| Policy | Moment | Detects (summary) | Action |
|---|---|---|---|
| **cost_budget** | observe | Run (or segment) spend ≥ budget limit | **HALT** |
| **pre_call_worst_case** | pre_call | Next call's worst-case cost would exceed remaining budget | **MUTATE** (cap output) or **HALT** |
| **cost_guard** | observe | Spend crosses ~80% of budget (once per run) | **INJECT** ("keep minimal") or **MUTATE** (cheaper model) |

**How they work together:** `pre_call_worst_case` tries to prevent a breach before the call. `cost_guard` steers the run cheaper as spend rises. `cost_budget` is the guarantee — if spend still crosses the limit, the run halts.

### Loops & progress

| Policy | Moment | Detects (summary) | Action |
|---|---|---|---|
| **step_cap** | observe | Number of boundary crossings ≥ configured max | **HALT** |
| **progress_guard** | observe | Same tool action + same result repeating, or degenerate model output | **INJECT** correction, then **HALT** after repeated failures |
| **output_runaway** | observe (stream) | Repetitive or degenerate generated text | **CANCEL** → **RETRY** (bounded) → **INJECT** error; never HALT |
| **tool_fix** | observe | Unknown tool name or invalid arguments | **INJECT** synthetic error; **HALT** after repeated identical failures |

### Context & payload size

| Policy | Moment | Detects (summary) | Action |
|---|---|---|---|
| **context_compaction** | pre_call | Assembled input approaching context ceiling | **MUTATE** prompt (dedup, pin critical sections); telemetry-only if no hook |
| **tool_output_cap** | observe | Tool return payload estimated too large for context | **INJECT** descriptor + handle; full payload stored for paginated access |

### Infrastructure

| Policy | Moment | Detects (summary) | Action |
|---|---|---|---|
| **concurrency_cap** | pre_call | In-flight calls for segment ≥ max concurrent | **QUEUE** (single process) or **REJECT** (distributed) |

`concurrency_cap` protects memory and downstream rate limits. It does not reduce token spend on calls already in flight.

---

## Default parameters (demo seed)

These are starting points in the reference bench — operators tune them per workflow:

| Policy | Key parameters |
|---|---|
| `cost_budget` | Linked to budget `run_llm_cap` |
| `pre_call_worst_case` | Linked to `run_llm_cap`; default max output 1024 tokens |
| `step_cap` | `max_steps`: 20 (demo halt screenshot uses 3) |
| `concurrency_cap` | `max_concurrent`: 4; mode `reject` |
| `tool_fix` | Tool registry (e.g. `search`); max identical failures before halt |
| `tool_output_cap` | `cap_tokens`: 8000 |
| `progress_guard` | Sliding window, repeat threshold, max corrections before halt |
| `cost_guard` | Linked to `run_llm_cap`; threshold 0.8; mode `minimize` |
| `context_compaction` | `ctx_max`: 100000; requires prompt hook for full effect |
| `output_runaway` | Repeat threshold; bounded retries before inject |

Exact detector tuning (similarity thresholds, token estimators, etc.) may change between releases.

---

## Budgets

| Field | Meaning |
|---|---|
| **id** | Stable name referenced by policies |
| **limit** | Cap in currency (demo uses micro-dollars internally) |
| **dimension** | What the cap scopes to — `run`, `user`, tag key, etc. |

An unlimited budget (`limit` omitted) still accumulates spend for measurement but never trips `cost_budget`.

---

## What is not in the default demo

The following are on the roadmap or require additional configuration:

- **Composite segment DSL** — multi-dimensional budget scoping beyond single keys
- **CANCEL / RETRY** as first-class operator actions outside `output_runaway`
- **Tick-based hang detection** in `progress_guard` (detector stub; wiring optional)

---

## Policy design rules (public)

1. **Deterministic detectors** — no LLM in the enforcement path  
2. **Single ledger** — detection and accounting share one source of truth  
3. **Fail closed** — missing price or registration → refuse  
4. **Act in-path** — policies change behavior, not just metrics  
5. **Layered defense** — steer (`cost_guard`, `context_compaction`) before stop (`cost_budget`, `step_cap`)

---

[Back to overview](../README.md) · [Principles](./principles.md) · [Demo bench](./demo-bench.md)
