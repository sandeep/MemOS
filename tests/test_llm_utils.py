import pytest
from unittest.mock import patch
from src.llm_utils import call_llm

@patch("src.llm_utils.requests.post")
@patch.dict("os.environ", {"NVIDIA_API_KEY": "fake_key"})
def test_call_llm_raises_on_timeout(mock_post):
    mock_post.side_effect = Exception("Read timed out")
    with pytest.raises(RuntimeError, match="LLM Connection failed after 5 retries."):
        call_llm("test prompt", cache_dir="/tmp/test_cache")
