import types
from unittest.mock import Mock, patch

from synapses.ai.director.llm_director import LLMDirector


def test_llm_director_recommend_returns_valid_action_list() -> None:
    fake_response = Mock()
    fake_response.raise_for_status = Mock()
    fake_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "increase_safety_programs",
                }
            }
        ]
    }

    fake_requests = types.SimpleNamespace(post=Mock(return_value=fake_response))
    with patch.dict("sys.modules", {"requests": fake_requests}):
        director = LLMDirector(api_key="test-key")
        result = director.recommend({"gini": 0.6, "crime_rate": 55, "average_satisfaction": 45.0, "food_supply": 80})

    assert len(result) == 1
    assert result[0]["action"] in LLMDirector.VALID_ACTIONS
