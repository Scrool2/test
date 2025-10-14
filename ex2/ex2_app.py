from fastapi import FastAPI
from ex2.models.models import User

app = FastAPI()

user = User(name="John Doe", id=1)

@app.get("/users", response_model=User)
async def users():
    return user