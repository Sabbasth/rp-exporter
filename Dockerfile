FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src /app/src
COPY setup.py .

EXPOSE 8000

ENTRYPOINT ["python", "/app/src/app.py"]
CMD ["--console-url", "http://redpanda-console:8080", "--port", "8000"]
