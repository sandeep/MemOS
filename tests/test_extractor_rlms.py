import os
from unittest.mock import patch
from src.extractor_rlms import extract

@patch('src.extractor_rlms.RLM')
def test_extract_saves_stdout_fallback(mock_rlm_class, tmp_path):
    mock_rlm_instance = mock_rlm_class.return_value
    mock_rlm_instance.completion.return_value = '{"fallback": "json"}'
    
    transcript_file = tmp_path / "transcript.json"
    transcript_file.write_text('{}')
    output_file = tmp_path / "out.json"
    
    extract(str(transcript_file), None, str(output_file))
    
    assert output_file.exists()
    assert output_file.read_text() == '{"fallback": "json"}'
