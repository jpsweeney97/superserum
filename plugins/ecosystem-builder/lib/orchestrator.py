"""Single-threaded orchestrator for ecosystem-builder runs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from lib.logging import EventLogger
from lib.staging import StagingManager
from lib.state import RunManifest


class Orchestrator:
    """Orchestrates a single ecosystem-builder run."""

    def __init__(
        self,
        manifest: RunManifest,
        staging_dir: Path | None = None,
    ) -> None:
        self.manifest = manifest
        self.logger = EventLogger(manifest.run_dir / "log.jsonl")
        self.staging = StagingManager(staging_dir=staging_dir)
        self.build_queue: list[dict[str, Any]] = []

    def run(self) -> None:
        """Execute the main control loop."""
        self.logger.log("run_started", {
            "run_id": self.manifest.run_id,
            "budget": {
                "artifacts": self.manifest.budget.artifacts.limit,
                "hours": self.manifest.budget.hours.limit,
            },
        })

        try:
            # Phase 1: Analyze
            gaps = self._analyze()
            self.manifest.progress.analyzed = len(gaps)
            self.manifest.save()

            self.logger.log("gap_analyzed", {"count": len(gaps)})

            # Phase 2: Propose (populate build queue)
            self.build_queue = self._prioritize(gaps)

            # Phase 3-5: Build -> Validate -> Stage loop
            while self.build_queue and not self.manifest.budget.any_exhausted:
                gap = self.build_queue.pop(0)

                # Build
                artifact = self._build(gap)
                if artifact is None:
                    continue

                self.manifest.progress.built += 1
                self.logger.log("artifact_built", {
                    "name": artifact["name"],
                    "gap_id": gap.get("gap_id"),
                })

                # Validate
                passed = self._validate(artifact)

                if passed:
                    # Stage
                    self.staging.stage_skill(
                        name=artifact["name"],
                        content=artifact["content"],
                        run_id=self.manifest.run_id,
                        gap_id=gap.get("gap_id", "unknown"),
                    )
                    self.manifest.progress.passed += 1
                    self.logger.log("artifact_staged", {"name": artifact["name"]})
                else:
                    self.manifest.progress.failed += 1
                    self.logger.log("artifact_rejected", {"name": artifact["name"]})

                # Update budget
                self.manifest.budget.artifacts.used += 1
                self.manifest.save()

            # Complete
            self.manifest.status = "complete"
            if self.manifest.budget.any_exhausted:
                self.manifest.completion_reason = "budget_exhausted"
            else:
                self.manifest.completion_reason = "queue_empty"

        except Exception as e:
            self.manifest.status = "failed"
            self.manifest.completion_reason = str(e)
            self.logger.log("run_failed", {"error": str(e)})
            raise

        finally:
            self.manifest.save()
            self.logger.log("run_complete", {
                "status": self.manifest.status,
                "reason": self.manifest.completion_reason,
                "progress": {
                    "analyzed": self.manifest.progress.analyzed,
                    "built": self.manifest.progress.built,
                    "passed": self.manifest.progress.passed,
                    "failed": self.manifest.progress.failed,
                },
            })

    def _analyze(self) -> list[dict[str, Any]]:
        """Analyze ecosystem for gaps. Override in subclass or mock."""
        # Placeholder - Phase 2 will implement multi-agent analysis
        return []

    def _prioritize(self, gaps: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Prioritize gaps for building. Override in subclass or mock."""
        # Placeholder - just return as-is for now
        return gaps

    def _build(self, gap: dict[str, Any]) -> dict[str, Any] | None:
        """Build an artifact for a gap. Override in subclass or mock."""
        # Placeholder - Phase 2 will invoke SkillForge
        return None

    def _validate(self, artifact: dict[str, Any]) -> bool:
        """Validate an artifact. Override in subclass or mock."""
        # Placeholder - Phase 2 will implement validation panel
        return True
