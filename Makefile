.PHONY: install research-server summarize-server planner-server researcher-server writer-server \
	control-plane bench-ui two-agent triad run run-triad stop stop-triad db-clear db-reseed db-reset

PYTHON ?= python3
export PYTHONPATH := .$(if $(PYTHONPATH),:$(PYTHONPATH),)
export TOKENOPS_CONFIG ?= examples/config/default.yaml

# Prefer a sibling checkout of tokenops; falls back to git dep via pyproject when absent.
install:
	$(PYTHON) -m pip install --upgrade pip setuptools wheel
	@if [ -d ../tokenops ]; then \
		$(PYTHON) -m pip install -e ../tokenops; \
	else \
		$(PYTHON) -m pip install "tokenops @ git+https://github.com/theagentplane/tokenops.git"; \
	fi
	$(PYTHON) -m pip install -e ".[langchain,dev]"

control-plane:
	$(PYTHON) -m tokenops.server

research-server:
	$(PYTHON) -m examples.servers.research

summarize-server:
	$(PYTHON) -m examples.servers.summarize

planner-server:
	TOKENOPS_CONFIG=$${TOKENOPS_CONFIG:-examples/config/triad.yaml} $(PYTHON) -m examples.servers.planner

researcher-server:
	TOKENOPS_CONFIG=$${TOKENOPS_CONFIG:-examples/config/triad.yaml} $(PYTHON) -m examples.servers.researcher

writer-server:
	TOKENOPS_CONFIG=$${TOKENOPS_CONFIG:-examples/config/triad.yaml} $(PYTHON) -m examples.servers.writer

# Chat + Simulator demos (examples UI).
bench-ui:
	streamlit run examples/ui/app.py --server.port 8501

two-agent: run

run: stop
	$(PYTHON) run.py

triad: run-triad

run-triad: stop-triad
	$(PYTHON) run_triad.py

stop:
	@for port in 7700 8001 8002 8501; do \
		pids=$$(lsof -tiTCP:$$port -sTCP:LISTEN 2>/dev/null); \
		if [ -n "$$pids" ]; then \
			echo "Stopping listener on port $$port ($$pids)"; \
			kill $$pids 2>/dev/null || true; \
			sleep 0.5; \
			pids=$$(lsof -tiTCP:$$port -sTCP:LISTEN 2>/dev/null); \
			if [ -n "$$pids" ]; then kill -9 $$pids 2>/dev/null || true; fi; \
		fi; \
	done

stop-triad:
	@for port in 7700 8011 8012 8013 8501; do \
		pids=$$(lsof -tiTCP:$$port -sTCP:LISTEN 2>/dev/null); \
		if [ -n "$$pids" ]; then \
			echo "Stopping listener on port $$port ($$pids)"; \
			kill $$pids 2>/dev/null || true; \
			sleep 0.5; \
			pids=$$(lsof -tiTCP:$$port -sTCP:LISTEN 2>/dev/null); \
			if [ -n "$$pids" ]; then kill -9 $$pids 2>/dev/null || true; fi; \
		fi; \
	done

db-clear:
	$(PYTHON) scripts/db_clear.py

db-reseed:
	$(PYTHON) scripts/db_reseed.py

db-reset: db-clear db-reseed
