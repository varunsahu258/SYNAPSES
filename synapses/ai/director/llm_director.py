class LLMDirector:
    VALID_ACTIONS = {
        "redistribute_resources",
        "fund_public_services",
        "increase_safety_programs",
        "monitor",
    }

    def __init__(
        self,
        api_key: str,
        model: str = "nvidia/nemotron-3-super-120b-a12b:free",
    ):
        self._api_key = api_key
        self._model = model
        self._endpoint = "https://openrouter.ai/api/v1/chat/completions"

    def recommend(self, global_metrics: dict | None) -> list[dict]:
        metrics = global_metrics or {}
        prompt = self._build_prompt(metrics)
        payload = {
            "model": self._model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "max_tokens": 64,
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        try:
            import requests

            response = requests.post(self._endpoint, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            text = response.json()["choices"][0]["message"]["content"]
            return self._parse_response(text)
        except Exception:
            return [{"action": "monitor", "reason": "llm_unavailable"}]

    def _build_prompt(self, metrics: dict) -> str:
        return f"""
You are the AI Director of a socio-economic simulation.

Current metrics:
- Gini coefficient (wealth inequality): {metrics.get("gini", 0):.3f}
- Crime rate: {metrics.get("crime_rate", 0)}
- Average satisfaction: {metrics.get("average_satisfaction", 0):.1f}
- Food supply: {metrics.get("food_supply", 0)}

Choose exactly ONE intervention from this list:

- redistribute_resources
- fund_public_services
- increase_safety_programs
- monitor

Respond with ONLY the intervention name.
Do not explain your reasoning.
"""

    def _parse_response(self, text: str) -> list[dict]:
        action = text.strip().lower().replace("-", "_")
        if action not in self.VALID_ACTIONS:
            action = "monitor"
        return [{"action": action, "reason": "llm_decision"}]
