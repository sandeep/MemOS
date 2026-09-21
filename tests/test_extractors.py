import os
import sys
import json
from unittest.mock import MagicMock, patch
import pytest

# Ensure src is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

sys.modules.setdefault("rlm", MagicMock())
import extractor
import extractor_rlms


@pytest.fixture
def sample_conv_file(tmp_path):
    conv_file = tmp_path / "conversation.json"
    conv_file.write_text(json.dumps([{"role": "user", "text": "Hello world"}]))
    return str(conv_file)


def test_extractor_default_output(tmp_path, monkeypatch, sample_conv_file):
    monkeypatch.chdir(tmp_path)
    with patch("extractor.call_llm", return_value='{"semantic_memory": {"nodes": [], "edges": []}}'):
        extractor.extract_rlm(sample_conv_file)
        assert os.path.exists("output.json")
        with open("output.json", "r") as f:
            data = json.load(f)
            assert "semantic_memory" in data


def test_extractor_dynamic_output(tmp_path, monkeypatch, sample_conv_file):
    monkeypatch.chdir(tmp_path)
    custom_output = str(tmp_path / "custom_output.json")
    with patch("extractor.call_llm", return_value='{"semantic_memory": {"nodes": ["node1"], "edges": []}}'):
        extractor.extract_rlm(sample_conv_file, custom_output)
        assert os.path.exists(custom_output)
        assert not os.path.exists("output.json")
        with open(custom_output, "r") as f:
            data = json.load(f)
            assert data["semantic_memory"]["nodes"] == ["node1"]


def test_extractor_nested_directory_creation(tmp_path, monkeypatch, sample_conv_file):
    monkeypatch.chdir(tmp_path)
    nested_output = str(tmp_path / "nested" / "dir" / "custom.json")
    with patch("extractor.call_llm", return_value='{"semantic_memory": {"nodes": [], "edges": []}}'):
        extractor.extract_rlm(sample_conv_file, nested_output)
        assert os.path.exists(nested_output)


def test_extractor_rlms_dynamic_output_default_prompt(tmp_path, monkeypatch, sample_conv_file):
    monkeypatch.chdir(tmp_path)
    mock_rlm_instance = MagicMock()
    custom_output = "data/working/evaluations/test/kg_rlms.json"
    
    with patch("extractor_rlms.RLM", return_value=mock_rlm_instance):
        extractor_rlms.extract(sample_conv_file, prompt_file=None, output_file=custom_output)
        
        mock_rlm_instance.completion.assert_called_once()
        prompt_arg = mock_rlm_instance.completion.call_args[0][0]
        assert f"'{custom_output}'" in prompt_arg
        assert "'output_rlms.json'" not in prompt_arg


def test_extractor_rlms_dynamic_output_with_prompt_file(tmp_path, monkeypatch, sample_conv_file):
    monkeypatch.chdir(tmp_path)
    mock_prompt_file = tmp_path / "prompt.txt"
    mock_prompt_file.write_text("Extract KG and save to `output_propositional_kg.json` checkpoint.")
    
    mock_rlm_instance = MagicMock()
    custom_output = "data/working/evaluations/test/kg_prop.json"
    
    with patch("extractor_rlms.RLM", return_value=mock_rlm_instance):
        extractor_rlms.extract(sample_conv_file, prompt_file=str(mock_prompt_file), output_file=custom_output)
        
        mock_rlm_instance.completion.assert_called_once()
        prompt_arg = mock_rlm_instance.completion.call_args[0][0]
        assert custom_output in prompt_arg
        assert "output_propositional_kg.json" not in prompt_arg
