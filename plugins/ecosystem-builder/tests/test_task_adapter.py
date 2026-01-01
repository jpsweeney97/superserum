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
