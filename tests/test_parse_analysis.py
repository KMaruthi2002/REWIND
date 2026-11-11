import pytest

from src.pipeline.meta_client import parse_analysis_text


def test_parses_json_wrapped_in_code_fence():
    text = 'Here you go:\n```json\n{"damage_type": "impact", "reconstruction": {"narrative": "x"}}\n```'
    result = parse_analysis_text(text)
    assert result["reconstruction"]["narrative"] == "x"


def test_non_object_fields_are_coerced_to_empty_dict():
    text = '{"reconstruction": "a plain string", "parameters": [1, 2]}'
    result = parse_analysis_text(text)
    assert result["reconstruction"] == {}
    assert result["parameters"] == {}
    assert result.get("reconstruction", {}).get("narrative") is None


@pytest.mark.parametrize("text", ["", "no json here", '{"truncated": ', "{not json}"])
def test_unparseable_output_raises(text):
    with pytest.raises(ValueError):
        parse_analysis_text(text)
