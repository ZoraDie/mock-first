from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from prometheus_client import Counter, Histogram
import time
from generate_token import generate_token
import uvicorn


app = FastAPI()

users = {}
tokens = {}

# Метрики
REQUEST_COUNT = Counter("api_requests", "Number of API requests", ["endpoint"])
RESPONSE_TIME = Histogram("api_response_time", "API response time", ["endpoint"])

class UserIn(BaseModel):
    username: str
    password: str

@app.post("/register")
def register(user: UserIn):
    users[user.username] = user.password
    REQUEST_COUNT.labels(endpoint="register").inc()
    return {"message": "User registered successfully"}

@app.post("/login")
def login(user: UserIn):
    if user.username in users and users[user.username] == user.password:
        token = generate_token(user.username)
        tokens[token] = user.username
        REQUEST_COUNT.labels(endpoint="login").inc()
        return {"token": token}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/user")
def get_user(authorization: str = Header(None)):
    start_time = time.time()
    REQUEST_COUNT.labels(endpoint="user").inc()

    if authorization:
        # Поддерживаем "Bearer <token>" и просто "<token>"
        token = authorization.split()[-1]
        if token in tokens:
            duration = time.time() - start_time
            RESPONSE_TIME.labels(endpoint="user").observe(duration)
            return {"username": tokens[token], "full_name": "John Doe"}

    raise HTTPException(status_code=401, detail="Invalid token")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
