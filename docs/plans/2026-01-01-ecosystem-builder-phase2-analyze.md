# Ecosystem Builder Phase 2: Multi-Agent Gap Analysis

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement `_analyze()` method with a multi-agent panel that catalogs the ecosystem (user skills + plugin ecosystem) and identifies gaps through specialized agent perspectives.

**Architecture:** Three specialized agents run in parallel—Catalog Agent (inventories existing artifacts), Workflow Analyzer (identifies workflow holes), and Quality Scorer (flags improvement opportunities). Results merge into a deduplicated, prioritized gap list stored in `opportunities.json`.

**Tech Stack:** Python 3.12, pytest, dataclasses, Task tool subagents (claude-code agents dispatched via subprocess)

---

## Task 1: Define Gap Data Model

**Files:**
- Modify: `plugins/ecosystem-builder/lib/state.py`
- Test: `plugins/ecosystem-builder/tests/test_state.py`

**Step 1: Write the failing test**

```python
# Add to test_state.py

from lib.state import Gap, GapType


class TestGap:
    """Tests for Gap dataclass."""

    def test_gap_creation(self) -> None:
        """Gap should store all required fields."""
        gap = Gap(
            gap_id="gap-001",
            gap_type=GapType.MISSING_SKILL,
            title="TDD workflow for Go projects",
            description="No skill exists for Go-specific TDD workflow",
            source_agent="workflow-analyzer",
            confidence=0.8,
            priority=1,
        )
        assert gap.gap_id == "gap-001"
        assert gap.gap_type == GapType.MISSING_SKILL
        assert gap.confidence == 0.8

    def test_gap_to_dict(self) -> None:
        """Gap should serialize to dict."""
        gap = Gap(
            gap_id="gap-002",
            gap_type=GapType.INCOMPLETE_ARTIFACT,
            title="Missing tests for handoff skill",
            description="handoff skill has no test coverage",
            source_agent="quality-scorer",
            confidence=0.9,
            priority=2,
        )
        data = gap.to_dict()
        assert data["gap_id"] == "gap-002"
        assert data["gap_type"] == "incomplete_artifact"
        assert data["source_agent"] == "quality-scorer"

    def test_gap_from_dict(self) -> None:
        """Gap should deserialize from dict."""
        data = {
            "gap_id": "gap-003",
            "gap_type": "workflow_hole",
            "title": "No pre-commit validation",
            "description": "Common workflow has no hook",
            "source_agent": "workflow-analyzer",
            "confidence": 0.7,
            "priority": 3,
        }
        gap = Gap.from_dict(data)
        assert gap.gap_type == GapType.WORKFLOW_HOLE
        assert gap.title == "No pre-commit validation"
```

**Step 2: Run test to verify it fails**

Run: `cd plugins/ecosystem-builder && python -m pytest tests/test_state.py::TestGap -v`
Expected: FAIL with "cannot import name 'Gap'"

**Step 3: Write minimal implementation**

Add to `lib/state.py` after the imports:

```python
from enum import Enum


class GapType(Enum):
    """Types of ecosystem gaps."""

    MISSING_SKILL = "missing_skill"
    INCOMPLETE_ARTIFACT = "incomplete_artifact"
    WORKFLOW_HOLE = "workflow_hole"
    QUALITY_ISSUE = "quality_issue"


@dataclass
class Gap:
    """A detected gap in the ecosystem."""

    gap_id: str
    gap_type: GapType
    title: str
    description: str
    source_agent: str
    confidence: float  # 0.0 to 1.0
    priority: int  # 1 = highest

    def to_dict(self) -> dict:
        """Serialize to dict for JSON storage."""
        return {
            "gap_id": self.gap_id,
            "gap_type": self.gap_type.value,
            "title": self.title,
            "description": self.description,
            "source_agent": self.source_agent,
            "confidence": self.confidence,
            "priority": self.priority,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Gap":
        """Deserialize from dict."""
        return cls(
            gap_id=data["gap_id"],
            gap_type=GapType(data["gap_type"]),
            title=data["title"],
            description=data["description"],
            source_agent=data["source_agent"],
            confidence=data["confidence"],
            priority=data["priority"],
        )
```

**Step 4: Run test to verify it passes**

Run: `cd plugins/ecosystem-builder && python -m pytest tests/test_state.py::TestGap -v`
Expected: PASS

**Step 5: Commit**

```bash
git add plugins/ecosystem-builder/lib/state.py plugins/ecosystem-builder/tests/test_state.py
git commit -m "feat(ecosystem-builder): add Gap dataclass with GapType enum"
```

---

## Task 2: Define Agent Panel Interface

**Files:**
- Create: `plugins/ecosystem-builder/lib/agents.py`
- Test: `plugins/ecosystem-builder/tests/test_agents.py`

**Step 1: Create test file with first test**

```python
# tests/test_agents.py
"""Tests for agent panel."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from lib.agents import AgentPanel, AgentResult
from lib.state import Gap, GapType


class TestAgentResult:
    """Tests for AgentResult."""

    def test_agent_result_creation(self) -> None:
        """AgentResult should store gaps and metadata."""
        gaps = [
            Gap(
                gap_id="gap-001",
                gap_type=GapType.MISSING_SKILL,
                title="Test gap",
                description="Description",
                source_agent="catalog",
                confidence=0.8,
                priority=1,
            )
        ]
        result = AgentResult(
            agent_name="catalog",
            gaps=gaps,
            artifacts_scanned=15,
            error=None,
        )
        assert result.agent_name == "catalog"
        assert len(result.gaps) == 1
        assert result.artifacts_scanned == 15
        assert result.success is True

    def test_agent_result_with_error(self) -> None:
        """AgentResult should track errors."""
        result = AgentResult(
            agent_name="catalog",
            gaps=[],
            artifacts_scanned=0,
            error="Failed to scan skills directory",
        )
        assert result.success is False
        assert result.error == "Failed to scan skills directory"
```

**Step 2: Run test to verify it fails**

Run: `cd plugins/ecosystem-builder && python -m pytest tests/test_agents.py::TestAgentResult -v`
Expected: FAIL with "No module named 'lib.agents'"

**Step 3: Write minimal implementation**

Create `lib/agents.py`:

```python
"""Multi-agent panel for ecosystem gap analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from lib.state import Gap


@dataclass
class AgentResult:
    """Result from a single agent's analysis."""

    agent_name: str
    gaps: list[Gap]
    artifacts_scanned: int
    error: str | None = None

    @property
    def success(self) -> bool:
        """True if agent completed without error."""
        return self.error is None
```

**Step 4: Run test to verify it passes**

Run: `cd plugins/ecosystem-builder && python -m pytest tests/test_agents.py::TestAgentResult -v`
Expected: PASS

**Step 5: Commit**

```bash
git add plugins/ecosystem-builder/lib/agents.py plugins/ecosystem-builder/tests/test_agents.py
git commit -m "feat(ecosystem-builder): add AgentResult dataclass"
```

---

## Task 3: Implement AgentPanel Class

**Files:**
- Modify: `plugins/ecosystem-builder/lib/agents.py`
- Modify: `plugins/ecosystem-builder/tests/test_agents.py`

**Step 1: Write the failing test**

Add to `tests/test_agents.py`:

```python
class TestAgentPanel:
    """Tests for AgentPanel."""

    def test_panel_initialization(self, tmp_path: Path) -> None:
        """AgentPanel should initialize with ecosystem paths."""
        panel = AgentPanel(
            user_skills_dir=tmp_path / "skills",
            plugins_dir=tmp_path / "plugins",
        )
        assert panel.user_skills_dir == tmp_path / "skills"
        assert panel.plugins_dir == tmp_path / "plugins"

    def test_panel_run_all_agents_returns_results(self, tmp_path: Path) -> None:
        """run_all_agents should return results from all agents."""
        # Setup minimal skill structure
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        skill_dir = skills_dir / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: test-skill\n---\n# Test")

        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()

        panel = AgentPanel(
            user_skills_dir=skills_dir,
            plugins_dir=plugins_dir,
        )
        results = panel.run_all_agents()

        assert len(results) == 3  # catalog, workflow, quality
        agent_names = {r.agent_name for r in results}
        assert agent_names == {"catalog", "workflow-analyzer", "quality-scorer"}

    def test_panel_merge_gaps_deduplicates(self, tmp_path: Path) -> None:
        """merge_gaps should deduplicate by gap_id."""
        panel = AgentPanel(
            user_skills_dir=tmp_path / "skills",
            plugins_dir=tmp_path / "plugins",
        )

        gap1 = Gap(
            gap_id="gap-001",
            gap_type=GapType.MISSING_SKILL,
            title="Missing skill A",
            description="Desc",
            source_agent="catalog",
            confidence=0.8,
            priority=1,
        )
        gap2 = Gap(
            gap_id="gap-001",  # duplicate
            gap_type=GapType.MISSING_SKILL,
            title="Missing skill A",
            description="Desc",
            source_agent="workflow-analyzer",
            confidence=0.9,
            priority=2,
        )
        gap3 = Gap(
            gap_id="gap-002",
            gap_type=GapType.QUALITY_ISSUE,
            title="Quality issue B",
            description="Desc",
            source_agent="quality-scorer",
            confidence=0.7,
            priority=3,
        )

        results = [
            AgentResult(agent_name="catalog", gaps=[gap1], artifacts_scanned=5),
            AgentResult(agent_name="workflow-analyzer", gaps=[gap2], artifacts_scanned=3),
            AgentResult(agent_name="quality-scorer", gaps=[gap3], artifacts_scanned=5),
        ]

        merged = panel.merge_gaps(results)

        assert len(merged) == 2
        # Higher confidence version should be kept
        gap_001 = next(g for g in merged if g.gap_id == "gap-001")
        assert gap_001.confidence == 0.9
```

**Step 2: Run test to verify it fails**

Run: `cd plugins/ecosystem-builder && python -m pytest tests/test_agents.py::TestAgentPanel -v`
Expected: FAIL with "cannot import name 'AgentPanel'"

**Step 3: Write minimal implementation**

Add to `lib/agents.py`:

```python
@dataclass
class AgentPanel:
    """Coordinates multiple analysis agents."""

    user_skills_dir: Path
    plugins_dir: Path

    def run_all_agents(self) -> list[AgentResult]:
        """Run all agents and collect results."""
        return [
            self._run_catalog_agent(),
            self._run_workflow_agent(),
            self._run_quality_agent(),
        ]

    def merge_gaps(self, results: list[AgentResult]) -> list[Gap]:
        """Merge and deduplicate gaps from all agents."""
        gaps_by_id: dict[str, Gap] = {}

        for result in results:
            for gap in result.gaps:
                if gap.gap_id not in gaps_by_id:
                    gaps_by_id[gap.gap_id] = gap
                elif gap.confidence > gaps_by_id[gap.gap_id].confidence:
                    # Keep higher confidence version
                    gaps_by_id[gap.gap_id] = gap

        # Sort by priority (lower = higher priority)
        return sorted(gaps_by_id.values(), key=lambda g: g.priority)

    def _run_catalog_agent(self) -> AgentResult:
        """Catalog existing artifacts and find missing skills."""
        # Phase 2.1: Placeholder - returns empty
        return AgentResult(
            agent_name="catalog",
            gaps=[],
            artifacts_scanned=0,
        )

    def _run_workflow_agent(self) -> AgentResult:
        """Analyze workflows for holes."""
        # Phase 2.2: Placeholder - returns empty
        return AgentResult(
            agent_name="workflow-analyzer",
            gaps=[],
            artifacts_scanned=0,
        )

    def _run_quality_agent(self) -> AgentResult:
        """Score artifact quality and flag issues."""
        # Phase 2.3: Placeholder - returns empty
        return AgentResult(
            agent_name="quality-scorer",
            gaps=[],
            artifacts_scanned=0,
        )
```

**Step 4: Run test to verify it passes**

Run: `cd plugins/ecosystem-builder && python -m pytest tests/test_agents.py::TestAgentPanel -v`
Expected: PASS

**Step 5: Commit**

```bash
git add plugins/ecosystem-builder/lib/agents.py plugins/ecosystem-builder/tests/test_agents.py
git commit -m "feat(ecosystem-builder): add AgentPanel with merge_gaps"
```

---

## Task 4: Implement Catalog Agent

**Files:**
- Modify: `plugins/ecosystem-builder/lib/agents.py`
- Modify: `plugins/ecosystem-builder/tests/test_agents.py`

**Step 1: Write the failing test**

Add to `tests/test_agents.py`:

```python
class TestCatalogAgent:
    """Tests for catalog agent functionality."""

    def test_catalog_scans_user_skills(self, tmp_path: Path) -> None:
        """Catalog agent should scan user skills directory."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        # Create two skills
        for name in ["skill-a", "skill-b"]:
            skill_dir = skills_dir / name
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(f"---\nname: {name}\ndescription: Test\n---\n# {name}")

        panel = AgentPanel(
            user_skills_dir=skills_dir,
            plugins_dir=tmp_path / "plugins",
        )
        result = panel._run_catalog_agent()

        assert result.agent_name == "catalog"
        assert result.artifacts_scanned == 2
        assert result.success is True

    def test_catalog_scans_plugin_skills(self, tmp_path: Path) -> None:
        """Catalog agent should scan plugin skills."""
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()

        # Create plugin with skills
        plugin_dir = plugins_dir / "my-plugin"
        plugin_dir.mkdir()
        skills_dir = plugin_dir / "skills" / "my-skill"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text("---\nname: my-skill\n---\n# My Skill")

        panel = AgentPanel(
            user_skills_dir=tmp_path / "user-skills",
            plugins_dir=plugins_dir,
        )
        result = panel._run_catalog_agent()

        assert result.artifacts_scanned >= 1

    def test_catalog_identifies_missing_common_skills(self, tmp_path: Path) -> None:
        """Catalog agent should flag missing common skill patterns."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        # Only one skill - should flag others as missing
        skill_dir = skills_dir / "debugging"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: debugging\ndescription: Debug\n---\n# Debug")

        panel = AgentPanel(
            user_skills_dir=skills_dir,
            plugins_dir=tmp_path / "plugins",
        )
        result = panel._run_catalog_agent()

        # Should find gaps for expected but missing patterns
        assert len(result.gaps) > 0
        gap_titles = [g.title.lower() for g in result.gaps]
        # Common patterns that should be suggested
        assert any("test" in t or "refactor" in t or "documentation" in t for t in gap_titles)
```

**Step 2: Run test to verify it fails**

Run: `cd plugins/ecosystem-builder && python -m pytest tests/test_agents.py::TestCatalogAgent -v`
Expected: FAIL with assertions

**Step 3: Write minimal implementation**

Replace `_run_catalog_agent` in `lib/agents.py`:

```python
    def _run_catalog_agent(self) -> AgentResult:
        """Catalog existing artifacts and find missing skills."""
        import uuid

        existing_skills: set[str] = set()
        scanned = 0

        # Scan user skills
        if self.user_skills_dir.exists():
            for skill_dir in self.user_skills_dir.iterdir():
                if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                    existing_skills.add(skill_dir.name.lower())
                    scanned += 1

        # Scan plugin skills
        if self.plugins_dir.exists():
            for plugin_dir in self.plugins_dir.iterdir():
                if not plugin_dir.is_dir():
                    continue
                skills_path = plugin_dir / "skills"
                if skills_path.exists():
                    for skill_dir in skills_path.iterdir():
                        if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                            existing_skills.add(skill_dir.name.lower())
                            scanned += 1

        # Common skill patterns to check for
        expected_patterns = [
            ("testing", "TDD or testing workflow skill"),
            ("refactoring", "Code refactoring patterns skill"),
            ("documentation", "Documentation generation skill"),
            ("code-review", "Code review workflow skill"),
            ("deployment", "Deployment automation skill"),
        ]

        gaps: list[Gap] = []
        for pattern, description in expected_patterns:
            # Check if any existing skill matches this pattern
            if not any(pattern in skill for skill in existing_skills):
                gaps.append(Gap(
                    gap_id=f"gap-catalog-{uuid.uuid4().hex[:6]}",
                    gap_type=GapType.MISSING_SKILL,
                    title=f"Missing {pattern} skill",
                    description=description,
                    source_agent="catalog",
                    confidence=0.6,
                    priority=2,
                ))

        return AgentResult(
            agent_name="catalog",
            gaps=gaps,
            artifacts_scanned=scanned,
        )
```

Add the import at the top of the method's scope (already in method).

**Step 4: Run test to verify it passes**

Run: `cd plugins/ecosystem-builder && python -m pytest tests/test_agents.py::TestCatalogAgent -v`
Expected: PASS

**Step 5: Commit**

```bash
git add plugins/ecosystem-builder/lib/agents.py plugins/ecosystem-builder/tests/test_agents.py
git commit -m "feat(ecosystem-builder): implement catalog agent with skill scanning"
```

---

## Task 5: Implement Workflow Analyzer Agent

**Files:**
- Modify: `plugins/ecosystem-builder/lib/agents.py`
- Modify: `plugins/ecosystem-builder/tests/test_agents.py`

**Step 1: Write the failing test**

Add to `tests/test_agents.py`:

```python
class TestWorkflowAnalyzerAgent:
    """Tests for workflow analyzer agent."""

    def test_workflow_checks_skill_completeness(self, tmp_path: Path) -> None:
        """Workflow agent should check if skills have complete structure."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        # Create incomplete skill (no examples, no references)
        skill_dir = skills_dir / "incomplete-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: incomplete\n---\n# Incomplete")

        panel = AgentPanel(
            user_skills_dir=skills_dir,
            plugins_dir=tmp_path / "plugins",
        )
        result = panel._run_workflow_agent()

        assert result.agent_name == "workflow-analyzer"
        # Should flag incomplete structure
        assert any(
            g.gap_type == GapType.INCOMPLETE_ARTIFACT
            for g in result.gaps
        )

    def test_workflow_detects_missing_hooks(self, tmp_path: Path) -> None:
        """Workflow agent should detect skills without hook integration."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        # Create skill that could benefit from hooks
        skill_dir = skills_dir / "pre-commit-check"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: pre-commit-check\ndescription: Run before commits\n---\n# Pre-commit"
        )

        panel = AgentPanel(
            user_skills_dir=skills_dir,
            plugins_dir=tmp_path / "plugins",
        )
        result = panel._run_workflow_agent()

        # Should suggest hook integration
        assert any(
            "hook" in g.description.lower() or g.gap_type == GapType.WORKFLOW_HOLE
            for g in result.gaps
        )
```

**Step 2: Run test to verify it fails**

Run: `cd plugins/ecosystem-builder && python -m pytest tests/test_agents.py::TestWorkflowAnalyzerAgent -v`
Expected: FAIL with assertions

**Step 3: Write minimal implementation**

Replace `_run_workflow_agent` in `lib/agents.py`:

```python
    def _run_workflow_agent(self) -> AgentResult:
        """Analyze workflows for holes."""
        import uuid

        gaps: list[Gap] = []
        scanned = 0

        # Check user skills for completeness
        if self.user_skills_dir.exists():
            for skill_dir in self.user_skills_dir.iterdir():
                if not skill_dir.is_dir():
                    continue
                skill_md = skill_dir / "SKILL.md"
                if not skill_md.exists():
                    continue

                scanned += 1
                skill_name = skill_dir.name

                # Check for references directory
                has_references = (skill_dir / "references").exists()
                # Check for examples directory
                has_examples = (skill_dir / "examples").exists()
                # Check for scripts directory
                has_scripts = (skill_dir / "scripts").exists()

                if not any([has_references, has_examples, has_scripts]):
                    gaps.append(Gap(
                        gap_id=f"gap-workflow-{uuid.uuid4().hex[:6]}",
                        gap_type=GapType.INCOMPLETE_ARTIFACT,
                        title=f"Incomplete structure: {skill_name}",
                        description=f"Skill '{skill_name}' lacks references, examples, or scripts",
                        source_agent="workflow-analyzer",
                        confidence=0.7,
                        priority=3,
                    ))

                # Check for hook-worthy skills
                content = skill_md.read_text().lower()
                hook_triggers = ["pre-commit", "before commit", "on save", "pre-push"]
                if any(trigger in content for trigger in hook_triggers):
                    # Check if hooks exist in same plugin
                    hooks_file = skill_dir.parent.parent / "hooks" / "hooks.json"
                    if not hooks_file.exists():
                        gaps.append(Gap(
                            gap_id=f"gap-workflow-{uuid.uuid4().hex[:6]}",
                            gap_type=GapType.WORKFLOW_HOLE,
                            title=f"Missing hook for: {skill_name}",
                            description=f"Skill '{skill_name}' mentions hook triggers but no hooks.json exists",
                            source_agent="workflow-analyzer",
                            confidence=0.75,
                            priority=2,
                        ))

        return AgentResult(
            agent_name="workflow-analyzer",
            gaps=gaps,
            artifacts_scanned=scanned,
        )
```

**Step 4: Run test to verify it passes**

Run: `cd plugins/ecosystem-builder && python -m pytest tests/test_agents.py::TestWorkflowAnalyzerAgent -v`
Expected: PASS

**Step 5: Commit**

```bash
git add plugins/ecosystem-builder/lib/agents.py plugins/ecosystem-builder/tests/test_agents.py
git commit -m "feat(ecosystem-builder): implement workflow analyzer agent"
```

---

## Task 6: Implement Quality Scorer Agent

**Files:**
- Modify: `plugins/ecosystem-builder/lib/agents.py`
- Modify: `plugins/ecosystem-builder/tests/test_agents.py`

**Step 1: Write the failing test**

Add to `tests/test_agents.py`:

```python
class TestQualityScorerAgent:
    """Tests for quality scorer agent."""

    def test_quality_flags_missing_description(self, tmp_path: Path) -> None:
        """Quality agent should flag skills without descriptions."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        skill_dir = skills_dir / "no-desc"
        skill_dir.mkdir()
        # Skill without description field
        (skill_dir / "SKILL.md").write_text("---\nname: no-desc\n---\n# No Description")

        panel = AgentPanel(
            user_skills_dir=skills_dir,
            plugins_dir=tmp_path / "plugins",
        )
        result = panel._run_quality_agent()

        assert result.agent_name == "quality-scorer"
        assert any(
            g.gap_type == GapType.QUALITY_ISSUE and "description" in g.title.lower()
            for g in result.gaps
        )

    def test_quality_flags_short_content(self, tmp_path: Path) -> None:
        """Quality agent should flag skills with minimal content."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        skill_dir = skills_dir / "short-skill"
        skill_dir.mkdir()
        # Very short skill
        (skill_dir / "SKILL.md").write_text("---\nname: short\ndescription: Short\n---\n# S")

        panel = AgentPanel(
            user_skills_dir=skills_dir,
            plugins_dir=tmp_path / "plugins",
        )
        result = panel._run_quality_agent()

        assert any(
            g.gap_type == GapType.QUALITY_ISSUE and "content" in g.description.lower()
            for g in result.gaps
        )

    def test_quality_high_score_for_complete_skill(self, tmp_path: Path) -> None:
        """Quality agent should not flag well-structured skills."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        skill_dir = skills_dir / "complete-skill"
        skill_dir.mkdir()
        (skill_dir / "references").mkdir()
        (skill_dir / "examples").mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: complete\ndescription: A complete skill with examples\n---\n"
            "# Complete Skill\n\n"
            "This is a complete skill with proper documentation.\n\n"
            "## Usage\n\nUse this skill when you need to...\n\n"
            "## Examples\n\nSee the examples directory.\n"
        )

        panel = AgentPanel(
            user_skills_dir=skills_dir,
            plugins_dir=tmp_path / "plugins",
        )
        result = panel._run_quality_agent()

        # Should not flag this skill
        assert not any(
            "complete-skill" in g.title
            for g in result.gaps
        )
```

**Step 2: Run test to verify it fails**

Run: `cd plugins/ecosystem-builder && python -m pytest tests/test_agents.py::TestQualityScorerAgent -v`
Expected: FAIL with assertions

**Step 3: Write minimal implementation**

Replace `_run_quality_agent` in `lib/agents.py`:

```python
    def _run_quality_agent(self) -> AgentResult:
        """Score artifact quality and flag issues."""
        import uuid
        import re

        gaps: list[Gap] = []
        scanned = 0

        def parse_frontmatter(content: str) -> dict:
            """Extract YAML frontmatter from markdown."""
            match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            if not match:
                return {}
            try:
                import yaml
                return yaml.safe_load(match.group(1)) or {}
            except Exception:
                # Simple fallback parsing
                result = {}
                for line in match.group(1).split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        result[key.strip()] = value.strip()
                return result

        # Check user skills for quality
        if self.user_skills_dir.exists():
            for skill_dir in self.user_skills_dir.iterdir():
                if not skill_dir.is_dir():
                    continue
                skill_md = skill_dir / "SKILL.md"
                if not skill_md.exists():
                    continue

                scanned += 1
                skill_name = skill_dir.name
                content = skill_md.read_text()
                frontmatter = parse_frontmatter(content)

                # Check for description
                if not frontmatter.get("description"):
                    gaps.append(Gap(
                        gap_id=f"gap-quality-{uuid.uuid4().hex[:6]}",
                        gap_type=GapType.QUALITY_ISSUE,
                        title=f"Missing description: {skill_name}",
                        description=f"Skill '{skill_name}' lacks a description field in frontmatter",
                        source_agent="quality-scorer",
                        confidence=0.9,
                        priority=2,
                    ))

                # Check content length (excluding frontmatter)
                body = re.sub(r'^---.*?---\s*', '', content, flags=re.DOTALL)
                if len(body.strip()) < 100:
                    gaps.append(Gap(
                        gap_id=f"gap-quality-{uuid.uuid4().hex[:6]}",
                        gap_type=GapType.QUALITY_ISSUE,
                        title=f"Minimal content: {skill_name}",
                        description=f"Skill '{skill_name}' has very short content (< 100 chars)",
                        source_agent="quality-scorer",
                        confidence=0.8,
                        priority=3,
                    ))

        return AgentResult(
            agent_name="quality-scorer",
            gaps=gaps,
            artifacts_scanned=scanned,
        )
```

**Step 4: Run test to verify it passes**

Run: `cd plugins/ecosystem-builder && python -m pytest tests/test_agents.py::TestQualityScorerAgent -v`
Expected: PASS

**Step 5: Commit**

```bash
git add plugins/ecosystem-builder/lib/agents.py plugins/ecosystem-builder/tests/test_agents.py
git commit -m "feat(ecosystem-builder): implement quality scorer agent"
```

---

## Task 7: Wire AgentPanel into Orchestrator

**Files:**
- Modify: `plugins/ecosystem-builder/lib/orchestrator.py`
- Modify: `plugins/ecosystem-builder/tests/test_orchestrator.py`

**Step 1: Write the failing test**

Add to `tests/test_orchestrator.py`:

```python
class TestOrchestratorAnalyze:
    """Tests for orchestrator analyze phase."""

    def test_analyze_uses_agent_panel(self, tmp_path: Path) -> None:
        """_analyze should use AgentPanel and return gaps."""
        # Setup ecosystem
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        skill_dir = skills_dir / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: test\n---\n# Test")

        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()

        state_manager = StateManager(state_dir=tmp_path / "state")
        manifest = state_manager.create_run(artifact_limit=5)

        orchestrator = Orchestrator(
            manifest=manifest,
            staging_dir=tmp_path / "staging",
            user_skills_dir=skills_dir,
            plugins_dir=plugins_dir,
        )

        gaps = orchestrator._analyze()

        # Should return gaps from agent panel
        assert isinstance(gaps, list)
        # All gaps should be dicts with required fields
        for gap in gaps:
            assert "gap_id" in gap
            assert "gap_type" in gap
            assert "title" in gap

    def test_analyze_saves_opportunities(self, tmp_path: Path) -> None:
        """_analyze should save opportunities to opportunities.json."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        state_manager = StateManager(state_dir=tmp_path / "state")
        manifest = state_manager.create_run(artifact_limit=5)

        orchestrator = Orchestrator(
            manifest=manifest,
            staging_dir=tmp_path / "staging",
            user_skills_dir=skills_dir,
            plugins_dir=tmp_path / "plugins",
        )

        orchestrator._analyze()

        # Check opportunities.json was updated
        opportunities_file = manifest.run_dir / "opportunities.json"
        import json
        opportunities = json.loads(opportunities_file.read_text())
        assert isinstance(opportunities, list)
```

**Step 2: Run test to verify it fails**

Run: `cd plugins/ecosystem-builder && python -m pytest tests/test_orchestrator.py::TestOrchestratorAnalyze -v`
Expected: FAIL (Orchestrator doesn't accept new params)

**Step 3: Write minimal implementation**

Update `lib/orchestrator.py`:

```python
"""Single-threaded orchestrator for ecosystem-builder runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from lib.agents import AgentPanel
from lib.logging import EventLogger
from lib.staging import StagingManager
from lib.state import RunManifest


class Orchestrator:
    """Orchestrates a single ecosystem-builder run."""

    def __init__(
        self,
        manifest: RunManifest,
        staging_dir: Path | None = None,
        user_skills_dir: Path | None = None,
        plugins_dir: Path | None = None,
    ) -> None:
        self.manifest = manifest
        self.logger = EventLogger(manifest.run_dir / "log.jsonl")
        self.staging = StagingManager(staging_dir=staging_dir)
        self.build_queue: list[dict[str, Any]] = []

        # Ecosystem paths
        if user_skills_dir is None:
            user_skills_dir = Path.home() / ".claude" / "skills"
        if plugins_dir is None:
            plugins_dir = Path.home() / ".claude" / "plugins"

        self.agent_panel = AgentPanel(
            user_skills_dir=user_skills_dir,
            plugins_dir=plugins_dir,
        )

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
        """Analyze ecosystem for gaps using agent panel."""
        results = self.agent_panel.run_all_agents()
        gaps = self.agent_panel.merge_gaps(results)

        # Convert to dicts and save
        gap_dicts = [g.to_dict() for g in gaps]

        opportunities_file = self.manifest.run_dir / "opportunities.json"
        opportunities_file.write_text(json.dumps(gap_dicts, indent=2))

        return gap_dicts

    def _prioritize(self, gaps: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Prioritize gaps for building. Override in subclass or mock."""
        # Already sorted by priority in merge_gaps
        return gaps

    def _build(self, gap: dict[str, Any]) -> dict[str, Any] | None:
        """Build an artifact for a gap. Override in subclass or mock."""
        # Placeholder - Phase 2 will invoke SkillForge
        return None

    def _validate(self, artifact: dict[str, Any]) -> bool:
        """Validate an artifact. Override in subclass or mock."""
        # Placeholder - Phase 2 will implement validation panel
        return True
```

**Step 4: Run test to verify it passes**

Run: `cd plugins/ecosystem-builder && python -m pytest tests/test_orchestrator.py::TestOrchestratorAnalyze -v`
Expected: PASS

**Step 5: Commit**

```bash
git add plugins/ecosystem-builder/lib/orchestrator.py plugins/ecosystem-builder/tests/test_orchestrator.py
git commit -m "feat(ecosystem-builder): wire AgentPanel into orchestrator _analyze"
```

---

## Task 8: Run Full Test Suite and Fix Regressions

**Files:**
- Possibly modify: any files with failing tests

**Step 1: Run all tests**

Run: `cd plugins/ecosystem-builder && python -m pytest tests/ -v`

**Step 2: Fix any failures**

If there are import errors or test failures, fix them one by one.

**Step 3: Verify all pass**

Run: `cd plugins/ecosystem-builder && python -m pytest tests/ -v`
Expected: All tests PASS

**Step 4: Commit if any fixes**

```bash
git add -A
git commit -m "fix(ecosystem-builder): fix test regressions after AgentPanel integration"
```

---

## Task 9: Update SKILL.md Documentation

**Files:**
- Modify: `plugins/ecosystem-builder/skills/ecosystem-builder/SKILL.md`

**Step 1: Read current SKILL.md**

Already read above.

**Step 2: Update limitations section**

Replace the Limitations section:

```markdown
## Limitations

- Phase 2: Build function returns None (not yet implemented)
- Phase 2: Validation always passes (not yet implemented)
- Gap analysis uses heuristics (expected patterns, structural checks)
- Skills will be staged, not deployed to production
- Human review required via `ecosystem-builder review`
```

**Step 3: Commit**

```bash
git add plugins/ecosystem-builder/skills/ecosystem-builder/SKILL.md
git commit -m "docs(ecosystem-builder): update limitations for Phase 2 progress"
```

---

## Summary

This plan implements the `_analyze()` method with:

1. **Gap data model** (`Gap` dataclass with `GapType` enum)
2. **Agent infrastructure** (`AgentResult`, `AgentPanel`)
3. **Three specialized agents:**
   - Catalog Agent: Scans skills, flags missing common patterns
   - Workflow Analyzer: Checks structure completeness, hook integration
   - Quality Scorer: Validates descriptions, content length
4. **Integration** into orchestrator with `opportunities.json` persistence

**Total: 9 tasks, ~20 test cases**

---

**Plan complete and saved to `docs/plans/2026-01-01-ecosystem-builder-phase2-analyze.md`. Two execution options:**

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

Which approach?
