FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV MODULE_NAME=app.main
ENV VARIABLE_NAME=app

CMD ["sh", "-c", "if [ \"$RUN_WORKER\" = '1' ]; then celery -A app.chatroom.tasks.celery_app worker --loglevel=info; else uvicorn app.main:app --host 0.0.0.0 --port 8000; fi"] 