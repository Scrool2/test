import re
from fastapi import FastAPI, Request, HTTPException


app = FastAPI()


def check_headers(headers: Request.headers):
    if "User-Agent" not in headers:
        raise HTTPException(status_code=400, detail="The User-Agent header not found!")

    if "Accept-Language" not in headers:
        raise HTTPException(status_code=400, detail="The Accept-Language header not found!")

    pattern = r"(?i:(?:\*|[a-z\-]{2,5})(?:;q=\d\.\d)?,)+(?:\*|[a-z\-]{2,5})(?:;q=\d\.\d)?"
    if not re.fullmatch(pattern, headers["Accept-Language"]):
        raise HTTPException(
            status_code=400,
            detail="The Accept-Language header is not in the correct format"
        )


@app.get("/headers")
async def get_headers(request: Request) -> dict:
    check_headers(request.headers)
    return {
        "User-Agent" : request.headers["user-agent"],
        "Accept-Language": request.headers["accept-language"]
    }