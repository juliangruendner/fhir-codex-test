FROM python:3.10-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY fhir_codex_check.py .
COPY codex-test-queries.json .

CMD [ "python", "fhir_codex_check.py"]
