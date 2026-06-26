import collections
import hashlib
import logging
import os
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

# injected from env file
SECRET_KEY = os.environ['DB_SECRET_KEY'].encode()
# assert on length, this guards against the key being missing if the injection fails, etc
assert len(SECRET_KEY) > 25, 'secret key either missing or too short'
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
    if check_excessive_failed_access(form_data.username):
        logging.warning(f'Access denied for user {form_data.username} - too many failed attempts')
        raise HTTPException(429, 'Too many invalid attempts')

    user = session.exec(
        select(User).where(
            User.username == form_data.username
        )
    ).one_or_none()

    if not user:
        register_failed_access(form_data.username)
        logger.warning(f"Token issue failed for user {form_data.username} - user does not exist")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(user, form_data.password):
        register_failed_access(form_data.username)
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
    except (jwt.InvalidTokenError, TypeError):
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


FAILED_ACCESS: dict[str, collections.deque] = {}
# allow max of 20 attemts over an hour
MAX_ACCESS_ATTEMPTS = 20
MAX_ACCESS_TIMESPAN_MINUTES = 60

def register_failed_access(username: str):
    if username not in FAILED_ACCESS:
        FAILED_ACCESS[username] = collections.deque([], MAX_ACCESS_ATTEMPTS)
    # append to the right, so oldest attempt on left at index [0]
    FAILED_ACCESS[username].append(datetime.now(timezone.utc))


def check_excessive_failed_access(username: str):
    # if no failed access attempts so far
    if username not in FAILED_ACCESS:
        return False
    # if not at max attempts
    if len(FAILED_ACCESS[username]) < MAX_ACCESS_ATTEMPTS:
        return False
    # if first attempt not in the 1 hour span
    earliest_allowed_time = datetime.now(timezone.utc) - timedelta(minutes=MAX_ACCESS_TIMESPAN_MINUTES)
    if FAILED_ACCESS[username][0] <= earliest_allowed_time:
        return False
    return True

