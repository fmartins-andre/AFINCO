FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir pymysql==1.1.1

COPY rd_document.py terminal.py rd_document.sql config.exemplo.ini ./

# config.ini, relatorio.log e os TXT ficam no volume /dados
ENTRYPOINT ["python", "terminal.py", "--config", "/dados/config.ini"]
