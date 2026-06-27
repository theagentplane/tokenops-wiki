# Contact & onboarding

## Get in touch

We help teams wire TokenOps into agent pipelines — registration, boundary instrumentation, budget design, and policy tuning for your workflows.

| Channel | Use for |
|---|---|
| **[GitHub Issues on this wiki](https://github.com/theagentplane/tokenops-wiki/issues)** | Onboarding questions, documentation feedback, general inquiries |
| **[Agent Plane on GitHub](https://github.com/theagentplane)** | Organization profile and related projects |

Open an issue with:

- A short description of your agent architecture (single vs multi-agent, frameworks)
- Which failure modes you care about most (runaway spend, stuck loops, context growth, fan-out)
- Whether you need help with instrumentation, governance config, or both

We respond to onboarding inquiries through GitHub Issues. If you prefer a private channel, say so in the issue and we will follow up.

## What onboarding typically covers

1. **Run registration** — stable `run_id`, intent, and customer tags before any telemetry  
2. **Boundary hooks** — LLM, tool, and delegate crossings instrumented for `pre_call` and `observe`  
3. **Budget design** — per-run caps, per-tenant rollups, and which policies link to which buckets  
4. **Policy selection** — which of the ten default policies to enable, and parameters for your task shapes  
5. **Operator visibility** — run history, halt reasons, and control-plane signals for your team  

---

[Back to overview](../README.md)
