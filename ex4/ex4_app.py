from fastapi import FastAPI
from ex4.models.models import UserCreate

app = FastAPI()

@app.post("/create_user", response_model=UserCreate)
async def create_user(user: UserCreate):
    user_create = UserCreate(name = user.name, email = user.email, age = user.age, id_subscribes = user.id_subscribes)
    return user_create