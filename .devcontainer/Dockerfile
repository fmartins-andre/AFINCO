# Use the official Python development container as base
FROM mcr.microsoft.com/devcontainers/python:2-3.12-bullseye

# Install additional system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libsasl2-dev \
    libldap2-dev \
    libssl-dev \
    python3-dev \
    libmariadb-dev \
    mariadb-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

# Set the default shell to bash
SHELL ["/bin/bash", "-c"]