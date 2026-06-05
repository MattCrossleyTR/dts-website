import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import select

from .db import DBSessionDep
from .db.models import User

logger = logging.getLogger(__name__)
security = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter(tags=["auth"])

# randomly generated on boot, so if backend crashes users get logged out, and so I don't have to manage
# injecting secrets from a secure source
SECRET_KEY = secrets.token_bytes(32)
ALGORITHM = "HS256"
TOKEN_EXPIRY_MINUTES = 60
# generated with openssl
PEPPER = '9aa8fc47a0fe5fbdb4b089fe4a15006fc75ee36e0de2bb5f40cd29820d8823cd'


def create_token(user: User):
    to_encode = {
        'sub': str(user.id),
        'username': user.username,
        'admin': user.admin
    }
    to_encode["exp"] = datetime.now(timezone.utc) + timedelta(
        minutes=TOKEN_EXPIRY_MINUTES
    )
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def hash_password(password: str, salt: bytes | None = None):
    if salt is None:
        salt = secrets.token_bytes(32)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode() + PEPPER.encode(), salt, 600_000)
    return salt + hashed


def verify_password(user: User, password: str):
    salt = user.password[:32]
    return hash_password(password, salt) == user.password


@router.post("/token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: DBSessionDep
):
    user = session.exec(
        select(User).where(
            User.username == form_data.username
        )
    ).one_or_none()

    if not user:
        logger.warning(f"Token issue failed for user {form_data.username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(user, form_data.password):
        logger.warning(f'invalid password for user {user.id}')
        raise HTTPException(401, 'Invalid credentials')

    return create_token(user)


async def auth_check(
    token: Annotated[str, Depends(security)],
    session: DBSessionDep,
) -> User:
    creds_exception = HTTPException(
        401, "Could not validate credentials", headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = UUID(payload.get("sub"))
        if not user_id:
            raise creds_exception
    except jwt.InvalidTokenError:
        logging.warning("invalid token submitted for auth")
        raise creds_exception

    user = session.exec(select(User).where(User.id == user_id)).one_or_none()
    if not user:
        logger.warning(
            f"Authentication failed for user {user_id} - valid token but user doesn't exist"
        )
        raise creds_exception

    logger.info(f"User {user_id} authenticated successfully")
    return user


AuthCheckDep = Annotated[User, Depends(auth_check)]
