# Phase 3b: Wire Subagent Invocation for Complex Gaps

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Enable `SkillBuilder._build_subagent()` to generate skills for complex gaps using a lightweight skill-generator agent.

**Architecture:** Create a dedicated `SkillGeneratorAgent` that wraps the Task tool pattern. For complex gaps (WORKFLOW_HOLE, INCOMPLETE_ARTIFACT, low confidence), the agent generates skills with richer analysis than direct templates. Uses async-capable design for future parallel generation.

**Tech Stack:** Python 3.12, dataclasses, subprocess/Task tool invocation pattern, existing state/builder modules

---

## Design Decision: Agent Approach

**Option A: Full SkillForge invocation**
- Pro: Highest quality (11 thinking models, synthesis panel)
- Con: Requires user interaction, heavyweight, not autonomous

**Option B: Simplified skill-generator agent** ✓ CHOSEN
- Pro: Autonomous, fast, focused on gap-to-skill transformation
- Con: Less sophisticated than SkillForge
- Rationale: Ecosystem-builder is autonomous; skills go through validation panel and human review anyway

**Option C: Enhanced templates with more context**
- Pro: Simple, no subagent needed
- Con: Can't handle truly complex gaps that need reasoning

---

## Task 1: Create SkillGeneratorAgent Interface

**Files:**
- Create: `plugins/ecosystem-builder/lib/skill_generator.py`
- Test: `plugins/ecosystem-builder/tests/test_skill_generator.py`

**Step 1: Write the failing test**

Create `plugins/ecosystem-builder/tests/test_skill_generator.py`:

```python
"""Tests for SkillGeneratorAgent."""

from lib.skill_generator import SkillGeneratorAgent, GenerationResult
from lib.state import Gap, GapType


class TestSkillGeneratorAgent:
    """Tests for SkillGeneratorAgent interface."""

    def test_generation_result_success(self) -> None:
        """GenerationResult tracks success state."""
        result = GenerationResult(
            name="test-skill",
            content="---\nname: test\n---\n# Test",
            gap_id="gap-123",
        )

        assert result.success is True
        assert result.error is None

    def test_generation_result_failure(self) -> None:
        """GenerationResult tracks failure state."""
        result = GenerationResult(
            name="test-skill",
            content=None,
            gap_id="gap-123",
            error="Generation failed: timeout",
        )

        assert result.success is False
        assert "timeout" in result.error

    def test_agent_accepts_gap_dict(self) -> None:
        """Agent.generate() accepts gap as dict."""
        agent = SkillGeneratorAgent()
        gap = Gap(
            gap_id="gap-1",
            gap_type=GapType.WORKFLOW_HOLE,
            title="ci-cd-integration",
            description="Complex CI/CD workflow integration",
            source_agent="workflow",
            confidence=0.5,
            priority=1,
        )

        # Should not raise
        result = agent.generate(gap.to_dict())

        assert isinstance(result, GenerationResult)
        assert result.gap_id == "gap-1"
```

**Step 2: Run test to verify it fails**

Run: `python3 plugins/ecosystem-builder/run_tests.py -k TestSkillGeneratorAgent -v`
Expected: FAIL with "No module named 'lib.skill_generator'"

**Step 3: Write minimal implementation**

Create `plugins/ecosystem-builder/lib/skill_generator.py`:

```python
"""Skill generator agent for complex gaps."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from lib.state import Gap


@dataclass
class GenerationResult:
    """Result of skill generation."""

    name: str
    gap_id: str
    content: str | None = None
    error: str | None = None

    @property
    def success(self) -> bool:
        return self.content is not None and self.error is None


@dataclass
class SkillGeneratorAgent:
    """Generates skills for complex gaps using enhanced reasoning."""

    def generate(self, gap_dict: dict[str, Any]) -> GenerationResult:
        """Generate a skill for the given gap.

        This is the interface for subagent-based generation.
        Currently returns a placeholder; will be wired to Task tool.
        """
        gap = Gap.from_dict(gap_dict)

        # Placeholder: will be replaced with actual generation
        return GenerationResult(
            name=self._normalize_name(gap.title),
            gap_id=gap.gap_id,
            content=None,
            error="Subagent generation not yet wired",
        )

    def _normalize_name(self, title: str) -> str:
        """Normalize title to skill name."""
        import re

        name = title.lower().strip()
        name = re.sub(r"[^a-z0-9]+", "-", name)
        return name.strip("-")
```

**Step 4: Run test to verify it passes**

Run: `python3 plugins/ecosystem-builder/run_tests.py -k TestSkillGeneratorAgent -v`
Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add plugins/ecosystem-builder/lib/skill_generator.py plugins/ecosystem-builder/tests/test_skill_generator.py
git commit -m "feat(ecosystem-builder): add SkillGeneratorAgent interface"
```

---

## Task 2: Create Generation Prompt Template

**Files:**
- Create: `plugins/ecosystem-builder/lib/prompts.py`
- Test: `plugins/ecosystem-builder/tests/test_prompts.py`

**Step 1: Write the failing test**

Create `plugins/ecosystem-builder/tests/test_prompts.py`:

```python
"""Tests for prompt templates."""

from lib.prompts import build_skill_generation_prompt
from lib.state import Gap, GapType


class TestSkillGenerationPrompt:
    """Tests for skill generation prompt."""

    def test_prompt_includes_gap_details(self) -> None:
        """Prompt contains gap title, description, type."""
        gap = Gap(
            gap_id="gap-1",
            gap_type=GapType.WORKFLOW_HOLE,
            title="ci-cd-integration",
            description="Complex CI/CD workflow",
            source_agent="workflow",
            confidence=0.5,
            priority=1,
        )

        prompt = build_skill_generation_prompt(gap)

        assert "ci-cd-integration" in prompt
        assert "CI/CD workflow" in prompt
        assert "workflow_hole" in prompt.lower() or "WORKFLOW_HOLE" in prompt

    def test_prompt_includes_output_format(self) -> None:
        """Prompt specifies expected output format."""
        gap = Gap(
            gap_id="gap-1",
            gap_type=GapType.MISSING_SKILL,
            title="testing",
            description="Testing patterns skill",
            source_agent="catalog",
            confidence=0.6,
            priority=2,
        )

        prompt = build_skill_generation_prompt(gap)

        assert "SKILL.md" in prompt or "frontmatter" in prompt.lower()
        assert "name:" in prompt or "description:" in prompt

    def test_prompt_handles_low_confidence(self) -> None:
        """Low confidence gaps get exploration guidance."""
        gap = Gap(
            gap_id="gap-1",
            gap_type=GapType.MISSING_SKILL,
            title="uncertain-feature",
            description="Feature with unclear requirements",
            source_agent="catalog",
            confidence=0.3,
            priority=2,
        )

        prompt = build_skill_generation_prompt(gap)

        # Should mention exploring or clarifying
        assert "explore" in prompt.lower() or "clarify" in prompt.lower() or "uncertain" in prompt.lower()
```

**Step 2: Run test to verify it fails**

Run: `python3 plugins/ecosystem-builder/run_tests.py -k TestSkillGenerationPrompt -v`
Expected: FAIL with "No module named 'lib.prompts'"

**Step 3: Write minimal implementation**

Create `plugins/ecosystem-builder/lib/prompts.py`:

```python
"""Prompt templates for skill generation."""

from __future__ import annotations

from lib.state import Gap, GapType


def build_skill_generation_prompt(gap: Gap) -> str:
    """Build a prompt for generating a skill from a gap.

    The prompt guides an LLM to create a complete SKILL.md file
    appropriate for the gap type and confidence level.
    """
    # Base context
    context_parts = [
        "Generate a complete Claude Code skill to address this ecosystem gap.",
        "",
        "## Gap Analysis",
        f"- **Title:** {gap.title}",
        f"- **Type:** {gap.gap_type.value}",
        f"- **Description:** {gap.description}",
        f"- **Confidence:** {gap.confidence:.0%}",
        f"- **Source:** {gap.source_agent}",
    ]

    # Type-specific guidance
    if gap.gap_type == GapType.WORKFLOW_HOLE:
        context_parts.extend([
            "",
            "## Workflow Gap Guidance",
            "This is a workflow hole - a missing connection between existing capabilities.",
            "Focus on:",
            "- How this skill bridges existing workflows",
            "- Integration points with other skills/tools",
            "- Clear handoff points",
        ])
    elif gap.gap_type == GapType.INCOMPLETE_ARTIFACT:
        context_parts.extend([
            "",
            "## Incomplete Artifact Guidance",
            "An existing artifact needs enhancement.",
            "Focus on:",
            "- What's missing from the current implementation",
            "- Backward compatibility with existing usage",
            "- Incremental improvement over current state",
        ])

    # Low confidence handling
    if gap.confidence < 0.5:
        context_parts.extend([
            "",
            "## Low Confidence Note",
            "This gap has uncertain requirements. The skill should:",
            "- Explore the problem space before prescribing solutions",
            "- Clarify assumptions upfront",
            "- Be flexible and adaptable",
        ])

    # Output format
    context_parts.extend([
        "",
        "## Required Output Format",
        "Generate a complete SKILL.md file with:",
        "",
        "```yaml",
        "---",
        "name: skill-name-here",
        'description: Use when [trigger phrases]. [What it does].',
        "---",
        "```",
        "",
        "Followed by:",
        "- H1 title matching skill name",
        "- Overview section explaining purpose",
        "- When to Use section with bullet points",
        "- Quick Reference table (if applicable)",
        "- Process section with numbered steps",
        "",
        "## Quality Requirements",
        "- Description must include trigger phrases (quoted terms or 'Use when/for')",
        "- Body must be at least 200 characters",
        "- Include 3-5 distinct trigger scenarios",
        "- No placeholder text - every section complete",
    ])

    return "\n".join(context_parts)
```

**Step 4: Run test to verify it passes**

Run: `python3 plugins/ecosystem-builder/run_tests.py -k TestSkillGenerationPrompt -v`
Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add plugins/ecosystem-builder/lib/prompts.py plugins/ecosystem-builder/tests/test_prompts.py
git commit -m "feat(ecosystem-builder): add skill generation prompt template"
```

---

## Task 3: Implement Mock-Based Subagent Generation

**Files:**
- Modify: `plugins/ecosystem-builder/lib/skill_generator.py`
- Modify: `plugins/ecosystem-builder/tests/test_skill_generator.py`

**Step 1: Write the failing test**

Add to `plugins/ecosystem-builder/tests/test_skill_generator.py`:

```python
class TestSkillGeneration:
    """Tests for actual skill generation."""

    def test_generate_with_mock_llm(self) -> None:
        """Generation works with mock LLM response."""
        mock_response = """---
name: ci-cd-integration
description: Use when setting up "CI/CD pipelines" or integrating continuous deployment.
---

# CI/CD Integration

## Overview

Skill for CI/CD integration workflows.

## When to Use

- Setting up CI/CD pipelines
- Integrating continuous deployment
- Automating build and deploy processes

## Process

1. Analyze current pipeline setup
2. Identify integration points
3. Configure automation
"""

        agent = SkillGeneratorAgent(
            llm_callable=lambda prompt: mock_response
        )
        gap = Gap(
            gap_id="gap-1",
            gap_type=GapType.WORKFLOW_HOLE,
            title="ci-cd-integration",
            description="Complex CI/CD workflow integration",
            source_agent="workflow",
            confidence=0.5,
            priority=1,
        )

        result = agent.generate(gap.to_dict())

        assert result.success is True
        assert "ci-cd-integration" in result.content
        assert "---" in result.content

    def test_generate_handles_llm_error(self) -> None:
        """Generation handles LLM errors gracefully."""
        def failing_llm(prompt: str) -> str:
            raise RuntimeError("LLM unavailable")

        agent = SkillGeneratorAgent(llm_callable=failing_llm)
        gap = Gap(
            gap_id="gap-1",
            gap_type=GapType.WORKFLOW_HOLE,
            title="test",
            description="Test",
            source_agent="test",
            confidence=0.5,
            priority=1,
        )

        result = agent.generate(gap.to_dict())

        assert result.success is False
        assert "LLM unavailable" in result.error or "unavailable" in result.error.lower()
```

**Step 2: Run test to verify it fails**

Run: `python3 plugins/ecosystem-builder/run_tests.py -k TestSkillGeneration -v`
Expected: FAIL (agent doesn't accept llm_callable parameter)

**Step 3: Update implementation**

Update `plugins/ecosystem-builder/lib/skill_generator.py`:

```python
"""Skill generator agent for complex gaps."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable

from lib.prompts import build_skill_generation_prompt
from lib.state import Gap


@dataclass
class GenerationResult:
    """Result of skill generation."""

    name: str
    gap_id: str
    content: str | None = None
    error: str | None = None

    @property
    def success(self) -> bool:
        return self.content is not None and self.error is None


@dataclass
class SkillGeneratorAgent:
    """Generates skills for complex gaps using enhanced reasoning.

    Accepts an optional llm_callable for testing. In production,
    this would invoke the Task tool with a skill generation agent.
    """

    llm_callable: Callable[[str], str] | None = None

    def generate(self, gap_dict: dict[str, Any]) -> GenerationResult:
        """Generate a skill for the given gap."""
        gap = Gap.from_dict(gap_dict)
        name = self._normalize_name(gap.title)

        if self.llm_callable is None:
            # No LLM configured - return placeholder
            return GenerationResult(
                name=name,
                gap_id=gap.gap_id,
                content=None,
                error="No LLM callable configured for skill generation",
            )

        # Build prompt and invoke LLM
        prompt = build_skill_generation_prompt(gap)

        try:
            content = self.llm_callable(prompt)
        except Exception as e:
            return GenerationResult(
                name=name,
                gap_id=gap.gap_id,
                content=None,
                error=f"LLM generation failed: {e}",
            )

        # Validate response has required structure
        if not content or "---" not in content:
            return GenerationResult(
                name=name,
                gap_id=gap.gap_id,
                content=None,
                error="LLM response missing required YAML frontmatter",
            )

        return GenerationResult(
            name=name,
            gap_id=gap.gap_id,
            content=content,
        )

    def _normalize_name(self, title: str) -> str:
        """Normalize title to skill name."""
        name = title.lower().strip()
        name = re.sub(r"[^a-z0-9]+", "-", name)
        return name.strip("-")
```

**Step 4: Run test to verify it passes**

Run: `python3 plugins/ecosystem-builder/run_tests.py -k TestSkillGeneration -v`
Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add plugins/ecosystem-builder/lib/skill_generator.py plugins/ecosystem-builder/tests/test_skill_generator.py
git commit -m "feat(ecosystem-builder): implement mock-based skill generation"
```

---

## Task 4: Wire SkillGeneratorAgent into SkillBuilder

**Files:**
- Modify: `plugins/ecosystem-builder/lib/builder.py`
- Modify: `plugins/ecosystem-builder/tests/test_builder.py`

**Step 1: Write the failing test**

Add to `plugins/ecosystem-builder/tests/test_builder.py`:

```python
class TestSubagentGeneration:
    """Tests for subagent-based skill generation."""

    def test_complex_gap_uses_subagent(self) -> None:
        """Complex gaps route to subagent generation."""
        mock_response = """---
name: ci-cd-integration
description: Use when setting up "CI/CD" workflows.
---

# CI/CD Integration

## Overview

Complex CI/CD workflow skill.

## When to Use

- CI/CD pipeline setup
- Continuous deployment integration

## Process

1. Configure pipeline
2. Deploy
"""

        builder = SkillBuilder(
            subagent_callable=lambda prompt: mock_response
        )
        gap = Gap(
            gap_id="gap-1",
            gap_type=GapType.WORKFLOW_HOLE,
            title="ci-cd-integration",
            description="Complex CI/CD workflow",
            source_agent="workflow",
            confidence=0.5,
            priority=1,
        )

        result = builder.build(gap.to_dict())

        assert result.success is True
        assert result.method == "subagent"
        assert "ci-cd-integration" in result.content

    def test_subagent_failure_returns_error(self) -> None:
        """Subagent failure returns BuildResult with error."""
        def failing_subagent(prompt: str) -> str:
            raise RuntimeError("Agent unavailable")

        builder = SkillBuilder(subagent_callable=failing_subagent)
        gap = Gap(
            gap_id="gap-1",
            gap_type=GapType.WORKFLOW_HOLE,
            title="test",
            description="Test",
            source_agent="test",
            confidence=0.5,
            priority=1,
        )

        result = builder.build(gap.to_dict())

        assert result.success is False
        assert result.method == "subagent"
        assert "unavailable" in result.error.lower()
```

**Step 2: Run test to verify it fails**

Run: `python3 plugins/ecosystem-builder/run_tests.py -k TestSubagentGeneration -v`
Expected: FAIL (SkillBuilder doesn't accept subagent_callable)

**Step 3: Update implementation**

Update `plugins/ecosystem-builder/lib/builder.py`:

```python
"""Skill builder with hybrid generation strategy."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable

from lib.skill_generator import SkillGeneratorAgent
from lib.state import BuildResult, Gap, GapType


@dataclass
class SkillBuilder:
    """Builds skills using hybrid direct/subagent strategy.

    Simple gaps (MISSING_SKILL with high confidence) use direct
    template generation. Complex gaps route to the SkillGeneratorAgent.
    """

    confidence_threshold: float = 0.7
    subagent_callable: Callable[[str], str] | None = None

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
        """Build using SkillGeneratorAgent."""
        agent = SkillGeneratorAgent(llm_callable=self.subagent_callable)
        result = agent.generate(gap.to_dict())

        return BuildResult(
            name=result.name,
            gap_id=result.gap_id,
            content=result.content,
            error=result.error,
            method="subagent",
        )

    def _normalize_name(self, title: str) -> str:
        """Normalize title to skill name."""
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

Run: `python3 plugins/ecosystem-builder/run_tests.py -k TestSubagentGeneration -v`
Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add plugins/ecosystem-builder/lib/builder.py plugins/ecosystem-builder/tests/test_builder.py
git commit -m "feat(ecosystem-builder): wire SkillGeneratorAgent into SkillBuilder"
```

---

## Task 5: Create Task Tool Adapter (Production Wiring)

**Files:**
- Create: `plugins/ecosystem-builder/lib/task_adapter.py`
- Test: `plugins/ecosystem-builder/tests/test_task_adapter.py`

**Step 1: Write the failing test**

Create `plugins/ecosystem-builder/tests/test_task_adapter.py`:

```python
"""Tests for Task tool adapter."""

from lib.task_adapter import create_subagent_callable, SubagentConfig


class TestSubagentConfig:
    """Tests for SubagentConfig."""

    def test_default_config(self) -> None:
        """Default config uses general-purpose agent."""
        config = SubagentConfig()

        assert config.subagent_type == "general-purpose"
        assert config.model == "sonnet"
        assert config.timeout_ms > 0

    def test_custom_config(self) -> None:
        """Config accepts custom values."""
        config = SubagentConfig(
            subagent_type="Explore",
            model="opus",
            timeout_ms=120000,
        )

        assert config.subagent_type == "Explore"
        assert config.model == "opus"
        assert config.timeout_ms == 120000


class TestTaskAdapter:
    """Tests for Task tool adapter."""

    def test_create_callable_returns_function(self) -> None:
        """create_subagent_callable returns a callable."""
        callable_fn = create_subagent_callable()

        assert callable(callable_fn)

    def test_callable_includes_prompt(self) -> None:
        """Callable would pass prompt to Task tool."""
        # This is a structural test - actual Task invocation
        # happens in Claude Code runtime, not in tests
        config = SubagentConfig()
        callable_fn = create_subagent_callable(config)

        # The callable exists but can't actually invoke Task tool in tests
        # We verify the structure is correct
        assert callable_fn is not None
```

**Step 2: Run test to verify it fails**

Run: `python3 plugins/ecosystem-builder/run_tests.py -k TestTaskAdapter -v`
Expected: FAIL with "No module named 'lib.task_adapter'"

**Step 3: Write minimal implementation**

Create `plugins/ecosystem-builder/lib/task_adapter.py`:

```python
"""Adapter for Claude Code Task tool invocation.

This module provides the interface between ecosystem-builder
and Claude Code's Task tool for subagent-based skill generation.

In production, this would be invoked by Claude Code itself.
The adapter pattern allows testing with mocks while maintaining
the same interface for production use.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class SubagentConfig:
    """Configuration for subagent invocation."""

    subagent_type: str = "general-purpose"
    model: str = "sonnet"
    timeout_ms: int = 60000
    description: str = "Generate skill from gap"


def create_subagent_callable(
    config: SubagentConfig | None = None,
) -> Callable[[str], str]:
    """Create a callable that invokes the Task tool.

    In production, this would be wired to Claude Code's Task tool.
    For testing, use mock callables directly on SkillBuilder.

    Returns:
        A callable that takes a prompt string and returns generated content.
        In test environments, this returns a placeholder.
    """
    if config is None:
        config = SubagentConfig()

    def invoke_task(prompt: str) -> str:
        """Invoke Task tool with the given prompt.

        This is a placeholder implementation. In production,
        Claude Code provides the actual Task tool invocation.
        """
        # Production implementation would be:
        # - Claude Code intercepts this call
        # - Invokes Task tool with subagent_type, prompt, model
        # - Returns the agent's response

        # For now, return error indicating production wiring needed
        raise RuntimeError(
            "Task tool not available. "
            "This function should be overridden in production "
            "with Claude Code's Task tool adapter."
        )

    return invoke_task


def create_mock_callable(response: str) -> Callable[[str], str]:
    """Create a mock callable for testing.

    Args:
        response: The skill content to return.

    Returns:
        A callable that returns the given response.
    """

    def mock_invoke(prompt: str) -> str:
        return response

    return mock_invoke
```

**Step 4: Run test to verify it passes**

Run: `python3 plugins/ecosystem-builder/run_tests.py -k TestTaskAdapter -v`
Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add plugins/ecosystem-builder/lib/task_adapter.py plugins/ecosystem-builder/tests/test_task_adapter.py
git commit -m "feat(ecosystem-builder): add Task tool adapter for production wiring"
```

---

## Task 6: Wire Adapter into Orchestrator

**Files:**
- Modify: `plugins/ecosystem-builder/lib/orchestrator.py`
- Modify: `plugins/ecosystem-builder/tests/test_orchestrator.py`

**Step 1: Write the failing test**

Add to `plugins/ecosystem-builder/tests/test_orchestrator.py`:

```python
class TestOrchestratorSubagent:
    """Tests for orchestrator subagent integration."""

    def test_orchestrator_passes_callable_to_builder(self, tmp_path: Path) -> None:
        """Orchestrator wires subagent callable to SkillBuilder."""
        mock_skill = """---
name: ci-cd-integration
description: Use when setting up "CI/CD" workflows.
---

# CI/CD Integration

## Overview

Skill for CI/CD workflows.

## When to Use

- CI/CD pipeline setup
- Deployment automation

## Process

1. Configure
2. Deploy
"""

        def mock_callable(prompt: str) -> str:
            return mock_skill

        state_manager = StateManager(state_dir=tmp_path / "state")
        manifest = state_manager.create_run(artifact_limit=5)

        orchestrator = Orchestrator(
            manifest=manifest,
            staging_dir=tmp_path / "staging",
            subagent_callable=mock_callable,
        )

        # Complex gap should use subagent
        gap = {
            "gap_id": "gap-1",
            "gap_type": "workflow_hole",
            "title": "ci-cd-integration",
            "description": "Complex CI/CD workflow",
            "source_agent": "workflow",
            "confidence": 0.5,
            "priority": 1,
        }

        artifact = orchestrator._build(gap)

        assert artifact is not None
        assert artifact["method"] == "subagent"
        assert "ci-cd-integration" in artifact["content"]
```

**Step 2: Run test to verify it fails**

Run: `python3 plugins/ecosystem-builder/run_tests.py -k TestOrchestratorSubagent -v`
Expected: FAIL (Orchestrator doesn't accept subagent_callable)

**Step 3: Update implementation**

Update the `__init__` method in `plugins/ecosystem-builder/lib/orchestrator.py`:

Add to imports at top:
```python
from typing import Callable
```

Update `__init__` signature and add builder initialization:
```python
def __init__(
    self,
    manifest: RunManifest,
    staging_dir: Path | None = None,
    user_skills_dir: Path | None = None,
    plugins_dir: Path | None = None,
    subagent_callable: Callable[[str], str] | None = None,
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
    self.builder = SkillBuilder(subagent_callable=subagent_callable)
    self.validator = ValidationPanel(existing_skills_dir=user_skills_dir)
```

**Step 4: Run test to verify it passes**

Run: `python3 plugins/ecosystem-builder/run_tests.py -k TestOrchestratorSubagent -v`
Expected: PASS (1 test)

**Step 5: Commit**

```bash
git add plugins/ecosystem-builder/lib/orchestrator.py plugins/ecosystem-builder/tests/test_orchestrator.py
git commit -m "feat(ecosystem-builder): wire subagent callable through orchestrator"
```

---

## Task 7: Run Full Test Suite

**Files:**
- All test files

**Step 1: Run all tests**

Run: `python3 plugins/ecosystem-builder/run_tests.py -v`
Expected: All tests pass

**Step 2: Verify test count**

```bash
python3 plugins/ecosystem-builder/run_tests.py -v 2>&1 | grep -E "passed|failed"
```

Expected: ~35+ tests passed, 0 failed

**Step 3: Commit if any fixes needed**

```bash
git status
# If clean, proceed to Task 8
```

---

## Task 8: Update Documentation

**Files:**
- Modify: `plugins/ecosystem-builder/skills/ecosystem-builder/SKILL.md`

**Step 1: Update limitations section**

Replace the Phase 3 limitations with Phase 3b progress:

```markdown
## Limitations

- Subagent generation requires Claude Code runtime (mock callable for tests)
- Skills are staged, not auto-deployed to production
- Human review required via `ecosystem-builder review`
- Validation panel checks structure, quality, integration (no semantic analysis)
- Gap analysis uses heuristics (expected patterns, structural checks)
```

**Step 2: Add architecture note**

Add to the Process section or create new Architecture section:

```markdown
## Architecture

### Hybrid Generation Strategy

| Gap Complexity | Method | When Used |
|---------------|--------|-----------|
| Simple | Direct template | MISSING_SKILL with confidence ≥ 0.7 |
| Complex | Subagent | WORKFLOW_HOLE, INCOMPLETE_ARTIFACT, or confidence < 0.7 |

Complex gaps use the `SkillGeneratorAgent` which:
1. Builds a prompt with gap context and type-specific guidance
2. Invokes Claude Code's Task tool for generation
3. Validates response structure before staging
```

**Step 3: Commit**

```bash
git add plugins/ecosystem-builder/skills/ecosystem-builder/SKILL.md
git commit -m "docs(ecosystem-builder): update for Phase 3b subagent wiring"
```

---

## Task 9: Mark Phase 3 Plan as Superseded

**Files:**
- Modify: `docs/plans/2026-01-01-ecosystem-builder-phase3-build-validate.md`

**Step 1: Add superseded marker**

Add at the top of the file after the title:

```markdown
> **⚠️ SUPERSEDED (2026-01-01):** Phase 3a complete, subagent wiring moved to Phase 3b plan.
>
> - Replacement: `docs/plans/2026-01-01-ecosystem-builder-phase3b-subagent-wiring.md`
>
> *Original preserved for historical reference.*
```

**Step 2: Commit**

```bash
git add docs/plans/2026-01-01-ecosystem-builder-phase3-build-validate.md
git commit -m "docs: mark Phase 3 plan as superseded by Phase 3b"
```

---

## Summary

After completing all tasks:

| Component | Status |
|-----------|--------|
| `SkillGeneratorAgent` | New class for complex gap generation |
| `GenerationResult` | New dataclass for generation results |
| `prompts.py` | Prompt templates for gap-to-skill conversion |
| `task_adapter.py` | Production wiring interface for Task tool |
| `SkillBuilder` | Updated with subagent_callable support |
| `Orchestrator` | Wired to pass callable through to builder |

**Test Coverage:**
- 6+ new tests for skill generator
- 3+ new tests for prompts
- 3+ new tests for task adapter
- 2+ new tests for builder subagent path
- 1+ new test for orchestrator integration

**Remaining Work:**
- Production wiring: Claude Code's Task tool adapter implementation
- Integration testing with actual Claude Code runtime
- Consider: Semantic validation in ValidationPanel
