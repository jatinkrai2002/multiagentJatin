# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY shared_protocol.py /app/
COPY agent_server.py /app/
COPY agents/ /app/agents/
COPY orchestrator.py /app/

# No external dependencies; using stdlib only
RUN useradd -m runner && chown -R runner:runner /app
USER runner

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

CMD ["python", "orchestrator.py"]
