import os
import json
from unittest.mock import patch, MagicMock
from src.extractor_rlms import extract

@patch('src.extractor_rlms.RLM')
def test_fallback_handles_0_byte_file(mock_rlm_class, tmp_path):
    mock_rlm_instance = mock_rlm_class.return_value
    mock_response = MagicMock()
    mock_response.response = '{"fallback": "success"}'
    mock_rlm_instance.completion.return_value = mock_response
    
    transcript_file = tmp_path / "transcript.json"
    transcript_file.write_text('{}')
    output_file = tmp_path / "out.json"
    
    # Create a 0-byte file to simulate the previous crash state
    output_file.touch()
    assert os.path.getsize(output_file) == 0
    
    extract(str(transcript_file), None, str(output_file))
    
    assert output_file.exists()
    assert output_file.read_text() == '{"fallback": "success"}'

@patch('src.extractor_rlms.RLM')
def test_fallback_handles_string_cast_fallback(mock_rlm_class, tmp_path):
    mock_rlm_instance = mock_rlm_class.return_value
    mock_response = MagicMock()
    # Simulate a response that throws an attribute error when accessing response
    del mock_response.response 
    mock_response.__str__.return_value = '{"fallback": "string_cast"}'
    mock_rlm_instance.completion.return_value = mock_response
    
    transcript_file = tmp_path / "transcript.json"
    transcript_file.write_text('{}')
    output_file = tmp_path / "out2.json"
    
    extract(str(transcript_file), None, str(output_file))
    
    assert output_file.exists()
    assert output_file.read_text() == '{"fallback": "string_cast"}'
