# Use the official Python Dev Container base image
FROM mcr.microsoft.com/devcontainers/python:3.11

# Install OS-level dependencies (no longer need libunwind-dev)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    pipx \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Set up pipx environment
ENV PIPX_BIN_DIR=/usr/local/bin
ENV PIPX_HOME=/usr/local/pipx
RUN pipx install poetry
