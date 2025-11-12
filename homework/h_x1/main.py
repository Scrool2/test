from fastapi import FastAPI, HTTPException, Request, Form, File, UploadFile, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import jwt
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional


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

app = FastAPI()
templates = Jinja2Templates(directory="homework/templates")

app.mount("/static", StaticFiles(directory="C:\\Users\\kNikita\\PycharmProjects\\test\\homework\\h_x1"), name="static")

movies_data = {
    "avatar": Movietop(name="Avatar", id=1, cost=237000000, director="James Cameron"),
    "avengers": Movietop(name="Avengers: Endgame", id=2, cost=356000000, director="Anthony Russo"),
    "titanic": Movietop(name="Titanic", id=3, cost=200000000, director="James Cameron"),
    "starwars": Movietop(name="Star Wars: The Force Awakens", id=4, cost=245000000, director="J.J. Abrams"),
    "jurassic": Movietop(name="Jurassic World", id=5, cost=150000000, director="Colin Trevorrow"),
    "frozen": Movietop(name="Frozen II", id=6, cost=150000000, director="Chris Buck"),
    "lionking": Movietop(name="The Lion King", id=7, cost=260000000, director="Jon Favreau"),
    "joker": Movietop(name="Joker", id=8, cost=55000000, director="Todd Phillips"),
    "blackpanther": Movietop(name="Black Panther", id=9, cost=200000000, director="Ryan Coogler"),
    "harrypotter": Movietop(name="Harry Potter and the Deathly Hallows", id=10, cost=250000000, director="David Yates")
}

sessions: Dict[str, dict] = {}
users_db = {"admin": "password123"}
SECRET_KEY = "secret-key"
security = HTTPBearer()


def create_jwt_token(data: dict):
    expiration = datetime.utcnow() + timedelta(minutes=30)
    data.update({"exp": expiration})
    token = jwt.encode(data, SECRET_KEY, algorithm="HS256")
    return token

def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/study", response_class=HTMLResponse)
async def study(request: Request):
    return """
        <html>
            <head>Title</head>
            <body>
                <p>БГИТУ</p>
                <img src="/static/images/bgitu.jpg">
            </body>
        </html>
    """

@app.get("/movietop/{movie_name}")
async def get_movie(movie_name: str):
    movie = movies_data.get(movie_name.lower())
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

@app.get("/add_film", response_class=HTMLResponse)
async def add_film_form(request: Request):
    return templates.TemplateResponse("add_film.html", {"request": request})

@app.post("/add_film")
async def add_film(
        name: str = Form(...),
        director: str = Form(...),
        cost: int = Form(...),
        is_active: bool = Form(False),
        description: Optional[UploadFile] = File(None),
        cover: Optional[UploadFile] = File(None)
):
    file_info = {}
    if description:
        description_content = await description.read()
        file_info["description"] = f"File size: {len(description_content)} bytes"

    if cover:
        cover_content = await cover.read()
        file_info["cover"] = f"File size: {len(cover_content)} bytes"

    new_movie = Movietop(name=name, director=director, cost=cost, id=len(movies_data)+1)
    movies_data[new_movie.name.lower().replace(" ", "")] = new_movie

    return {"message": "Film added successfully", "film": new_movie}

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(
        username: str = Form(...),
        password: str = Form(...)
):
    if username in users_db and users_db[username] == password:
        session_token = str(uuid.uuid4())
        sessions[session_token] = {
            "username": username,
            "login_time": datetime.now(),
            "last_access": datetime.now()
        }

        response = JSONResponse({"message": "Login successful"})
        response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            max_age=120
        )
        return response
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/user")
async def get_user(request: Request):
    session_token = request.cookies.get("session_token")

    if not session_token or session_token not in sessions:
        return {"message": "Unauthorized"}

    session_data = sessions[session_token]
    current_time = datetime.now()

    if (current_time - session_data["last_access"]).total_seconds() > 120:
        del sessions[session_token]
        return {"message": "Unauthorized"}

    sessions[session_token]["last_access"] = current_time

    user_info = {
        "username": session_data["username"],
        "login_time": session_data["login_time"],
        "last_access": current_time,
        "movies": [movie.dict() for movie in movies_data.values()]
    }

    return user_info

@app.post("/jwt/login")
async def jwt_login(user: User):
    if user.username in users_db and users_db[user.username] == user.password:
        token = create_jwt_token({"sub": user.username})
        return {"access_token": token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/jwt/add_film")
async def jwt_add_film(
        film: MovieCreate,
        credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_jwt_token(token)

    new_movie = Movietop(
        name=film.name,
        director=film.director,
        cost=film.cost,
        id=len(movies_data) + 1
    )

    movies_data[new_movie.name.lower().replace(" ", "")] = new_movie

    return {"message": "Film added successfully", "film": new_movie}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8165, reload=True)