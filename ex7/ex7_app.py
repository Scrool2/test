from fastapi import FastAPI
from pydantic import BaseModel
from ex7.models.models import Cred

app = FastAPI()

user = Cred(email="kr@gmail.com", password="12345")

@app.post("/login")
async def login(cred: Cred):
    if cred.email == user.email and cred.password == user.password:
        print("Hello")
    else:
        return Response(

        )