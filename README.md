# TokenOps

**Run-aware token governance for AI agents.**

TokenOps is a control plane that sits alongside your agent (data plane). It measures spend as it accrues, attributes it to the right run and customer context, and enforces deterministic policies — before and after each model, tool, and delegation call.

---

## The problem in one sentence

A **request** is one model call; a **run** is the whole task — many calls, tools, and sub-agents. Gateways see requests one at a time. TokenOps governs the **run**: loops, growing context, fan-out, and runaway cost.

## Architecture at a glance

```
  data plane (your agent)          control plane (TokenOps)
  ─────────────────────          ──────────────────────────
  model / tool / delegate   →    measure + attribute + enforce
                                 budgets · policies · ledger
```

![Control plane vs data plane](./assets/tokenops-planes.png)

| Layer | Sees | Can govern |
|---|---|---|
| API gateway / proxy | Independent requests | Per-request rate, routing, coarse caps |
| **TokenOps** | Full **run**: step sequence, context, delegation | Loops, stalls, context decay, fan-out, per-run and per-customer spend |

Policies live **outside** the agent so the agent cannot rewrite or bypass them. Checks sit **in the call path** so spend is stopped before it lands. That combination — out-of-band rules, in-path enforcement — is what makes a budget a guarantee rather than an alert.

## How TokenOps compares

<table>
<thead>
<tr>
<th align="left">Capability</th>
<th align="left">Example</th>
<th align="left">TokenOps</th>
<th align="left"><img src="./assets/logos/litellm.png" height="20" alt="" /> LiteLLM</th>
<th align="left"><img src="./assets/logos/portkey.png" height="20" alt="" /> Portkey</th>
<th align="left"><img src="./assets/logos/cloudflare.svg" height="20" alt="" /> Cloudflare AI Gateway</th>
<th align="left"><img src="./assets/logos/langfuse.svg" height="20" alt="" /> Langfuse</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Primary Focus</strong></td>
<td>What is fundamentally being governed?</td>
<td>Run (stateful)</td>
<td>Request</td>
<td>Request</td>
<td>Request</td>
<td>Request (trace)</td>
</tr>
<tr>
<td><strong>Execution Scope</strong></td>
<td>Research Agent → Summarizer Agent → Reviewer</td>
<td>Full multi-agent workflow</td>
<td>Single request</td>
<td>Single request</td>
<td>Single request</td>
<td>Trace spans (observed)</td>
</tr>
<tr>
<td><strong>Cost Measurement</strong></td>
<td>Total spend across an entire workflow</td>
<td>Cumulative &amp; tunable</td>
<td>Per-request</td>
<td>Per-request</td>
<td>Per-request</td>
<td>Per-trace</td>
</tr>
<tr>
<td><strong>Budget Enforcement</strong></td>
<td>"$0.50 per run" or "$5 per customer/day"</td>
<td>Yes (run-aware context)</td>
<td>Yes (team/key)</td>
<td>Yes (virtual key)</td>
<td>Yes (identity)</td>
<td>No (analytics only)</td>
</tr>
<tr>
<td><strong>Steering Capability</strong></td>
<td>Swap model, shorten output, inject guidance</td>
<td>Full (mutate/inject)</td>
<td>Minimal (routing)</td>
<td>Low (fallbacks)</td>
<td>Low (routing)</td>
<td>None</td>
</tr>
<tr>
<td><strong>Enforcement Point</strong></td>
<td>Before the next model/tool call executes</td>
<td>In-path (deterministic)</td>
<td>In-path (gateway)</td>
<td>In-path (gateway)</td>
<td>In-path (gateway)</td>
<td>Out-of-band</td>
</tr>
<tr>
<td><strong>Fail-Closed Integrity</strong></td>
<td>Missing registration or exceeded budget</td>
<td>Upcoming (optional)</td>
<td>Optional</td>
<td>Limited</td>
<td>No</td>
<td>No</td>
</tr>
</tbody>
</table>

Expanded notes on each row → [Comparison guide](./docs/comparison.md)

---

## Feature set

### Platform capabilities

| Capability | What it does |
|---|---|
| **Run registration** | Bind a `run_id` to intent and customer tags before any telemetry |
| **Attribution** | Every crossing carries run, agent, span, and tag dimensions for the ledger |
| **Boundary instrumentation** | Govern LLM calls, tool calls, and agent delegations |
| **Enforcement moments** | `pre_call` (before dispatch), `observe` (after each step), `tick` (optional timer) |
| **Budgets** | Spend accumulators with optional caps scoped to run, user, or tag |
| **Deterministic policies** | Detector reads ledger → policy emits action; no LLM in the enforcement path |
| **Multi-agent rollup** | Same `run_id` across agents; child spend rolls into the parent total |
| **Sticky halt** | Once halted, every later crossing for that run is refused |
| **Fail closed** | Missing registration or price → refuse (upcoming, optional) |
| **Run history** | Completed, halted, and throttled runs with cost, steps, and halt reasons |
| **Operator UI** | Policy admin, dashboard, live simulator with trace and control-plane views |

### Supported policies (10)

| Policy | Category | What it governs |
|---|---|---|
| [`cost_budget`](./docs/policies-and-actions.md#spend--budgets) | Spend | Hard stop when run or segment spend crosses a budget limit |
| [`pre_call_worst_case`](./docs/policies-and-actions.md#spend--budgets) | Spend | Cap or block the next call if its worst-case cost exceeds remaining budget |
| [`cost_guard`](./docs/policies-and-actions.md#spend--budgets) | Spend | Steer output shorter or swap to a cheaper model as spend approaches the limit |
| [`step_cap`](./docs/policies-and-actions.md#loops--progress) | Loops | Circuit breaker on the number of boundary crossings per run |
| [`progress_guard`](./docs/policies-and-actions.md#loops--progress) | Loops | Detect stuck runs (repeated actions or degenerate output); inject correction, then halt |
| [`output_runaway`](./docs/policies-and-actions.md#loops--progress) | Loops | Cancel degenerate streams, retry with stricter settings, inject error if still broken |
| [`tool_fix`](./docs/policies-and-actions.md#loops--progress) | Loops | Catch invalid tool calls before I/O; inject synthetic error, halt after repeated failures |
| [`context_compaction`](./docs/policies-and-actions.md#context--payload-size) | Context | Shrink the outgoing prompt as input approaches the context ceiling |
| [`tool_output_cap`](./docs/policies-and-actions.md#context--payload-size) | Context | Offload oversized tool payloads; substitute a paginated handle |
| [`concurrency_cap`](./docs/policies-and-actions.md#infrastructure) | Infrastructure | Limit in-flight calls per segment; queue or reject when at capacity |

Full policy tables, default parameters, and how policies compose → [Policies & actions](./docs/policies-and-actions.md)

### Supported actions (8)

| Action | Effect |
|---|---|
| **ALLOW** | Proceed unchanged |
| **MUTATE** | Rewrite the outgoing call — output cap, model, or prompt |
| **INJECT** | Add a message or substitute a tool result in the conversation |
| **REJECT** | Refuse with retry hint (429-style backpressure) |
| **QUEUE** | Hold until capacity frees (single-process backpressure) |
| **RETRY** | Re-issue with stricter generation settings |
| **CANCEL** | Stop an in-flight stream mid-generation |
| **HALT** | End the run; refuse all subsequent crossings |

---

## Guide

### [Principles](./docs/principles.md)

How TokenOps thinks about token spend — the rules that hold regardless of model or framework.

- Govern the **run**, not the individual request
- **Measure, attribute, bound** on every crossing
- Enforce **during** the run, not from a static pre-run estimate
- **Control plane** separate from data plane; agent never owns the budget check
- Fail-closed mode (upcoming, optional); **act** (halt, steer, inject), don't just alert
- Budgets accumulate spend; policies decide what to do when signals trip

→ [Read principles](./docs/principles.md)

### [How TokenOps compares](./docs/comparison.md)

Side-by-side with LiteLLM, Portkey, Cloudflare AI Gateway, and Langfuse — scoped to run vs request, budget enforcement, steering, and fail-closed behavior.

→ [Read comparison](./docs/comparison.md)

### [Workflow](./docs/workflow.md)

What happens on each agent run, from registration through completion or halt.

- Register `run_id` with intent and tags → start task → load governance config
- Every LLM, tool, and delegate crossing runs `pre_call` then `observe`
- Multi-agent pipelines share one run; child cost rolls up to the parent
- Outcomes: **completed**, **halted** (sticky), or **throttled** (backpressure)
- Operator changes in policy admin apply on the next run

→ [Read workflow](./docs/workflow.md)

### [Demo bench walkthrough](./docs/demo-bench.md)

Screenshots from the reference **research → summarize** two-agent bench.

- **Test Bench** — live pipeline over HTTP
- **Run simulator** — in-process demo with live timeline, trace, and control-plane tabs
- **Policy admin** — edit budgets and policy instances
- **Dashboard** — run history, cost, and problematic runs

Includes a step-cap halt example and control-plane signal view.

→ [See screenshots](./docs/demo-bench.md)

### [Policies & actions](./docs/policies-and-actions.md)

Deep dive on the (detect, fix) model, enforcement moments, full policy tables, budget schema, and design rules.

→ [Read policies & actions](./docs/policies-and-actions.md)

### [Contact & onboarding](./docs/contact.md)

We help teams wire TokenOps into agent pipelines — registration, boundary hooks, budget design, and policy tuning.

Open a [GitHub Issue](https://github.com/theagentplane/tokenops-wiki/issues) or email [tishachawla5@gmail.com](mailto:tishachawla5@gmail.com) / [susheemkoul97@gmail.com](mailto:susheemkoul97@gmail.com) with your agent architecture, priority failure modes, and whether you need instrumentation or governance config help.

→ [Get in touch](./docs/contact.md)

---

*TokenOps is developed by [Agent Plane](https://github.com/theagentplane).*
