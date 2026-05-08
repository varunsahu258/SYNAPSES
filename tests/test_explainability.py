"""Tests for explainability engine."""

from synapses.application.services.explainability_service import ExplainabilityEngine, sample_explanation_inputs


def test_generate_explanations_with_supported_claims() -> None:
    timeline, interventions = sample_explanation_inputs()
    report = ExplainabilityEngine().generate(timeline, interventions)

    assert report.explanations
    summaries = [item.summary for item in report.explanations]
    assert any("Crime increased" in s for s in summaries)
    assert any("Migration increased" in s for s in summaries)
    assert any("Director intervention" in s for s in summaries)


def test_explanations_ranked_by_confidence_desc() -> None:
    timeline, interventions = sample_explanation_inputs()
    report = ExplainabilityEngine().generate(timeline, interventions)
    confidences = [item.confidence for item in report.explanations]
    assert confidences == sorted(confidences, reverse=True)


def test_trace_reconstruction_links_step_interventions() -> None:
    timeline, interventions = sample_explanation_inputs()
    report = ExplainabilityEngine().generate(timeline, interventions)
    step2 = [row for row in report.trace if row["step"] == 2][0]
    assert step2["interventions"][0]["action"] == "increase_safety_programs"
