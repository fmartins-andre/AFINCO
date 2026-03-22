# Use the official Python development container as base
FROM python:3.9-alpine3.22 as base

# Install additional system dependencies
RUN apk --update --no-cache add \
    bash curl git nodejs build-base openssh-client sudo \
    openldap-dev cyrus-sasl-dev python3-dev \
    mariadb-dev mariadb-client

FROM base as devcontainer

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1
# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

ENV USER=dev
ENV GROUPNAME=$USER
ENV UID=1000
ENV GID=1000

RUN addgroup -g "$GID" "$GROUPNAME" \
    && adduser -D -G "$GROUPNAME" -u "$UID" -s "/bin/bash" $USER \
    && echo $USER ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USER \
    && chmod 0440 /etc/sudoers.d/$USER

USER $USER

WORKDIR /workspace

RUN pip install --no-cache-dir uv
