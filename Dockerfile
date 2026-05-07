FROM python:3.11-slim

RUN pip install fastmcp google-ads

WORKDIR /app

COPY server.py .

EXPOSE 8000

CMD ["python", "server.py"]
