from fastapi.security import OAuth2PasswordRequestForm
import pytest
from fastapi.exceptions import HTTPException
from mocks import MockSessionOrTable
from src.auth import auth_check, ALGORITHM, SECRET_KEY, login
import jwt
from uuid import uuid4


class TestCheckAuth:
    @pytest.mark.asyncio
    async def test_raises_error_if_unauthenticated(self):
        with pytest.raises(HTTPException):
            await auth_check("abcdef", session=MockSessionOrTable())


    @pytest.mark.asyncio
    async def test_raises_error_for_invalid_token_signing(self):
        token = jwt.encode(
            {"sub": "id123", "exp": 999999999999999}, "abc" * 12, algorithm=ALGORITHM
        )
        with pytest.raises(HTTPException):
            await auth_check(token, session=MockSessionOrTable())


    @pytest.mark.asyncio
    async def test_raises_error_for_missing_user_id(self):
        token = jwt.encode({"exp": 999999999999999}, SECRET_KEY, algorithm=ALGORITHM)
        with pytest.raises(HTTPException):
            await auth_check(token, session=MockSessionOrTable())


    @pytest.mark.asyncio
    async def test_raises_error_if_user_does_not_exist(self):
        token = jwt.encode({'sub': str(uuid4()), "exp": 999999999999999}, SECRET_KEY, algorithm=ALGORITHM)
        with pytest.raises(HTTPException):
            await auth_check(token, session=MockSessionOrTable())


class TestLogin:
    @pytest.mark.asyncio
    async def test_blocks_excessive_failed_requests(self):
        for _ in range(20):
            with pytest.raises(HTTPException):
                await login(OAuth2PasswordRequestForm(username='abc123', password='abc123'), session=MockSessionOrTable())

        # now make one additional request
        with pytest.raises(HTTPException, match='429: Too many invalid attempts'):
            await login(OAuth2PasswordRequestForm(username='abc123', password='abc123'), session=MockSessionOrTable())

        # but this should not block other users
        with pytest.raises(HTTPException, match='401: Invalid credentials'):
            await login(OAuth2PasswordRequestForm(username='def567', password='def567'), session=MockSessionOrTable())