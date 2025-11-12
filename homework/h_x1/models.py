from pydantic import BaseModel

class Movietop(BaseModel):
    name: str
    id: int
    cost: int
    director: str

class MovieCreate(BaseModel):
    name: str
    director: str
    cost: int
    is_active: bool

class User(BaseModel):
    username: str
    password: str
