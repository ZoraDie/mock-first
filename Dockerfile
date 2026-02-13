FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/app.py .

COPY app/generate_token.py .

EXPOSE 8000

CMD ["python", "app.py"]