import httpx
from fastapi import Depends, Header, HTTPException
from pydantic import BaseModel

import config


class User(BaseModel):
    id: str
    email: str


async def get_auth_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(401, "Access denied")
    return authorization.split()[-1]


async def get_user(token: str = Depends(get_auth_token)):
    response = await httpx.get(
        "https://login.yandex.ru/info", headers={"Authorization": f"OAuth {token}"}
    )
    response_data = response.json()
    email = response_data["default_email"]
    if email not in config.USERS:
        raise HTTPException(403, "User not listed in config file.")
    return User(id=response_data["id"], email=response_data["default_email"])
