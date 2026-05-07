"""Unit tests for the Python workflow primitives."""

import unittest

from synapses import Workflow, WorkflowStep, create_default_workflow


class WorkflowTests(unittest.TestCase):
    """Verify default rendering and immutable step updates."""

    def test_default_workflow_renders_requested_sections(self) -> None:
        workflow = create_default_workflow()

        self.assertEqual(
            workflow.render(),
            "1. Plan: pending\n2. Code: pending\n3. Test: pending",
        )

    def test_mark_returns_new_workflow_with_updated_step(self) -> None:
        workflow = create_default_workflow()
        updated = workflow.mark("Code", "complete")

        self.assertEqual(workflow.steps[1].status, "pending")
        self.assertEqual(updated.steps[1].status, "complete")

    def test_mark_rejects_unknown_step(self) -> None:
        workflow = Workflow((WorkflowStep("Plan"),))

        with self.assertRaisesRegex(ValueError, "Unknown workflow step"):
            workflow.mark("Deploy", "complete")

    def test_workflow_requires_steps(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least one step"):
            Workflow(())


if __name__ == "__main__":
    unittest.main()
