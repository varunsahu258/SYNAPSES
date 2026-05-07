import assert from "node:assert/strict";
import test from "node:test";

import { createDefaultWorkflow, createStep, markStep, renderWorkflow } from "./workflow.js";

test("default workflow renders requested sections", () => {
  const workflow = createDefaultWorkflow();

  assert.equal(renderWorkflow(workflow), "1. Plan: pending\n2. Code: pending\n3. Test: pending");
});

test("markStep returns a new workflow with an updated step", () => {
  const workflow = createDefaultWorkflow();
  const updated = markStep(workflow, "Code", "complete");

  assert.equal(workflow[1].status, "pending");
  assert.equal(updated[1].status, "complete");
});

test("markStep rejects unknown steps", () => {
  const workflow = createDefaultWorkflow();

  assert.throws(() => markStep(workflow, "Deploy", "complete"), /Unknown workflow step/);
});

test("createStep rejects invalid statuses", () => {
  assert.throws(() => createStep("Plan", "started"), /Invalid workflow status/);
});
