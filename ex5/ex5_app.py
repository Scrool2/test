from fastapi import FastAPI, Cookie, HTTPException
from pydantic import BaseModel
from fastapi import Response

# Предполагается, что у вас есть модель LoginUser в ex5.models.models
from ex5.models.models import LoginUser

app = FastAPI()

u = LoginUser(email="kr@gmail.com", password="12345")

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/login")
async def login(user: LoginUser):
    if user.email == u.email and user.password == u.password:
        response = Response(
            content='{"message": "Logged in successfully"}',
            media_type="application/json"
        )
        response.set_cookie(
            key="session_token",
            value="gha443dcb5",
            httponly=True
        )
        return response
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/user")
async def get_user(session_token: str = Cookie(None)):
    if session_token is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if session_token != "gha443dcb5":
        raise HTTPException(status_code=401, detail="Unauthorized")

    return u