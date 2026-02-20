"""Module description."""
from typing import Any, Mapping, Callable
from datetime import timedelta
import asyncio
import pytest
from haystack import component, Pipeline
from haystack.components.builders.prompt_builder import PromptBuilder
from aiobreaker import CircuitBreakerError, CircuitBreaker
from haystack.core.errors import PipelineRuntimeError


def fake_generator_constructor(breaker: CircuitBreaker, llm_generator: Callable):
    """Fake generator constructor."""

    class SafeComponent:
        """Represents SafeComponent."""

        def __init__(self, component_instance: Any):
            self._component = component_instance
            self._breaker = breaker

            if hasattr(component_instance, "__haystack_input__"):
                self.__haystack_input__ = component_instance.__haystack_input__
            if hasattr(component_instance, "__haystack_output__"):
                self.__haystack_output__ = component_instance.__haystack_output__

        def run(self, *args: Any, **kwargs: Any) -> Mapping[str, Any]:
            return self._breaker.call(self._component.run, *args, **kwargs)

        def __getattr__(self, item: str) -> Any:
            return getattr(self._component, item)

    pipeleine = Pipeline()
    pipeleine.add_component(
        "prompt",
        PromptBuilder(template="Hello {{ dialog }}")
    )

    safe_llm = SafeComponent(llm_generator())
    pipeleine.add_component("llm", safe_llm)
    pipeleine.connect("prompt", "llm")
    return pipeleine


class FailingService:
    def run(self):
        raise RuntimeError("boom")


class TestCircuitBreak:
    """Test suite for circuit break."""

    def test_unit(self):
        """Test unit."""

        breaker = CircuitBreaker(
            fail_max=2,
            timeout_duration=timedelta(seconds=1),
        )

        service = FailingService()

        with pytest.raises(RuntimeError):
            breaker.call(service.run)

        assert breaker.current_state.name == "CLOSED"
        assert breaker.fail_counter == 1

        with pytest.raises(CircuitBreakerError) as exc:
            breaker.call(service.run)

        assert breaker.current_state.name == "OPEN"
        assert breaker.fail_counter == 2

        assert isinstance(exc.value.__cause__, RuntimeError)

        with pytest.raises(CircuitBreakerError) as exc:
            breaker.call(service.run)

        assert breaker.current_state.name == "OPEN"
        assert "circuit breaker still open" in exc.value.message

    @pytest.mark.asyncio
    async def test_pipeline(self):

        test_breaker = CircuitBreaker(
            fail_max=2,
            timeout_duration=timedelta(seconds=2),
        )

        @component
        class GeneratorWithFalure:
            @component.output_types(answer=str)
            def run(self, prompt: str):
                raise RuntimeError("Simulated failure")

        @component
        class GeneratorWithSuccess:
            @component.output_types(answer=str)
            def run(self, prompt: str):
                return {"answer": "test"}

        PIPELINE_WITH_FAILURE = fake_generator_constructor(
            test_breaker, GeneratorWithFalure)
        PIPELINE_WITH_SUCCESS = fake_generator_constructor(
            test_breaker, GeneratorWithSuccess)

        assert test_breaker.current_state.name == "CLOSED"

        with pytest.raises(PipelineRuntimeError):
            await asyncio.to_thread(PIPELINE_WITH_FAILURE.run, {"prompt": {"dialog": "hello"}})

        assert test_breaker.current_state.name == "CLOSED"

        with pytest.raises(PipelineRuntimeError):
            await asyncio.to_thread(PIPELINE_WITH_FAILURE.run, {"prompt": {"dialog": "hello"}})

        assert test_breaker.current_state.name == "OPEN"

        with pytest.raises(PipelineRuntimeError) as exc:
            await asyncio.to_thread(PIPELINE_WITH_FAILURE.run, {"prompt": {"dialog": "hello"}})

        assert test_breaker.current_state.name == "OPEN"
        assert "circuit breaker still open" in exc.value.args[0]

        await asyncio.sleep(2.5)
        assert test_breaker.current_state.name == "OPEN"

        with pytest.raises(PipelineRuntimeError) as exc:
            await asyncio.to_thread(PIPELINE_WITH_FAILURE.run, {"prompt": {"dialog": "hello"}})

        assert test_breaker.current_state.name == "OPEN"
        assert "Trial call failed" in exc.value.args[0]

        await asyncio.sleep(2.5)
        assert test_breaker.current_state.name == "OPEN"
        await asyncio.to_thread(PIPELINE_WITH_SUCCESS.run, {"prompt": {"dialog": "hello"}})
        assert test_breaker.current_state.name == "CLOSED"
