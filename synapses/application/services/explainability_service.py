"""Explainability engine for socio-economic simulation outputs.

This module is intentionally decoupled from simulation internals: it consumes
serializable metric timelines and intervention history to produce human-readable,
evidence-linked explanations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping


@dataclass(frozen=True)
class ExplanationItem:
    """One evidence-backed narrative explanation."""

    event_type: str
    summary: str
    confidence: float
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class ExplainabilityReport:
    """Complete explainability output for one timeline."""

    explanations: tuple[ExplanationItem, ...]
    event_graph: dict[str, tuple[str, ...]]
    trace: tuple[dict[str, Any], ...]


class ExplainabilityEngine:
    """Generate prioritized, human-readable explanations from metric timelines."""

    def generate(
        self,
        metrics_over_time: Iterable[Mapping[str, Any]],
        intervention_history: Iterable[Mapping[str, Any]] | None = None,
    ) -> ExplainabilityReport:
        timeline = tuple(dict(entry) for entry in metrics_over_time)
        interventions = tuple(dict(event) for event in (intervention_history or ()))

        explanations: list[ExplanationItem] = []
        graph: dict[str, tuple[str, ...]] = {}
        trace = self._reconstruct_trace(timeline, interventions)

        explanations.extend(self._explain_crime_spikes(timeline, graph))
        explanations.extend(self._explain_inequality_changes(timeline, graph))
        explanations.extend(self._explain_economic_instability(timeline, graph))
        explanations.extend(self._explain_resource_shortages(timeline, graph))
        explanations.extend(self._explain_director_interventions(interventions, graph))
        explanations.extend(self._explain_migration_patterns(timeline, graph))

        ranked = tuple(sorted(explanations, key=lambda item: item.confidence, reverse=True))
        return ExplainabilityReport(explanations=ranked, event_graph=graph, trace=trace)

    def _explain_crime_spikes(self, timeline: tuple[dict[str, Any], ...], graph: dict[str, tuple[str, ...]]) -> list[ExplanationItem]:
        items: list[ExplanationItem] = []
        for prev, cur in self._pairs(timeline):
            crime_delta = _to_float(cur.get("crime_rate")) - _to_float(prev.get("crime_rate"))
            if crime_delta < 5:
                continue

            evidence: list[str] = [f"crime_rate increased by {crime_delta:.1f}"]
            if _to_float(cur.get("food_supply")) < _to_float(prev.get("food_supply")):
                evidence.append("food_supply declined")
            if _to_float(cur.get("price")) > _to_float(prev.get("price")):
                evidence.append("price increased")

            if len(evidence) > 1:
                summary = "Crime increased because food shortages correlated with inflation pressure."
                graph["crime_spike"] = ("resource_shortage", "inflation")
                confidence = 0.9
            else:
                summary = "Crime increased alongside adverse socio-economic shifts in the same interval."
                graph["crime_spike"] = ("trend_shift",)
                confidence = 0.6
            items.append(ExplanationItem("crime_spike", summary, confidence, tuple(evidence)))
        return items

    def _explain_inequality_changes(self, timeline: tuple[dict[str, Any], ...], graph: dict[str, tuple[str, ...]]) -> list[ExplanationItem]:
        items: list[ExplanationItem] = []
        for prev, cur in self._pairs(timeline):
            gini_delta = _to_float(cur.get("gini")) - _to_float(prev.get("gini"))
            if abs(gini_delta) < 0.05:
                continue
            direction = "increased" if gini_delta > 0 else "decreased"
            summary = f"Inequality {direction} due to distribution changes observed in consecutive metrics."
            graph["inequality_change"] = ("wealth_distribution",)
            items.append(
                ExplanationItem(
                    "inequality_change",
                    summary,
                    0.75,
                    (f"gini changed by {gini_delta:.3f}",),
                )
            )
        return items

    def _explain_economic_instability(self, timeline: tuple[dict[str, Any], ...], graph: dict[str, tuple[str, ...]]) -> list[ExplanationItem]:
        items: list[ExplanationItem] = []
        for prev, cur in self._pairs(timeline):
            price_jump = abs(_to_float(cur.get("price")) - _to_float(prev.get("price")))
            satisfaction_drop = _to_float(prev.get("average_satisfaction")) - _to_float(cur.get("average_satisfaction"))
            if price_jump >= 2 and satisfaction_drop >= 5:
                graph["economic_instability"] = ("inflation", "wellbeing_decline")
                items.append(
                    ExplanationItem(
                        "economic_instability",
                        "Economic instability rose as prices shifted sharply while social satisfaction declined.",
                        0.85,
                        (f"price movement: {price_jump:.1f}", f"satisfaction drop: {satisfaction_drop:.1f}"),
                    )
                )
        return items

    def _explain_resource_shortages(self, timeline: tuple[dict[str, Any], ...], graph: dict[str, tuple[str, ...]]) -> list[ExplanationItem]:
        items: list[ExplanationItem] = []
        if not timeline:
            return items

        low_food_steps = [entry for entry in timeline if _to_float(entry.get("food_supply")) < 50]
        if low_food_steps:
            graph["resource_shortage"] = ("food_supply",)
            items.append(
                ExplanationItem(
                    "resource_shortage",
                    "Resource shortages emerged because food supply remained below the resilience threshold.",
                    0.8,
                    (f"low food steps: {len(low_food_steps)}",),
                )
            )
        return items

    def _explain_director_interventions(self, interventions: tuple[dict[str, Any], ...], graph: dict[str, tuple[str, ...]]) -> list[ExplanationItem]:
        items: list[ExplanationItem] = []
        if not interventions:
            return items
        grouped: dict[str, int] = {}
        for event in interventions:
            action = str(event.get("action", "unknown"))
            grouped[action] = grouped.get(action, 0) + 1

        for action, count in grouped.items():
            graph[f"director:{action}"] = ("policy_tracing",)
            items.append(
                ExplanationItem(
                    "director_intervention",
                    f"Director intervention '{action}' was applied {count} times in response to observed risk signals.",
                    0.7,
                    (f"count={count}",),
                )
            )
        return items

    def _explain_migration_patterns(self, timeline: tuple[dict[str, Any], ...], graph: dict[str, tuple[str, ...]]) -> list[ExplanationItem]:
        items: list[ExplanationItem] = []
        for prev, cur in self._pairs(timeline):
            prev_m = _to_float(prev.get("migration_rate"))
            cur_m = _to_float(cur.get("migration_rate"))
            if cur_m - prev_m >= 3:
                evidence = [f"migration_rate increased by {cur_m - prev_m:.1f}"]
                if _to_float(cur.get("food_supply")) < _to_float(prev.get("food_supply")):
                    evidence.append("resource availability declined")
                graph["migration_pattern"] = ("regional_resource_imbalance",)
                items.append(
                    ExplanationItem(
                        "migration_pattern",
                        "Migration increased due to regional resource imbalance.",
                        0.78,
                        tuple(evidence),
                    )
                )
        return items

    def _reconstruct_trace(self, timeline: tuple[dict[str, Any], ...], interventions: tuple[dict[str, Any], ...]) -> tuple[dict[str, Any], ...]:
        intervention_by_step: dict[int, list[dict[str, Any]]] = {}
        for event in interventions:
            step = int(_to_float(event.get("step", 0)))
            intervention_by_step.setdefault(step, []).append(event)

        trace: list[dict[str, Any]] = []
        for entry in timeline:
            step = int(_to_float(entry.get("step", 0)))
            trace.append({
                "step": step,
                "metrics": entry,
                "interventions": tuple(intervention_by_step.get(step, ())),
            })
        return tuple(trace)

    def _pairs(self, timeline: tuple[dict[str, Any], ...]) -> Iterable[tuple[dict[str, Any], dict[str, Any]]]:
        return zip(timeline, timeline[1:])


def sample_explanation_inputs() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return small sample timeline/intervention inputs for documentation and demos."""
    timeline = [
        {"step": 1, "crime_rate": 10, "gini": 0.30, "food_supply": 80, "price": 10, "average_satisfaction": 60, "migration_rate": 1},
        {"step": 2, "crime_rate": 18, "gini": 0.38, "food_supply": 42, "price": 12, "average_satisfaction": 52, "migration_rate": 5},
    ]
    interventions = [{"step": 2, "action": "increase_safety_programs", "reason": "high_crime"}]
    return timeline, interventions


def _to_float(value: Any) -> float:
    if isinstance(value, bool):
        return float(int(value))
    if isinstance(value, (int, float)):
        return float(value)
    return 0.0
