import asyncio
from typing import Optional, Dict

import resend
from fastapi import Depends, Request
from fastapi_users import BaseUserManager,IntegerIDMixin

from src.config import settings
from src.db import get_user_db
from src.entites.models import User

SECRET = settings.MANAGER_PASS
resend.api_key=settings.RESEND_API_KEY

class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.username} has registered.")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")

    async def on_after_forgot_password(
            self, user: User, token: str, request: Optional[Request] = None
    ) -> Dict:
        # noinspection PyTypeChecker
        params: resend.Emails.SendParams = {
            "from": "AccountingDA@petproject.website",
            "to": user.email,
            "subject": "Hello World",
            "html": f"<h1>Token for resent password:</h1>"
                    f"<p>{token}</p>",
        }
        email: resend.Email = resend.Emails.send(params)

        print(f"User {user.id} has forgot their password.\n"
              f"Reset token: {token}")
        return email

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)