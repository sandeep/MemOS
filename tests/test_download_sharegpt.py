import io
import json
import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from src.download_sharegpt import stream_json_conversations, fetch_sharegpt_conversations


def test_stream_json_conversations_mock():
    mock_data = json.dumps([
        {
            "id": "conv_1",
            "conversations": [
                {"from": "human", "value": "Hello world"},
                {"from": "gpt", "value": "Hi there! How can I help you today?"}
            ]
        },
        {
            "id": "conv_2",
            "conversations": [
                {"from": "human", "value": "What is Python?"},
                {"from": "gpt", "value": "Python is a programming language."}
            ]
        },
        {
            "id": "conv_3",
            "conversations": [
                {"from": "human", "value": "Tell me a joke."},
                {"from": "gpt", "value": "Why did the chicken cross the road?"}
            ]
        }
    ]).encode("utf-8")

    stream = io.BytesIO(mock_data)
    results = stream_json_conversations(stream, max_count=2, chunk_size=16)

    assert len(results) == 2
    assert results[0]["id"] == "conv_1"
    assert len(results[0]["conversations"]) == 2
    assert results[0]["conversations"][0]["from"] == "human"
    assert results[1]["id"] == "conv_2"


def test_fetch_sharegpt_conversations_mock():
    mock_items = [
        {
            "id": f"conv_{i}",
            "conversations": [
                {"from": "human", "value": f"hello {i}"},
                {"from": "gpt", "value": f"response {i}"}
            ]
        }
        for i in range(5)
    ]
    mock_bytes = json.dumps(mock_items).encode("utf-8")

    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read = io.BytesIO(mock_bytes).read
    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
    mock_resp.__exit__ = MagicMock(return_value=None)

    with tempfile.TemporaryDirectory() as tmpdir:
        out_file = os.path.join(tmpdir, "subdir", "real_conversations.json")

        with patch("urllib.request.urlopen", return_value=mock_resp):
            saved_file = fetch_sharegpt_conversations(
                count=3,
                output_path=out_file,
                url="http://mock-url"
            )

        assert os.path.exists(saved_file)
        with open(saved_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert len(data) == 3
        assert data[0]["id"] == "conv_0"
        assert data[2]["id"] == "conv_2"


def test_is_valid_conversation():
    from src.download_sharegpt import is_valid_conversation

    # Valid multi-turn
    assert is_valid_conversation({
        "id": "1",
        "conversations": [
            {"from": "human", "value": "Hi"},
            {"from": "gpt", "value": "Hello"}
        ]
    })

    # Empty conversations list
    assert not is_valid_conversation({"id": "2", "conversations": []})

    # Single turn when min_turns=2
    assert not is_valid_conversation({
        "id": "3",
        "conversations": [{"from": "human", "value": "Hi"}]
    }, min_turns=2)

    # Missing ID
    assert not is_valid_conversation({
        "conversations": [{"from": "human", "value": "Hi"}, {"from": "gpt", "value": "Hello"}]
    })

    # Blank value
    assert not is_valid_conversation({
        "id": "4",
        "conversations": [
            {"from": "human", "value": "   "},
            {"from": "gpt", "value": "Hello"}
        ]
    })


def test_stream_filters_empty_conversations():
    mixed_data = json.dumps([
        {"id": "empty_1", "conversations": []},
        {
            "id": "valid_1",
            "conversations": [
                {"from": "human", "value": "Hello"},
                {"from": "gpt", "value": "World"}
            ]
        },
        {"id": "blank_val", "conversations": [{"from": "human", "value": ""}, {"from": "gpt", "value": ""}]},
        {
            "id": "valid_2",
            "conversations": [
                {"from": "human", "value": "Foo"},
                {"from": "gpt", "value": "Bar"}
            ]
        }
    ]).encode("utf-8")

    stream = io.BytesIO(mixed_data)
    results = stream_json_conversations(stream, max_count=2, min_turns=2)

    assert len(results) == 2
    assert results[0]["id"] == "valid_1"
    assert results[1]["id"] == "valid_2"

