FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir pymysql==1.1.1

COPY rd_document.py rd_document.sql ./

ENTRYPOINT ["python", "rd_document.py", "--saida", "/app/saida"]
