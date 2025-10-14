from fastapi import FastAPI
from ex3.models.models import User
from ex3.models.models import FeedBack

app = FastAPI()

lst = []

user = User(name="John Doe", id=1)

@app.get("/users", response_model=User)
async def users():
    return user

@app.post("/feedback")
async def feedback(feedback: FeedBack):
    lst.append({"name": feedback.name, "comments": feedback.message})
    return f"Feedback received. Thank you, {feedback.name}!"