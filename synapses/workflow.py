"""PLAN → BUILD → TEST workflow primitives.

The module is intentionally small and dependency-free so it can be tested in
isolation and reused by command-line tools, services, or notebooks.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal

StepStatus = Literal["pending", "in_progress", "complete"]


@dataclass(frozen=True)
class WorkflowStep:
    """A single workflow step with a display name and execution status."""

    name: str
    status: StepStatus = "pending"

    def with_status(self, status: StepStatus) -> "WorkflowStep":
        """Return a copy of the step with an updated status."""
        return WorkflowStep(name=self.name, status=status)


class Workflow:
    """Immutable-ish workflow helper for rendering ordered engineering phases."""

    def __init__(self, steps: Iterable[WorkflowStep]) -> None:
        self._steps = tuple(steps)
        if not self._steps:
            raise ValueError("A workflow requires at least one step.")

    @property
    def steps(self) -> tuple[WorkflowStep, ...]:
        """Return the workflow steps in execution order."""
        return self._steps

    def mark(self, step_name: str, status: StepStatus) -> "Workflow":
        """Return a new workflow with one named step updated."""
        if step_name not in {step.name for step in self._steps}:
            raise ValueError(f"Unknown workflow step: {step_name}")

        return Workflow(
            step.with_status(status) if step.name == step_name else step
            for step in self._steps
        )

    def render(self) -> str:
        """Render numbered workflow sections for concise status reporting."""
        return "\n".join(
            f"{index}. {step.name}: {step.status}"
            for index, step in enumerate(self._steps, start=1)
        )


def create_default_workflow() -> Workflow:
    """Create the standard PLAN → BUILD → TEST workflow."""
    return Workflow(
        (
            WorkflowStep("Plan"),
            WorkflowStep("Code"),
            WorkflowStep("Test"),
        )
    )
