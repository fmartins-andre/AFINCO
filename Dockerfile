FROM python:3.9-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY --from=ghcr.io/astral-sh/uv:0.9.9 /uv /uvx /bin/

WORKDIR /usr/src/app

RUN apk --update --no-cache add \
    build-base \
    openldap-dev \
    mariadb-connector-c-dev \
    && rm -rf /var/cache/apk/*

COPY app pyproject.toml uv.lock ./

RUN mkdir -p media /var/backups

RUN uv export --format requirements-txt > requirements.txt && uv pip install -r requirements.txt --system

RUN  python -c "import django; print(f'Django version: {django.__version__}')"

CMD ["python", "gunicorn", "contabil.wsgi", "-b", "0.0.0.0:8008" ]

EXPOSE 8008
