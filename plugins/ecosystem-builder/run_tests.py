#!/usr/bin/env python3
"""Manual test runner for ecosystem-builder when pytest unavailable."""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent))


def test_state_manager():
    """Test StateManager functionality."""
    from lib.state import StateManager

    print("Testing StateManager...")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        manager = StateManager(state_dir=tmp_path)

        # Test unique IDs
        run1 = manager.create_run(artifact_limit=5)
        run2 = manager.create_run(artifact_limit=5)
        assert run1.run_id != run2.run_id, "Run IDs should be unique"
        print("  ✓ create_run generates unique IDs")

        # Test directory creation
        run = manager.create_run(artifact_limit=5)
        run_dir = tmp_path / run.run_id
        assert run_dir.exists(), "Run directory should exist"
        assert (run_dir / "manifest.json").exists(), "Manifest should exist"
        print("  ✓ create_run creates directory structure")

        # Test load/save
        run = manager.create_run(artifact_limit=10)
        run.budget.artifacts.used = 3
        run.save()
        loaded = manager.load_run(run.run_id)
        assert loaded.budget.artifacts.used == 3, "State should persist"
        print("  ✓ load_run restores state correctly")

        # Test current symlink
        run = manager.create_run(artifact_limit=5)
        current = tmp_path / "current"
        assert current.is_symlink(), "Current should be symlink"
        print("  ✓ current symlink works")

    return 4  # tests passed


def test_event_logger():
    """Test EventLogger functionality."""
    from lib.logging import EventLogger

    print("\nTesting EventLogger...")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        log_file = tmp_path / "log.jsonl"
        logger = EventLogger(log_file)

        # Test logging
        logger.log("run_started", {"artifact_limit": 5})
        logger.log("gap_found", {"gap_id": "gap-001"})

        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 2, "Should have 2 log entries"
        event1 = json.loads(lines[0])
        assert event1["type"] == "run_started"
        print("  ✓ log_event appends to file")

        # Test reading
        events = logger.read_all()
        assert len(events) == 2, "Should read all events"
        assert events[0].type == "run_started"
        print("  ✓ read_events returns all events")

    return 2  # tests passed


def test_staging_manager():
    """Test StagingManager functionality."""
    from lib.staging import StagingManager

    print("\nTesting StagingManager...")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        manager = StagingManager(staging_dir=tmp_path)

        # Test staging
        artifact = manager.stage_skill(
            name="my-skill",
            content="# My Skill\n\nContent here.",
            run_id="run-2026-01-01-abc123",
            gap_id="gap-001",
        )

        skill_dir = tmp_path / "skills" / "my-skill"
        assert skill_dir.exists(), "Skill dir should exist"
        assert (skill_dir / "SKILL.md").exists(), "SKILL.md should exist"
        print("  ✓ stage_skill creates directory")

        # Test listing
        manager.stage_skill("skill-2", "content", "run-1", "gap-2")
        staged = manager.list_staged()
        assert len(staged) == 2, "Should list all staged"
        print("  ✓ list_staged returns all artifacts")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        # Test accept
        staging = tmp_path / "staging"
        production = tmp_path / "production"
        manager = StagingManager(staging_dir=staging, production_dir=production)
        artifact = manager.stage_skill("accept-skill", "content", "run-1", "gap-1")
        manager.accept(artifact.name)
        assert not (staging / "skills" / "accept-skill").exists()
        assert (production / "accept-skill" / "SKILL.md").exists()
        print("  ✓ accept moves to production")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        # Test reject
        staging = tmp_path / "staging"
        rejected = tmp_path / "rejected"
        manager = StagingManager(staging_dir=staging, rejected_dir=rejected)
        artifact = manager.stage_skill("reject-skill", "content", "run-1", "gap-1")
        manager.reject(artifact.name, reason="Not useful")
        assert not (staging / "skills" / "reject-skill").exists()
        assert (rejected / "run-1" / "reject-skill").exists()
        print("  ✓ reject moves to rejected")

    return 4  # tests passed


def test_agent_result():
    """Test AgentResult functionality."""
    from lib.agents import AgentResult
    from lib.state import Gap, GapType

    print("\nTesting AgentResult...")

    # Test creation with gaps
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
    assert result.agent_name == "catalog", "agent_name should match"
    assert len(result.gaps) == 1, "Should have 1 gap"
    assert result.artifacts_scanned == 15, "artifacts_scanned should match"
    assert result.success is True, "success should be True when no error"
    print("  ✓ AgentResult stores gaps and metadata")

    # Test with error
    result = AgentResult(
        agent_name="catalog",
        gaps=[],
        artifacts_scanned=0,
        error="Failed to scan skills directory",
    )
    assert result.success is False, "success should be False with error"
    assert result.error == "Failed to scan skills directory"
    print("  ✓ AgentResult tracks errors correctly")

    return 2  # tests passed


def test_orchestrator():
    """Test Orchestrator functionality."""
    from lib.orchestrator import Orchestrator
    from lib.state import StateManager

    print("\nTesting Orchestrator...")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        state_manager = StateManager(state_dir=tmp_path / "state")
        manifest = state_manager.create_run(artifact_limit=2)

        builds = []
        def mock_build(gap):
            builds.append(gap)
            return {"name": f"skill-{len(builds)}", "content": "content"}

        gaps = [{"gap_id": f"gap-{i}"} for i in range(5)]

        orchestrator = Orchestrator(
            manifest=manifest,
            staging_dir=tmp_path / "staging",
        )
        orchestrator._analyze = Mock(return_value=gaps)
        orchestrator._build = mock_build
        orchestrator._validate = Mock(return_value=True)

        orchestrator.run()

        assert len(builds) == 2, f"Should build exactly 2, got {len(builds)}"
        assert manifest.status == "complete", "Status should be complete"
        assert manifest.budget.artifacts.used == 2
        print("  ✓ run stops when budget exhausted")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        state_manager = StateManager(state_dir=tmp_path / "state")
        manifest = state_manager.create_run(artifact_limit=1)

        orchestrator = Orchestrator(
            manifest=manifest,
            staging_dir=tmp_path / "staging",
        )
        orchestrator._analyze = Mock(return_value=[{"gap_id": "gap-1"}])
        orchestrator._build = Mock(return_value={"name": "skill-1", "content": "c"})
        orchestrator._validate = Mock(return_value=True)

        orchestrator.run()

        log_file = manifest.run_dir / "log.jsonl"
        log_content = log_file.read_text()
        assert "run_started" in log_content
        assert "run_complete" in log_content
        print("  ✓ run logs events correctly")

    return 2  # tests passed


def test_skill_builder():
    """Test SkillBuilder functionality."""
    from lib.builder import SkillBuilder
    from lib.state import Gap, GapType

    print("\nTesting SkillBuilder...")

    builder = SkillBuilder()

    # Test classify simple gap
    gap = Gap(
        gap_id="gap-1",
        gap_type=GapType.MISSING_SKILL,
        title="testing",
        description="Add testing skill",
        source_agent="catalog",
        confidence=0.8,
        priority=2,
    )
    assert builder._classify_complexity(gap) == "simple", "MISSING_SKILL should be simple"
    print("  ✓ classify_simple_gap")

    # Test classify complex gap
    gap = Gap(
        gap_id="gap-2",
        gap_type=GapType.WORKFLOW_HOLE,
        title="ci-cd-integration",
        description="Complex workflow for CI/CD",
        source_agent="workflow",
        confidence=0.5,
        priority=1,
    )
    assert builder._classify_complexity(gap) == "complex", "WORKFLOW_HOLE should be complex"
    print("  ✓ classify_complex_gap")

    # Test build simple direct generation
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
    assert result.success is True, "Build should succeed"
    assert result.method == "direct", "Method should be direct"
    assert "---" in result.content, "Should have frontmatter"
    assert "name:" in result.content, "Should have name field"
    assert "description:" in result.content, "Should have description field"
    print("  ✓ build_simple_direct_generation")

    return 3  # tests passed


def test_direct_generation():
    """Test direct skill generation."""
    import yaml
    from lib.builder import SkillBuilder
    from lib.state import Gap, GapType

    print("\nTesting DirectGeneration...")

    builder = SkillBuilder()

    # Test generates valid frontmatter
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

    lines = content.split("\n")
    assert lines[0] == "---", "Should start with frontmatter"
    yaml_end = lines.index("---", 1)
    frontmatter = "\n".join(lines[1:yaml_end])
    metadata = yaml.safe_load(frontmatter)
    assert "name" in metadata, "Should have name in metadata"
    assert "description" in metadata, "Should have description in metadata"
    assert metadata["name"] == "code-review", "Name should match"
    print("  ✓ generates_valid_frontmatter")

    # Test generates body structure
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

    assert "# " in content, "Should have heading"
    assert "## " in content or "When to Use" in content, "Should have sections"
    print("  ✓ generates_body_structure")

    return 2  # tests passed


def test_orchestrator_validate():
    """Test Orchestrator validate phase."""
    from lib.orchestrator import Orchestrator
    from lib.state import StateManager

    print("\nTesting Orchestrator validate phase...")

    # Test valid artifact passes
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
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
        assert passed is True, "Valid artifact should pass validation"
        print("  ✓ valid artifact passes validation")

    # Test invalid artifact fails
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
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
        assert passed is False, "Invalid artifact should fail validation"
        print("  ✓ invalid artifact fails validation")

    return 2  # tests passed


def test_validator():
    """Test ValidationPanel functionality."""
    from lib.validator import ValidationPanel
    from lib.state import ValidationResult

    print("\nTesting ValidationPanel...")

    # Test structure check - valid
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
    assert check.passed is True, "Valid structure should pass"
    assert len(check.issues) == 0, "No issues expected"
    print("  ✓ valid_structure_passes")

    # Test structure check - missing frontmatter
    content = """# Test Skill

No frontmatter here.
"""
    check = panel._check_structure(content)
    assert check.passed is False, "Missing frontmatter should fail"
    assert any("frontmatter" in i.lower() for i in check.issues), "Should mention frontmatter"
    print("  ✓ missing_frontmatter_fails")

    # Test structure check - missing required fields
    content = """---
name: test-skill
---

# Test
"""
    check = panel._check_structure(content)
    assert check.passed is False, "Missing description should fail"
    assert any("description" in i.lower() for i in check.issues), "Should mention description"
    print("  ✓ missing_required_fields_fails")

    # Test content quality - good content
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
    assert check.passed is True, "Good content should pass"
    print("  ✓ good_content_passes")

    # Test content quality - short body
    content = """---
name: test
description: Use when testing
---

# Test

Short.
"""
    check = panel._check_content_quality(content)
    assert check.passed is False, "Short body should fail"
    assert any("length" in i.lower() or "short" in i.lower() for i in check.issues)
    print("  ✓ short_body_fails")

    # Test integration check - unique name
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        panel = ValidationPanel(existing_skills_dir=skills_dir)
        check = panel._check_integration("new-skill", "content")
        assert check.passed is True, "Unique name should pass"
        print("  ✓ unique_name_passes")

    # Test integration check - conflicting name
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        skills_dir = tmp_path / "skills"
        (skills_dir / "existing-skill").mkdir(parents=True)

        panel = ValidationPanel(existing_skills_dir=skills_dir)
        check = panel._check_integration("existing-skill", "content")
        assert check.passed is False, "Conflicting name should fail"
        assert any("conflict" in i.lower() or "exists" in i.lower() for i in check.issues)
        print("  ✓ conflicting_name_fails")

    # Test full validation
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
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
        assert isinstance(result, ValidationResult), "Should return ValidationResult"
        assert len(result.checks) == 3, "Should have 3 checks"
        assert result.passed is True, "All checks should pass"
        print("  ✓ validate_runs_all_checks")

    return 8  # tests passed


def test_skill_generator():
    """Test SkillGeneratorAgent functionality."""
    from lib.skill_generator import GenerationResult, SkillGeneratorAgent
    from lib.state import Gap, GapType

    print("\nTesting SkillGeneratorAgent...")

    # Test GenerationResult success
    result = GenerationResult(
        name="test-skill",
        content="---\nname: test\n---\n# Test",
        gap_id="gap-123",
    )
    assert result.success is True, "Result with content should be success"
    assert result.error is None, "Success result should have no error"
    print("  ✓ GenerationResult tracks success state")

    # Test GenerationResult failure
    result = GenerationResult(
        name="test-skill",
        content=None,
        gap_id="gap-123",
        error="Generation failed: timeout",
    )
    assert result.success is False, "Result without content should not be success"
    assert "timeout" in result.error, "Error should contain timeout"
    print("  ✓ GenerationResult tracks failure state")

    # Test agent accepts gap dict
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
    result = agent.generate(gap.to_dict())
    assert isinstance(result, GenerationResult), "Should return GenerationResult"
    assert result.gap_id == "gap-1", "gap_id should match"
    print("  ✓ Agent.generate() accepts gap as dict")

    return 3  # tests passed


def test_skill_generation():
    """Test actual skill generation with mock LLM."""
    from lib.skill_generator import SkillGeneratorAgent
    from lib.state import Gap, GapType

    print("\nTesting SkillGeneration...")

    # Test generate with mock LLM
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

    agent = SkillGeneratorAgent(llm_callable=lambda prompt: mock_response)
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
    assert result.success is True, "Generation with mock LLM should succeed"
    assert "ci-cd-integration" in result.content, "Content should include skill name"
    assert "---" in result.content, "Content should include frontmatter"
    print("  ✓ generate_with_mock_llm works")

    # Test generate handles LLM error
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
    assert result.success is False, "Failing LLM should result in failure"
    assert "LLM unavailable" in result.error or "unavailable" in result.error.lower(), \
        "Error should mention LLM unavailable"
    print("  ✓ generate_handles_llm_error")

    return 2  # tests passed


def test_subagent_generation():
    """Test subagent-based skill generation."""
    from lib.builder import SkillBuilder
    from lib.state import Gap, GapType

    print("\nTesting SubagentGeneration...")

    # Test complex gap uses subagent
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

    builder = SkillBuilder(subagent_callable=lambda prompt: mock_response)
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

    assert result.success is True, "Complex gap with subagent should succeed"
    assert result.method == "subagent", "Should use subagent method"
    assert "ci-cd-integration" in result.content, "Content should include skill name"
    print("  ✓ complex_gap_uses_subagent")

    # Test subagent failure returns error
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

    assert result.success is False, "Failing subagent should not succeed"
    assert result.method == "subagent", "Should use subagent method"
    assert "unavailable" in result.error.lower(), "Error should mention unavailable"
    print("  ✓ subagent_failure_returns_error")

    return 2  # tests passed


def test_prompts():
    """Test prompt template functionality."""
    from lib.prompts import build_skill_generation_prompt
    from lib.state import Gap, GapType

    print("\nTesting Prompts...")

    # Test prompt includes gap details
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
    assert "ci-cd-integration" in prompt, "Prompt should include gap title"
    assert "CI/CD workflow" in prompt, "Prompt should include description"
    assert "workflow_hole" in prompt.lower() or "WORKFLOW_HOLE" in prompt, "Prompt should include gap type"
    print("  ✓ prompt_includes_gap_details")

    # Test prompt includes output format
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
    assert "SKILL.md" in prompt or "frontmatter" in prompt.lower(), "Should specify output format"
    assert "name:" in prompt or "description:" in prompt, "Should show field format"
    print("  ✓ prompt_includes_output_format")

    # Test low confidence handling
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
    assert "explore" in prompt.lower() or "clarify" in prompt.lower() or "uncertain" in prompt.lower(), \
        "Low confidence should get exploration guidance"
    print("  ✓ prompt_handles_low_confidence")

    return 3  # tests passed


def main():
    """Run all tests."""
    print("=" * 60)
    print("Ecosystem Builder - Test Suite")
    print("=" * 60)

    total = 0
    try:
        total += test_state_manager()
        total += test_event_logger()
        total += test_staging_manager()
        total += test_agent_result()
        total += test_orchestrator()
        total += test_orchestrator_validate()
        total += test_skill_builder()
        total += test_direct_generation()
        total += test_validator()
        total += test_skill_generator()
        total += test_skill_generation()
        total += test_subagent_generation()
        total += test_prompts()

        print("\n" + "=" * 60)
        print(f"ALL TESTS PASSED: {total}/{total}")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
