FROM python:3.14-alpine

WORKDIR /app

COPY requirements.txt .
RUN apk add --no-cache build-base && \
    pip install --no-cache-dir -r requirements.txt

COPY app/. .
COPY static/ /static/

USER nobody

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]