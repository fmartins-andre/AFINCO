FROM python:3.9-alpine3.22

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

RUN apk --update --no-cache add \
    build-base openldap-dev cyrus-sasl-dev \
    python3-dev mariadb-dev mariadb-client \
    && rm -rf /var/cache/apk/*

RUN pip install --no-cache-dir uv

COPY app pyproject.toml uv.lock ./

RUN mkdir -p media /var/backups

RUN uv export --format requirements-txt > requirements.txt && uv pip install -r requirements.txt --system

CMD ["uv", "run", "gunicorn", "contabil.wsgi", "-b", "0.0.0.0:8008" ]

EXPOSE 8008
