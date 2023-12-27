FROM python:3.11-slim as builder

ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip==23.*

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --user -r /app/requirements.txt

ENV PATH=/root/.local/bin:$PATH

FROM python:3.11-slim as runner

LABEL org.opencontainers.image.source https://github.com/kw90/felfel-taskwork-quality_metric_calculator

RUN apt update && apt install -y wget && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /root/.local /root/.local

COPY quality_metric_calculator /app/quality_metric_calculator
COPY docker-entrypoint.sh /app/docker-entrypoint.sh

FROM builder as tester

WORKDIR /app

COPY --from=builder /root/.local /root/.local

COPY requirements-test.txt /app/requirements-test.txt
COPY requirements.txt /app/requirements.txt

RUN pip install --user -r /app/requirements-test.txt -r /app/requirements.txt

COPY quality_metric_calculator /app/quality_metric_calculator
COPY tests /app/tests
COPY pyproject.toml /app/
