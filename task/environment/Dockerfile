FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb

# Task runtime deps + verifier deps, baked at build time (pinned)
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
    && pip install --no-cache-dir --break-system-packages \
        numpy==2.2.6 \
        pytest==8.4.1 \
        pytest-json-ctrf==0.3.5 \
    && apt-get purge -y gcc \
    && rm -rf /var/lib/apt/lists/*

# Pre-create the artifact output directory so the agent can write there
RUN mkdir -p /app

# Input data: trajectory file
COPY data /app/data

WORKDIR /app
