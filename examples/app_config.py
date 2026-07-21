"""Example-bench app config (agent ports, frameworks, corpus profile).

Lives in tokenops-wiki — not part of the TokenOps core library. Governance seed
YAML is still loaded via ``tokenops.config.loader.load_governance_yaml``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import yaml

CorpusProfile = Literal["healthy", "leak"]
Framework = Literal["native", "langchain"]

EXAMPLES_ROOT = Path(__file__).resolve().parent
PRESETS_DIR = EXAMPLES_ROOT / "config" / "presets"
DEFAULT_CONFIG = EXAMPLES_ROOT / "config" / "default.yaml"


@dataclass
class AgentServerConfig:
    url: str = "http://localhost:8001"
    framework: Framework = "native"
    provider: str = "openai"
    model: str = "gpt-4o-mini"
    port: int = 8001
    max_steps: int = 20
    satisfaction_threshold: float = 0.7
    summarize_url: str = "http://localhost:8002"

    @classmethod
    def from_dict(cls, data: dict[str, Any], defaults: AgentServerConfig | None = None) -> AgentServerConfig:
        base = defaults or cls()
        return cls(
            url=str(data.get("url", base.url)),
            framework=data.get("framework", base.framework),
            provider=str(data.get("provider", base.provider)),
            model=str(data.get("model", base.model)),
            port=int(data.get("port", base.port)),
            max_steps=int(data.get("max_steps", base.max_steps)),
            satisfaction_threshold=float(
                data.get("satisfaction_threshold", base.satisfaction_threshold)
            ),
            summarize_url=str(data.get("summarize_url", base.summarize_url)),
        )


@dataclass
class SummarizeServerConfig:
    url: str = "http://localhost:8002"
    framework: Framework = "native"
    provider: str = "openai"
    model: str = "gpt-4o-mini"
    port: int = 8002

    @classmethod
    def from_dict(cls, data: dict[str, Any], defaults: SummarizeServerConfig | None = None) -> SummarizeServerConfig:
        base = defaults or cls()
        return SummarizeServerConfig(
            url=str(data.get("url", base.url)),
            framework=data.get("framework", base.framework),
            provider=str(data.get("provider", base.provider)),
            model=str(data.get("model", base.model)),
            port=int(data.get("port", base.port)),
        )


@dataclass
class PlannerServerConfig:
    url: str = "http://localhost:8011"
    provider: str = "openai"
    model: str = "gpt-4o-mini"
    port: int = 8011
    max_questions: int = 3
    researcher_url: str = "http://localhost:8012"
    writer_url: str = "http://localhost:8013"

    @classmethod
    def from_dict(cls, data: dict[str, Any], defaults: PlannerServerConfig | None = None) -> PlannerServerConfig:
        base = defaults or cls()
        return cls(
            url=str(data.get("url", base.url)),
            provider=str(data.get("provider", base.provider)),
            model=str(data.get("model", base.model)),
            port=int(data.get("port", base.port)),
            max_questions=int(data.get("max_questions", base.max_questions)),
            researcher_url=str(data.get("researcher_url", base.researcher_url)),
            writer_url=str(data.get("writer_url", base.writer_url)),
        )


@dataclass
class ResearcherServerConfig:
    url: str = "http://localhost:8012"
    provider: str = "openai"
    model: str = "gpt-4o-mini"
    port: int = 8012
    max_steps: int = 5
    satisfaction_threshold: float = 0.7

    @classmethod
    def from_dict(
        cls, data: dict[str, Any], defaults: ResearcherServerConfig | None = None
    ) -> ResearcherServerConfig:
        base = defaults or cls()
        return cls(
            url=str(data.get("url", base.url)),
            provider=str(data.get("provider", base.provider)),
            model=str(data.get("model", base.model)),
            port=int(data.get("port", base.port)),
            max_steps=int(data.get("max_steps", base.max_steps)),
            satisfaction_threshold=float(
                data.get("satisfaction_threshold", base.satisfaction_threshold)
            ),
        )


@dataclass
class WriterServerConfig:
    url: str = "http://localhost:8013"
    provider: str = "openai"
    model: str = "gpt-4o-mini"
    port: int = 8013

    @classmethod
    def from_dict(cls, data: dict[str, Any], defaults: WriterServerConfig | None = None) -> WriterServerConfig:
        base = defaults or cls()
        return cls(
            url=str(data.get("url", base.url)),
            provider=str(data.get("provider", base.provider)),
            model=str(data.get("model", base.model)),
            port=int(data.get("port", base.port)),
        )


@dataclass
class AppConfig:
    task: str = "Research enterprise SaaS pricing"
    corpus_profile: CorpusProfile = "healthy"
    research: AgentServerConfig = field(default_factory=AgentServerConfig)
    summarize: SummarizeServerConfig = field(default_factory=SummarizeServerConfig)
    planner: PlannerServerConfig = field(default_factory=PlannerServerConfig)
    researcher: ResearcherServerConfig = field(default_factory=ResearcherServerConfig)
    writer: WriterServerConfig = field(default_factory=WriterServerConfig)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AppConfig:
        agents = data.get("agents", {})
        return cls(
            task=str(data.get("task", "Research enterprise SaaS pricing")),
            corpus_profile=data.get("corpus_profile", "healthy"),
            research=AgentServerConfig.from_dict(agents.get("research", {})),
            summarize=SummarizeServerConfig.from_dict(agents.get("summarize", {})),
            planner=PlannerServerConfig.from_dict(agents.get("planner", {})),
            researcher=ResearcherServerConfig.from_dict(agents.get("researcher", {})),
            writer=WriterServerConfig.from_dict(agents.get("writer", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "task": self.task,
            "corpus_profile": self.corpus_profile,
            "agents": {
                "research": {
                    "url": self.research.url,
                    "summarize_url": self.research.summarize_url,
                    "framework": self.research.framework,
                    "provider": self.research.provider,
                    "model": self.research.model,
                    "port": self.research.port,
                    "max_steps": self.research.max_steps,
                    "satisfaction_threshold": self.research.satisfaction_threshold,
                },
                "summarize": {
                    "url": self.summarize.url,
                    "framework": self.summarize.framework,
                    "provider": self.summarize.provider,
                    "model": self.summarize.model,
                    "port": self.summarize.port,
                },
                "planner": {
                    "url": self.planner.url,
                    "provider": self.planner.provider,
                    "model": self.planner.model,
                    "port": self.planner.port,
                    "max_questions": self.planner.max_questions,
                    "researcher_url": self.planner.researcher_url,
                    "writer_url": self.planner.writer_url,
                },
                "researcher": {
                    "url": self.researcher.url,
                    "provider": self.researcher.provider,
                    "model": self.researcher.model,
                    "port": self.researcher.port,
                    "max_steps": self.researcher.max_steps,
                    "satisfaction_threshold": self.researcher.satisfaction_threshold,
                },
                "writer": {
                    "url": self.writer.url,
                    "provider": self.writer.provider,
                    "model": self.writer.model,
                    "port": self.writer.port,
                },
            },
        }


def _default_path() -> Path:
    env = os.environ.get("TOKENOPS_CONFIG")
    if env:
        return Path(env)
    return DEFAULT_CONFIG


def load_config(path: Path | str | None = None) -> AppConfig:
    config_path = Path(path) if path else _default_path()
    if not config_path.exists():
        return AppConfig()
    data = yaml.safe_load(config_path.read_text()) or {}
    return AppConfig.from_dict(data)


def save_config(cfg: AppConfig, path: Path | str) -> None:
    Path(path).write_text(yaml.safe_dump(cfg.to_dict(), sort_keys=False))


def list_presets() -> list[Path]:
    if not PRESETS_DIR.exists():
        return []
    return sorted(PRESETS_DIR.glob("*.yaml"))
