# main.py
from fastapi import FastAPI, HTTPException, Form, UploadFile, File, Request, Response, Cookie, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import uuid
import time
import os
from typing import Optional

os.makedirs("static", exist_ok=True)

app = FastAPI()


class Movie(BaseModel):
    name: str
    director: str
    year: int
    rating: float

movies_db = [
    {"name": "Крестный отец", "director": "Фрэнсис Форд Коппола", "year": 1972, "rating": 9.2},
    {"name": "Побег из Шоушенка", "director": "Фрэнк Дарабонт", "year": 1994, "rating": 9.3},
    {"name": "Темный рыцарь", "director": "Кристофер Нолан", "year": 2008, "rating": 9.0},
]

sessions = {}
users_db = {"admin": "password"}


@app.get("/")
async def root():
    return {"message": "Сервер работает на порту 8165"}


@app.get("/study")
async def study():
    return {
        "name": "Московский Государственный Университет",
        "faculty": "Факультет Вычислительной Математики и Кибернетики",
        "year": 2024
    }


@app.get("/movietop/{film_name}")
async def get_movie(film_name: str):
    for movie in movies_db:
        if movie["name"].lower() == film_name.lower():
            return movie
    raise HTTPException(status_code=404, detail="Фильм не найден")


@app.get("/add_film")
async def add_film_form():
    return HTMLResponse("""
    <html>
        <body>
            <h2>Добавить новый фильм</h2>
            <form action="/add_film" method="post" enctype="multipart/form-data">
                <input type="text" name="name" placeholder="Название фильма" required><br><br>
                <input type="text" name="director" placeholder="Режиссер" required><br><br>
                <input type="number" name="year" placeholder="Год выпуска" required><br><br>
                <input type="number" step="0.1" name="rating" placeholder="Рейтинг" required><br><br>
                <input type="file" name="poster"><br><br>
                <button type="submit">Добавить фильм</button>
            </form>
        </body>
    </html>
    """)


@app.post("/add_film")
async def add_film(
        name: str = Form(...),
        director: str = Form(...),
        year: int = Form(...),
        rating: float = Form(...),
        poster: Optional[UploadFile] = None
):

    poster_url = None
    if poster:
        file_location = f"static/{poster.filename}"
        with open(file_location, "wb") as file_object:
            content = await poster.read()
            file_object.write(content)
        poster_url = f"/{file_location}"

    new_movie = {
        "name": name,
        "director": director,
        "year": year,
        "rating": rating,
        "poster": poster_url
    }

    movies_db.append(new_movie)
    return {"message": "Фильм добавлен", "movie": new_movie}


@app.post("/login")
async def login(response: Response, username: str = Form(...), password: str = Form(...)):
    if username in users_db and users_db[username] == password:
        session_token = str(uuid.uuid4())
        expire_time = time.time() + 120

        sessions[session_token] = {
            "username": username,
            "login_time": time.time(),
            "expire_time": expire_time
        }

        response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            max_age=120
        )
        return {"message": "Успешный вход"}

    raise HTTPException(status_code=401, detail="Неверные учетные данные")


def check_session(session_token: str = Cookie(None)):
    if not session_token or session_token not in sessions:
        raise HTTPException(status_code=401, detail="Не авторизован")

    session_data = sessions[session_token]
    if time.time() > session_data["expire_time"]:
        del sessions[session_token]
        raise HTTPException(status_code=401, detail="Сессия истекла")

    sessions[session_token]["expire_time"] = time.time() + 120
    return session_data


@app.get("/user")
async def get_user(session_data: dict = Depends(check_session)):
    return {
        "username": session_data["username"],
        "login_time": session_data["login_time"],
        "session_expires": session_data["expire_time"],
        "movies": movies_db
    }


def simple_jwt_encode(payload: dict) -> str:
    import base64
    import json
    payload_str = json.dumps(payload)
    return base64.b64encode(payload_str.encode()).decode()


def simple_jwt_decode(token: str) -> dict:
    import base64
    import json
    try:
        payload_str = base64.b64decode(token).decode()
        return json.loads(payload_str)
    except:
        return None


@app.post("/jwt_login")
async def jwt_login(username: str = Form(...), password: str = Form(...)):
    if username in users_db and users_db[username] == password:
        payload = {
            "username": username,
            "exp": time.time() + 120  # 2 минуты
        }
        token = simple_jwt_encode(payload)
        return {"access_token": token}

    raise HTTPException(status_code=401, detail="Неверные учетные данные")


@app.post("/add_film_secure")
async def add_film_secure(
        request: Request,
        name: str = Form(...),
        director: str = Form(...),
        year: int = Form(...),
        rating: float = Form(...)
):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Токен не предоставлен")

    token = auth_header.split(" ")[1]
    payload = simple_jwt_decode(token)

    if not payload or time.time() > payload.get("exp", 0):
        raise HTTPException(status_code=401, detail="Неверный или истекший токен")

    new_movie = {
        "name": name,
        "director": director,
        "year": year,
        "rating": rating
    }

    movies_db.append(new_movie)
    return {"message": "Фильм добавлен с JWT аутентификацией", "movie": new_movie}

