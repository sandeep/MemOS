FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir requests presidio-analyzer presidio-anonymizer rlms openai "pydantic>=2.0.0"
RUN python -m spacy download en_core_web_lg

# Copy pipeline files
COPY src/ /app/src/
COPY specs/ /app/specs/

# Set Python path
ENV PYTHONPATH=/app

# Default command
CMD ["python", "src/extractor.py", "specs/test-case-conversation.json"]
