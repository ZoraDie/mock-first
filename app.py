from fastapi import FastAPI, HTTPException, Header
from prometheus_client import Counter, Histogram
import time

from generate_token import generate_token

app = FastAPI()

users = {}
tokens = {}

# Метрики
REQUEST_COUNT = Counter("api_requests", "Number of API requests", ["endpoint"])
RESPONSE_TIME = Histogram("api_response_time", "API response time", ["endpoint"])

@app.post("/register")
def register(username: str, password: str):
    users[username] = password
    REQUEST_COUNT.labels(endpoint="register").inc()
    return {"message": "User registered successfully"}

@app.post("/login")
def login(username: str, password: str):
    if username in users and users[username] == password:
        token = generate_token(username)
        tokens[token] = username
        REQUEST_COUNT.labels(endpoint="login").inc()
        return {"token": token}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/user")
def get_user(authorization: str = Header(None)):
    start_time = time.time()
    REQUEST_COUNT.labels(endpoint="user").inc()

    if authorization and authorization in tokens:
        duration = time.time() - start_time
        RESPONSE_TIME.labels(endpoint="user").observe(duration)
        return {"username": tokens[authorization], "full_name": "John Doe"}

    raise HTTPException(status_code=401, detail="Invalid token")