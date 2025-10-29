from pydantic import BaseModel

class Cred(BaseModel):
    email: str
    password: str
