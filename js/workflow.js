/**
 * PLAN → BUILD → TEST workflow primitives.
 *
 * The module is dependency-free and exports small functions that can be tested
 * independently in Node.js or reused by browser-focused code.
 */

const VALID_STATUSES = new Set(["pending", "in_progress", "complete"]);

/**
 * Create a workflow step object.
 * @param {string} name - Human-readable step name.
 * @param {string} [status="pending"] - Step execution status.
 * @returns {{name: string, status: string}}
 */
export function createStep(name, status = "pending") {
  if (!VALID_STATUSES.has(status)) {
    throw new Error(`Invalid workflow status: ${status}`);
  }

  return Object.freeze({ name, status });
}

/**
 * Create the standard PLAN → BUILD → TEST workflow.
 * @returns {ReadonlyArray<{name: string, status: string}>}
 */
export function createDefaultWorkflow() {
  return Object.freeze([createStep("Plan"), createStep("Code"), createStep("Test")]);
}

/**
 * Return a new workflow with one named step updated.
 * @param {ReadonlyArray<{name: string, status: string}>} workflow - Ordered steps.
 * @param {string} stepName - Step name to update.
 * @param {string} status - New status.
 * @returns {ReadonlyArray<{name: string, status: string}>}
 */
export function markStep(workflow, stepName, status) {
  let found = false;

  const updated = workflow.map((step) => {
    if (step.name !== stepName) {
      return step;
    }

    found = true;
    return createStep(step.name, status);
  });

  if (!found) {
    throw new Error(`Unknown workflow step: ${stepName}`);
  }

  return Object.freeze(updated);
}

/**
 * Render numbered workflow sections for concise status reporting.
 * @param {ReadonlyArray<{name: string, status: string}>} workflow - Ordered steps.
 * @returns {string}
 */
export function renderWorkflow(workflow) {
  return workflow.map((step, index) => `${index + 1}. ${step.name}: ${step.status}`).join("\n");
}
