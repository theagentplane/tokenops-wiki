# TokenOps examples

Runnable A2A test benches and demos for [TokenOps](https://github.com/theagentplane/tokenops).
The core library (SDK, control plane, Admin/Dashboard) lives in that repo; this package is what you run to try it.

| Stack | Agents | Make target |
|-------|--------|-------------|
| Two-agent | Research → Summarize | `make two-agent` / `make run` |
| Triad | Planner → Researcher → Writer | `make triad` / `make run-triad` |
| Bench UI | Chat + Simulator | `make bench-ui` |

## Setup

From this repo root (expects a sibling `../tokenops` checkout while developing):

```bash
make install
cp ../tokenops/.env.example .env   # optional API keys
TOKENOPS_CONFIG=examples/config/default.yaml make db-reset
make run          # plane :7700 + agents + Admin UI
# or
make triad        # plane + planner/researcher/writer + Admin UI
make bench-ui     # Chat + Simulator only
```

Docker (two-agent):

```bash
docker compose -f docker-compose.examples.yml up --build
```

Triad overlay:

```bash
docker compose -f docker-compose.examples.yml -f docker-compose.triad.yml up --build \
  tokenops planner researcher writer
```

## Layout

```
examples/
  a2a/          # shared HTTP helpers
  agents/       # research + summarize
  triad/        # planner + researcher + writer
  servers/      # python -m entrypoints
  ui/           # Chat + Simulator
  config/       # demo governance YAML seeds
benchmarking/   # MetaGPT / browseruse / trials harness
```

Field guide: [`docs/field-guide-add-tokenops.md`](../docs/field-guide-add-tokenops.md).
Demo screenshots: [`docs/demo-bench.md`](../docs/demo-bench.md).
