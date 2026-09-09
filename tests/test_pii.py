import pytest
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

def test_presidio_redaction():
    text = "My phone number is 212-555-5555 and my email is test@example.com."
    
    analyzer = AnalyzerEngine()
    anonymizer = AnonymizerEngine()
    
    results = analyzer.analyze(text=text, entities=["PHONE_NUMBER", "EMAIL_ADDRESS"], language='en')
    anonymized_result = anonymizer.anonymize(text=text, analyzer_results=results)
    
    assert "212-555-5555" not in anonymized_result.text
    assert "test@example.com" not in anonymized_result.text
    assert "<PHONE_NUMBER>" in anonymized_result.text
    assert "<EMAIL_ADDRESS>" in anonymized_result.text
