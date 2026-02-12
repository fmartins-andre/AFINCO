# Use the official Python development container as base
FROM python:3.9-alpine3.22

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /workspace

# Install additional system dependencies
RUN apk --update --no-cache add bash curl git nodejs build-base openldap-dev cyrus-sasl-dev python3-dev mariadb-dev mariadb-client

RUN pip install --no-cache-dir uv

# set cmd to bash
CMD ["/bin/bash"]

# Set the default shell to bash
SHELL ["/bin/bash", "-c"]
