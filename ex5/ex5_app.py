from fastapi import FastAPI
from ex4.models.models import LoginUser

app = FastAPI()

@app.post("/login")
async def login(login_user: LoginUser):

    return user_create

@app.get("/user")
async def get_user():

    return user_create