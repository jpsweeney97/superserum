# Phase 3: Build and Validate Implementation Plan

> **⚠️ SUPERSEDED (2026-01-01):** Phase 3a complete, subagent wiring moved to Phase 3b plan.
>
> - Replacement: `docs/plans/2026-01-01-ecosystem-builder-phase3b-subagent-wiring.md`
>
> *Original preserved for historical reference.*

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement `_build()` with hybrid generation (direct for simple gaps, subagent for complex) and `_validate()` with three-check validation panel (structure, content quality, integration).

**Architecture:** Hybrid builder routes gaps by complexity; simple gaps use template generation, complex gaps spawn SkillForge subagent. Validation panel runs three independent checkers that all must pass. Review CLI integrates StagingManager for accept/reject workflow.

**Tech Stack:** Python 3.12, dataclasses, Task tool for subagents, existing state/staging/agents modules

---

## Task 1: BuildResult Dataclass

**Files:**
- Modify: `plugins/ecosystem-builder/lib/state.py`
- Test: `plugins/ecosystem-builder/tests/test_state.py`

**Step 1: Write the failing test**

Add to `tests/test_state.py`:

```python
class TestBuildResult:
    """Tests for BuildResult dataclass."""

    def test_success_result(self) -> None:
        """Successful build has content and no error."""
        from lib.state import BuildResult

        result = BuildResult(
            name="test-skill",
            content="---\nname: test\n---\n# Test",
            gap_id="gap-123",
        )

        assert result.success is True
        assert result.name == "test-skill"
        assert result.error is None

    def test_failure_result(self) -> None:
        """Failed build has error and no content."""
        from lib.state import BuildResult

        result = BuildResult(
            name="test-skill",
            content=None,
            gap_id="gap-123",
            error="Generation failed",
        )

        assert result.success is False
        assert result.content is None
        assert result.error == "Generation failed"

    def test_to_dict_serialization(self) -> None:
        """BuildResult should serialize to dict."""
        from lib.state import BuildResult

        result = BuildResult(
            name="test-skill",
            content="# Content",
            gap_id="gap-123",
            method="direct",
        )
        data = result.to_dict()

        assert data["name"] == "test-skill"
        assert data["method"] == "direct"
```

**Step 2: Run test to verify it fails**

Run: `python3 plugins/ecosystem-builder/run_tests.py -k TestBuildResult -v`
Expected: FAIL with "cannot import name 'BuildResult'"

**Step 3: Write minimal implementation**

Add to `plugins/ecosystem-builder/lib/state.py` after `Gap` class:

```python
@dataclass
class BuildResult:
    """Result of building an artifact."""

    name: str
    gap_id: str
    content: str | None = None
    error: str | None = None
    method: Literal["direct", "subagent"] = "direct"

    @property
    def success(self) -> bool:
        return self.content is not None and self.error is None

    def to_dict(self) -> dict:
        """Serialize to dict."""
        return {
            "name": self.name,
            "gap_id": self.gap_id,
            "content": self.content,
            "error": self.error,
            "method": self.method,
        }
```

**Step 4: Run test to verify it passes**

Run: `python3 plugins/ecosystem-builder/run_tests.py -k TestBuildResult -v`
Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add plugins/ecosystem-builder/lib/state.py plugins/ecosystem-builder/tests/test_state.py
git commit -m "feat(ecosystem-builder): add BuildResult dataclass"
```

---

## Task 2: ValidationResult and ValidationCheck Dataclasses

**Files:**
- Modify: `plugins/ecosystem-builder/lib/state.py`
- Test: `plugins/ecosystem-builder/tests/test_state.py`

**Step 1: Write the failing test**

Add to `tests/test_state.py`:

```python
class TestValidationResult:
    """Tests for validation result dataclasses."""

    def test_check_passed(self) -> None:
        """Passed check has no issues."""
        from lib.state import ValidationCheck

        check = ValidationCheck(
            name="structure",
            passed=True,
            issues=[],
        )

        assert check.passed is True
        assert len(check.issues) == 0

    def test_check_failed_with_issues(self) -> None:
        """Failed check has issues list."""
        from lib.state import ValidationCheck

        check = ValidationCheck(
            name="content_quality",
            passed=False,
            issues=["Description missing trigger phrases", "Body too short"],
        )

        assert check.passed is False
        assert len(check.issues) == 2

    def test_validation_result_all_passed(self) -> None:
        """ValidationResult passes when all checks pass."""
        from lib.state import ValidationResult, ValidationCheck

        result = ValidationResult(
            artifact_name="test-skill",
            checks=[
                ValidationCheck(name="structure", passed=True, issues=[]),
                ValidationCheck(name="content", passed=True, issues=[]),
                ValidationCheck(name="integration", passed=True, issues=[]),
            ],
        )

        assert result.passed is True
        assert len(result.failed_checks) == 0

    def test_validation_result_any_failed(self) -> None:
        """ValidationResult fails when any check fails."""
        from lib.state import ValidationResult, ValidationCheck

        result = ValidationResult(
            artifact_name="test-skill",
            checks=[
                ValidationCheck(name="structure", passed=True, issues=[]),
                ValidationCheck(name="content", passed=False, issues=["Too short"]),
                ValidationCheck(name="integration", passed=True, issues=[]),
            ],
        )

        assert result.passed is False
        assert len(result.failed_checks) == 1
        assert result.failed_checks[0].name == "content"
```

**Step 2: Run test to verify it fails**

Run: `python3 plugins/ecosystem-builder/run_tests.py -k TestValidationResult -v`
Expected: FAIL with "cannot import name 'ValidationCheck'"

**Step 3: Write minimal implementation**

Add to `plugins/ecosystem-builder/lib/state.py`:

```python
@dataclass
class ValidationCheck:
    """Result of a single validation check."""

    name: str
    passed: bool
    issues: list[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    """Result of validation panel."""

    artifact_name: str
    checks: list[ValidationCheck]

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks)

    @property
    def failed_checks(self) -> list[ValidationCheck]:
        return [c for c in self.checks if not c.passed]
```

**Step 4: Run test to verify it passes**

Run: `python3 plugins/ecosystem-builder/run_tests.py -k TestValidationResult -v`
Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add plugins/ecosystem-builder/lib/state.py plugins/ecosystem-builder/tests/test_state.py
git commit -m "feat(ecosystem-builder): add ValidationResult and ValidationCheck dataclasses"
```

---

## Task 3: SkillBuilder Class with Hybrid Logic

**Files:**
- Create: `plugins/ecosystem-builder/lib/builder.py`
- Create: `plugins/ecosystem-builder/tests/test_builder.py`

**Step 1: Write the failing test**

Create `plugins/ecosystem-builder/tests/test_builder.py`:

```python
"""Tests for SkillBuilder."""

from pathlib import Path

import pytest

from lib.builder import SkillBuilder
from lib.state import Gap, GapType, BuildResult


class TestSkillBuilder:
    """Tests for SkillBuilder class."""

    def test_classify_simple_gap(self) -> None:
        """MISSING_SKILL with clear title is simple."""
        builder = SkillBuilder()
        gap = Gap(
            gap_id="gap-1",
            gap_type=GapType.MISSING_SKILL,
            title="testing",
            description="Add testing skill",
            source_agent="catalog",
            confidence=0.8,
            priority=2,
        )

        assert builder._classify_complexity(gap) == "simple"

    def test_classify_complex_gap(self) -> None:
        """WORKFLOW_HOLE or low confidence is complex."""
        builder = SkillBuilder()
        gap = Gap(
            gap_id="gap-2",
            gap_type=GapType.WORKFLOW_HOLE,
            title="ci-cd-integration",
            description="Complex workflow for CI/CD",
            source_agent="workflow",
            confidence=0.5,
            priority=1,
        )

        assert builder._classify_complexity(gap) == "complex"

    def test_build_simple_direct_generation(self) -> None:
        """Simple gaps use direct template generation."""
        builder = SkillBuilder()
        gap = Gap(
            gap_id="gap-1",
            gap_type=GapType.MISSING_SKILL,
            title="testing",
            description="Add testing skill for pytest patterns",
            source_agent="catalog",
            confidence=0.9,
            priority=2,
        )

        result = builder.build(gap.to_dict())

        assert result.success is True
        assert result.method == "direct"
        assert "---" in result.content  # Has frontmatter
        assert "name:" in result.content
        assert "description:" in result.content


class TestDirectGeneration:
    """Tests for direct skill generation."""

    def test_generates_valid_frontmatter(self) -> None:
        """Direct generation creates valid YAML frontmatter."""
        builder = SkillBuilder()
        gap = Gap(
            gap_id="gap-1",
            gap_type=GapType.MISSING_SKILL,
            title="code-review",
            description="Skill for reviewing code quality",
            source_agent="catalog",
            confidence=0.85,
            priority=2,
        )

        result = builder.build(gap.to_dict())
        content = result.content

        # Parse frontmatter
        lines = content.split("\n")
        assert lines[0] == "---"
        yaml_end = lines.index("---", 1)
        frontmatter = "\n".join(lines[1:yaml_end])

        import yaml
        metadata = yaml.safe_load(frontmatter)
        assert "name" in metadata
        assert "description" in metadata
        assert metadata["name"] == "code-review"

    def test_generates_body_structure(self) -> None:
        """Direct generation creates proper skill body."""
        builder = SkillBuilder()
        gap = Gap(
            gap_id="gap-1",
            gap_type=GapType.MISSING_SKILL,
            title="documentation",
            description="Skill for documentation patterns",
            source_agent="catalog",
            confidence=0.85,
            priority=2,
        )

        result = builder.build(gap.to_dict())
        content = result.content

        # Should have expected sections
        assert "# " in content  # Has heading
        assert "## " in content or "When to Use" in content
```

**Step 2: Run test to verify it fails**

Run: `python3 plugins/ecosystem-builder/run_tests.py -k "TestSkillBuilder or TestDirectGeneration" -v`
Expected: FAIL with "No module named 'lib.builder'"

**Step 3: Write minimal implementation**

Create `plugins/ecosystem-builder/lib/builder.py`:

```python
"""Skill builder with hybrid generation strategy."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from lib.state import BuildResult, Gap, GapType


@dataclass
class SkillBuilder:
    """Builds skills using hybrid direct/subagent strategy."""

    confidence_threshold: float = 0.7

    def build(self, gap_dict: dict[str, Any]) -> BuildResult:
        """Build a skill for the given gap."""
        gap = Gap.from_dict(gap_dict)
        complexity = self._classify_complexity(gap)

        if complexity == "simple":
            return self._build_direct(gap)
        else:
            return self._build_subagent(gap)

    def _classify_complexity(self, gap: Gap) -> str:
        """Classify gap as simple or complex."""
        # Complex: workflow holes, low confidence, or incomplete artifacts
        if gap.gap_type == GapType.WORKFLOW_HOLE:
            return "complex"
        if gap.gap_type == GapType.INCOMPLETE_ARTIFACT:
            return "complex"
        if gap.confidence < self.confidence_threshold:
            return "complex"

        # Simple: missing skills or quality issues with high confidence
        return "simple"

    def _build_direct(self, gap: Gap) -> BuildResult:
        """Generate skill directly from template."""
        name = self._normalize_name(gap.title)
        description = self._generate_description(gap)
        body = self._generate_body(gap)

        content = f"""---
name: {name}
description: {description}
---

# {self._title_case(gap.title)}

{body}
"""

        return BuildResult(
            name=name,
            gap_id=gap.gap_id,
            content=content,
            method="direct",
        )

    def _build_subagent(self, gap: Gap) -> BuildResult:
        """Build using subagent (placeholder for Phase 3b)."""
        # Placeholder - would invoke Task tool with skillforge
        return BuildResult(
            name=self._normalize_name(gap.title),
            gap_id=gap.gap_id,
            content=None,
            error="Subagent generation not yet implemented",
            method="subagent",
        )

    def _normalize_name(self, title: str) -> str:
        """Normalize title to skill name."""
        import re
        name = title.lower().strip()
        name = re.sub(r"[^a-z0-9]+", "-", name)
        name = name.strip("-")
        return name

    def _title_case(self, title: str) -> str:
        """Convert to title case."""
        return " ".join(word.capitalize() for word in title.split("-"))

    def _generate_description(self, gap: Gap) -> str:
        """Generate description with trigger phrases."""
        base = gap.description
        name = gap.title.replace("-", " ")
        return f'Use when working with "{name}" patterns. {base}'

    def _generate_body(self, gap: Gap) -> str:
        """Generate skill body."""
        name = self._title_case(gap.title)
        return f"""## Overview

Skill for {name.lower()} workflows.

## When to Use

- Working with {name.lower()}
- Need guidance on {name.lower()} patterns
- {gap.description}

## Quick Reference

| Pattern | Description |
|---------|-------------|
| Basic | Standard {name.lower()} workflow |

## Process

1. Identify the task
2. Apply appropriate patterns
3. Verify results
"""
```

**Step 4: Run test to verify it passes**

Run: `python3 plugins/ecosystem-builder/run_tests.py -k "TestSkillBuilder or TestDirectGeneration" -v`
Expected: PASS (5 tests)

**Step 5: Commit**

```bash
git add plugins/ecosystem-builder/lib/builder.py plugins/ecosystem-builder/tests/test_builder.py
git commit -m "feat(ecosystem-builder): add SkillBuilder with hybrid generation"
```

---

## Task 4: ValidationPanel Class with Three Checks

**Files:**
- Create: `plugins/ecosystem-builder/lib/validator.py`
- Create: `plugins/ecosystem-builder/tests/test_validator.py`

**Step 1: Write the failing test**

Create `plugins/ecosystem-builder/tests/test_validator.py`:

```python
"""Tests for ValidationPanel."""

from pathlib import Path

import pytest

from lib.validator import ValidationPanel
from lib.state import ValidationResult


class TestStructureCheck:
    """Tests for structure validation."""

    def test_valid_structure_passes(self) -> None:
        """Valid frontmatter and structure passes."""
        panel = ValidationPanel()
        content = """---
name: test-skill
description: Use when testing
---

# Test Skill

## Overview

Content here.
"""
        check = panel._check_structure(content)

        assert check.passed is True
        assert len(check.issues) == 0

    def test_missing_frontmatter_fails(self) -> None:
        """Missing frontmatter fails structure check."""
        panel = ValidationPanel()
        content = """# Test Skill

No frontmatter here.
"""
        check = panel._check_structure(content)

        assert check.passed is False
        assert any("frontmatter" in i.lower() for i in check.issues)

    def test_missing_required_fields_fails(self) -> None:
        """Missing name or description fails."""
        panel = ValidationPanel()
        content = """---
name: test-skill
---

# Test
"""
        check = panel._check_structure(content)

        assert check.passed is False
        assert any("description" in i.lower() for i in check.issues)


class TestContentQualityCheck:
    """Tests for content quality validation."""

    def test_good_content_passes(self) -> None:
        """Content with trigger phrases and good length passes."""
        panel = ValidationPanel()
        content = """---
name: test-skill
description: Use when working with "testing patterns" or need test guidance
---

# Test Skill

## Overview

This skill provides guidance for testing patterns.

## When to Use

- Working with unit tests
- Need testing patterns
- Writing integration tests

## Process

Detailed process content here with enough words to meet the minimum length requirement.
More content to ensure we have sufficient body text for the quality check.
"""
        check = panel._check_content_quality(content)

        assert check.passed is True

    def test_short_body_fails(self) -> None:
        """Body under 100 characters fails."""
        panel = ValidationPanel()
        content = """---
name: test
description: Use when testing
---

# Test

Short.
"""
        check = panel._check_content_quality(content)

        assert check.passed is False
        assert any("length" in i.lower() or "short" in i.lower() for i in check.issues)


class TestIntegrationCheck:
    """Tests for integration validation."""

    def test_unique_name_passes(self, tmp_path: Path) -> None:
        """Skill with unique name passes."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        panel = ValidationPanel(existing_skills_dir=skills_dir)
        check = panel._check_integration("new-skill", "content")

        assert check.passed is True

    def test_conflicting_name_fails(self, tmp_path: Path) -> None:
        """Skill with existing name fails."""
        skills_dir = tmp_path / "skills"
        (skills_dir / "existing-skill").mkdir(parents=True)

        panel = ValidationPanel(existing_skills_dir=skills_dir)
        check = panel._check_integration("existing-skill", "content")

        assert check.passed is False
        assert any("conflict" in i.lower() or "exists" in i.lower() for i in check.issues)


class TestValidationPanel:
    """Tests for full validation panel."""

    def test_validate_runs_all_checks(self, tmp_path: Path) -> None:
        """validate() runs structure, content, and integration checks."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        panel = ValidationPanel(existing_skills_dir=skills_dir)
        content = """---
name: test-skill
description: Use when working with "testing" patterns
---

# Test Skill

## Overview

This skill provides testing guidance with enough content to pass quality checks.

## When to Use

- Testing scenarios
- Test patterns needed
- Quality assurance

## Process

Follow these steps for effective testing patterns and workflows.
Additional content here to meet minimum length requirements.
"""
        result = panel.validate("test-skill", content)

        assert isinstance(result, ValidationResult)
        assert len(result.checks) == 3
        assert result.passed is True
```

**Step 2: Run test to verify it fails**

Run: `python3 plugins/ecosystem-builder/run_tests.py -k "TestStructureCheck or TestContentQualityCheck or TestIntegrationCheck or TestValidationPanel" -v`
Expected: FAIL with "No module named 'lib.validator'"

**Step 3: Write minimal implementation**

Create `plugins/ecosystem-builder/lib/validator.py`:

```python
"""Validation panel for skill artifacts."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from lib.state import ValidationCheck, ValidationResult


@dataclass
class ValidationPanel:
    """Three-check validation panel for skills."""

    existing_skills_dir: Path | None = None
    min_body_length: int = 100
    min_description_length: int = 20

    def validate(self, name: str, content: str) -> ValidationResult:
        """Run all validation checks."""
        checks = [
            self._check_structure(content),
            self._check_content_quality(content),
            self._check_integration(name, content),
        ]

        return ValidationResult(
            artifact_name=name,
            checks=checks,
        )

    def _check_structure(self, content: str) -> ValidationCheck:
        """Check structural requirements."""
        issues = []

        # Check frontmatter exists
        if not content.startswith("---"):
            issues.append("Missing YAML frontmatter (must start with ---)")
            return ValidationCheck(name="structure", passed=False, issues=issues)

        # Parse frontmatter
        lines = content.split("\n")
        try:
            yaml_end = lines.index("---", 1)
            frontmatter_text = "\n".join(lines[1:yaml_end])
        except ValueError:
            issues.append("Malformed frontmatter (missing closing ---)")
            return ValidationCheck(name="structure", passed=False, issues=issues)

        # Check required fields
        import yaml
        try:
            metadata = yaml.safe_load(frontmatter_text)
        except yaml.YAMLError as e:
            issues.append(f"Invalid YAML in frontmatter: {e}")
            return ValidationCheck(name="structure", passed=False, issues=issues)

        if not metadata:
            issues.append("Empty frontmatter")
            return ValidationCheck(name="structure", passed=False, issues=issues)

        if "name" not in metadata:
            issues.append("Missing required field: name")
        if "description" not in metadata:
            issues.append("Missing required field: description")

        return ValidationCheck(
            name="structure",
            passed=len(issues) == 0,
            issues=issues,
        )

    def _check_content_quality(self, content: str) -> ValidationCheck:
        """Check content quality requirements."""
        issues = []

        # Extract body (after frontmatter)
        lines = content.split("\n")
        try:
            yaml_end = lines.index("---", 1)
            body = "\n".join(lines[yaml_end + 1:]).strip()
        except ValueError:
            body = content

        # Check body length
        if len(body) < self.min_body_length:
            issues.append(f"Body too short ({len(body)} chars, minimum {self.min_body_length})")

        # Check description has trigger phrases
        if content.startswith("---"):
            lines = content.split("\n")
            try:
                yaml_end = lines.index("---", 1)
                frontmatter_text = "\n".join(lines[1:yaml_end])
                import yaml
                metadata = yaml.safe_load(frontmatter_text)
                description = metadata.get("description", "")

                # Check for trigger phrase indicators
                has_trigger = (
                    '"' in description or
                    "Use when" in description or
                    "Use for" in description
                )
                if not has_trigger:
                    issues.append("Description should include trigger phrases (quoted terms or 'Use when/for')")
            except (ValueError, yaml.YAMLError):
                pass  # Structure check will catch this

        return ValidationCheck(
            name="content_quality",
            passed=len(issues) == 0,
            issues=issues,
        )

    def _check_integration(self, name: str, content: str) -> ValidationCheck:
        """Check integration with existing ecosystem."""
        issues = []

        # Check for naming conflicts
        if self.existing_skills_dir and self.existing_skills_dir.exists():
            existing_path = self.existing_skills_dir / name
            if existing_path.exists():
                issues.append(f"Name conflict: skill '{name}' already exists")

        return ValidationCheck(
            name="integration",
            passed=len(issues) == 0,
            issues=issues,
        )
```

**Step 4: Run test to verify it passes**

Run: `python3 plugins/ecosystem-builder/run_tests.py -k "TestStructureCheck or TestContentQualityCheck or TestIntegrationCheck or TestValidationPanel" -v`
Expected: PASS (8 tests)

**Step 5: Commit**

```bash
git add plugins/ecosystem-builder/lib/validator.py plugins/ecosystem-builder/tests/test_validator.py
git commit -m "feat(ecosystem-builder): add ValidationPanel with three checks"
```

---

## Task 5: Wire Builder into Orchestrator._build()

**Files:**
- Modify: `plugins/ecosystem-builder/lib/orchestrator.py`
- Modify: `plugins/ecosystem-builder/tests/test_orchestrator.py`

**Step 1: Write the failing test**

Add to `tests/test_orchestrator.py`:

```python
class TestOrchestratorBuild:
    """Tests for orchestrator build phase."""

    def test_build_uses_skill_builder(self, tmp_path: Path) -> None:
        """_build should use SkillBuilder and return artifact dict."""
        state_manager = StateManager(state_dir=tmp_path / "state")
        manifest = state_manager.create_run(artifact_limit=5)

        orchestrator = Orchestrator(
            manifest=manifest,
            staging_dir=tmp_path / "staging",
            user_skills_dir=tmp_path / "skills",
            plugins_dir=tmp_path / "plugins",
        )

        gap = {
            "gap_id": "gap-1",
            "gap_type": "missing_skill",
            "title": "testing",
            "description": "Add testing skill",
            "source_agent": "catalog",
            "confidence": 0.9,
            "priority": 2,
        }

        artifact = orchestrator._build(gap)

        assert artifact is not None
        assert "name" in artifact
        assert "content" in artifact
        assert artifact["name"] == "testing"

    def test_build_returns_none_on_failure(self, tmp_path: Path) -> None:
        """_build should return None when builder fails."""
        state_manager = StateManager(state_dir=tmp_path / "state")
        manifest = state_manager.create_run(artifact_limit=5)

        orchestrator = Orchestrator(
            manifest=manifest,
            staging_dir=tmp_path / "staging",
        )

        # Complex gap triggers subagent (which returns error)
        gap = {
            "gap_id": "gap-1",
            "gap_type": "workflow_hole",
            "title": "complex-workflow",
            "description": "Complex CI/CD workflow",
            "source_agent": "workflow",
            "confidence": 0.5,
            "priority": 1,
        }

        artifact = orchestrator._build(gap)

        # Subagent not implemented, should return None
        assert artifact is None
```

**Step 2: Run test to verify it fails**

Run: `python3 plugins/ecosystem-builder/run_tests.py -k TestOrchestratorBuild -v`
Expected: FAIL (artifact is None because _build returns None placeholder)

**Step 3: Write minimal implementation**

Update `plugins/ecosystem-builder/lib/orchestrator.py`:

Add import at top:
```python
from lib.builder import SkillBuilder
```

Add attribute in `__init__`:
```python
self.builder = SkillBuilder()
```

Replace `_build` method:
```python
def _build(self, gap: dict[str, Any]) -> dict[str, Any] | None:
    """Build an artifact for a gap using SkillBuilder."""
    result = self.builder.build(gap)

    if not result.success:
        self.logger.log("build_failed", {
            "gap_id": gap.get("gap_id"),
            "error": result.error,
        })
        return None

    return {
        "name": result.name,
        "content": result.content,
        "method": result.method,
    }
```

**Step 4: Run test to verify it passes**

Run: `python3 plugins/ecosystem-builder/run_tests.py -k TestOrchestratorBuild -v`
Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add plugins/ecosystem-builder/lib/orchestrator.py plugins/ecosystem-builder/tests/test_orchestrator.py
git commit -m "feat(ecosystem-builder): wire SkillBuilder into orchestrator _build"
```

---

## Task 6: Wire Validator into Orchestrator._validate()

**Files:**
- Modify: `plugins/ecosystem-builder/lib/orchestrator.py`
- Modify: `plugins/ecosystem-builder/tests/test_orchestrator.py`

**Step 1: Write the failing test**

Add to `tests/test_orchestrator.py`:

```python
class TestOrchestratorValidate:
    """Tests for orchestrator validate phase."""

    def test_validate_uses_validation_panel(self, tmp_path: Path) -> None:
        """_validate should use ValidationPanel."""
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

        artifact = {
            "name": "test-skill",
            "content": """---
name: test-skill
description: Use when working with "testing" patterns
---

# Test Skill

## Overview

This skill provides testing guidance with sufficient content length.

## When to Use

- Testing patterns needed
- Unit test guidance

## Process

Follow testing best practices and patterns for quality code.
""",
        }

        passed = orchestrator._validate(artifact)

        assert passed is True

    def test_validate_rejects_invalid_artifact(self, tmp_path: Path) -> None:
        """_validate should reject artifacts that fail checks."""
        state_manager = StateManager(state_dir=tmp_path / "state")
        manifest = state_manager.create_run(artifact_limit=5)

        orchestrator = Orchestrator(
            manifest=manifest,
            staging_dir=tmp_path / "staging",
        )

        artifact = {
            "name": "bad-skill",
            "content": "No frontmatter here",  # Invalid
        }

        passed = orchestrator._validate(artifact)

        assert passed is False
```

**Step 2: Run test to verify it fails**

Run: `python3 plugins/ecosystem-builder/run_tests.py -k TestOrchestratorValidate -v`
Expected: FAIL (passes with placeholder that always returns True)

**Step 3: Write minimal implementation**

Update `plugins/ecosystem-builder/lib/orchestrator.py`:

Add import at top:
```python
from lib.validator import ValidationPanel
```

Add attribute in `__init__`:
```python
self.validator = ValidationPanel(existing_skills_dir=user_skills_dir)
```

Replace `_validate` method:
```python
def _validate(self, artifact: dict[str, Any]) -> bool:
    """Validate an artifact using ValidationPanel."""
    result = self.validator.validate(
        name=artifact["name"],
        content=artifact["content"],
    )

    if not result.passed:
        for check in result.failed_checks:
            self.logger.log("validation_failed", {
                "artifact": artifact["name"],
                "check": check.name,
                "issues": check.issues,
            })

    return result.passed
```

**Step 4: Run test to verify it passes**

Run: `python3 plugins/ecosystem-builder/run_tests.py -k TestOrchestratorValidate -v`
Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add plugins/ecosystem-builder/lib/orchestrator.py plugins/ecosystem-builder/tests/test_orchestrator.py
git commit -m "feat(ecosystem-builder): wire ValidationPanel into orchestrator _validate"
```

---

## Task 7: Implement Review CLI Command

**Files:**
- Modify: `plugins/ecosystem-builder/bin/ecosystem-builder`
- Test: Manual verification

**Step 1: Design the review workflow**

The review command should:
1. List all staged artifacts
2. Show each artifact's metadata and preview
3. Allow accept/reject with reason

**Step 2: Implement the review command**

Replace the placeholder `review` command in `bin/ecosystem-builder`:

```python
@cli.command()
@click.option("--all", "show_all", is_flag=True, help="Show all staged artifacts")
@click.option("--accept", type=str, help="Accept artifact by name")
@click.option("--reject", type=str, help="Reject artifact by name")
@click.option("--reason", type=str, default="", help="Rejection reason")
def review(show_all: bool, accept: str, reject: str, reason: str) -> None:
    """Review staged artifacts."""
    from lib.staging import StagingManager

    staging = StagingManager()
    artifacts = staging.list_staged()

    if accept:
        try:
            prod_path = staging.accept(accept)
            click.echo(f"✓ Accepted '{accept}' → {prod_path}")
        except FileNotFoundError:
            click.echo(f"✗ Artifact not found: {accept}", err=True)
            raise SystemExit(1)
        return

    if reject:
        try:
            rejected_path = staging.reject(reject, reason=reason)
            click.echo(f"✗ Rejected '{reject}' → {rejected_path}")
        except FileNotFoundError:
            click.echo(f"✗ Artifact not found: {reject}", err=True)
            raise SystemExit(1)
        return

    # List staged artifacts
    if not artifacts:
        click.echo("No staged artifacts.")
        click.echo("Run 'ecosystem-builder run --artifacts N' to generate skills.")
        return

    click.echo(f"Staged artifacts ({len(artifacts)}):\n")

    for artifact in artifacts:
        click.echo(f"  {artifact.name}")
        click.echo(f"    Type: {artifact.artifact_type}")
        click.echo(f"    Run: {artifact.run_id}")
        click.echo(f"    Gap: {artifact.gap_id}")
        click.echo(f"    Staged: {artifact.staged_at[:19]}")

        # Show preview if --all
        if show_all:
            skill_file = artifact.path / "SKILL.md"
            if skill_file.exists():
                preview = skill_file.read_text()[:200]
                click.echo(f"    Preview: {preview}...")
        click.echo()

    click.echo("Commands:")
    click.echo("  ecosystem-builder review --accept NAME")
    click.echo("  ecosystem-builder review --reject NAME --reason 'Why'")
```

**Step 3: Test manually**

Run: `python3 plugins/ecosystem-builder/bin/ecosystem-builder review`
Expected: Shows "No staged artifacts" or lists any existing

Run: `python3 plugins/ecosystem-builder/bin/ecosystem-builder review --help`
Expected: Shows help with accept/reject options

**Step 4: Commit**

```bash
git add plugins/ecosystem-builder/bin/ecosystem-builder
git commit -m "feat(ecosystem-builder): implement review CLI command"
```

---

## Task 8: Run Full Test Suite

**Files:**
- All test files

**Step 1: Run all tests**

Run: `python3 plugins/ecosystem-builder/run_tests.py -v`
Expected: All tests pass (should be ~20+ tests now)

**Step 2: Verify no regressions**

Check that:
- TestState tests pass
- TestBuildResult tests pass
- TestValidationResult tests pass
- TestSkillBuilder tests pass
- TestValidationPanel tests pass
- TestOrchestrator tests pass (including new build/validate)
- TestAgentPanel tests pass

**Step 3: Document test count**

```bash
python3 plugins/ecosystem-builder/run_tests.py -v 2>&1 | tail -5
```

**Step 4: Commit if any fixes needed**

```bash
git status
# If clean, proceed to Task 9
```

---

## Task 9: Update SKILL.md Documentation

**Files:**
- Modify: `plugins/ecosystem-builder/skills/ecosystem-builder/SKILL.md`

**Step 1: Update limitations section**

The current SKILL.md says Phase 2 limitations. Update to reflect Phase 3 progress.

Replace the Limitations section:

```markdown
## Limitations

- Subagent generation: Complex gaps return None (subagent invocation not wired)
- Gap analysis uses heuristics (expected patterns, structural checks)
- Skills are staged, not auto-deployed to production
- Human review required via `ecosystem-builder review`
- Validation panel checks structure, quality, integration (no semantic analysis)
```

**Step 2: Update Process section if needed**

Ensure the process accurately describes the current workflow.

**Step 3: Commit**

```bash
git add plugins/ecosystem-builder/skills/ecosystem-builder/SKILL.md
git commit -m "docs(ecosystem-builder): update limitations for Phase 3 progress"
```

---

## Summary

After completing all tasks:

| Component | Status |
|-----------|--------|
| `BuildResult` | New dataclass for build results |
| `ValidationResult` | New dataclass for validation results |
| `SkillBuilder` | Hybrid direct/subagent generation |
| `ValidationPanel` | Three-check validation (structure, quality, integration) |
| `_build()` | Wired to SkillBuilder |
| `_validate()` | Wired to ValidationPanel |
| Review CLI | Accept/reject workflow |

**Remaining for Phase 3b:**
- Wire subagent invocation for complex gaps (currently returns error)
- Add semantic analysis to validation panel (optional enhancement)
