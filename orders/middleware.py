import os
import jwt
from urllib.parse import parse_qs
from django.db import close_old_connections
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.authentication import JWTAuthentication

User = get_user_model()


@database_sync_to_async
def close_connections():
    close_old_connections()


@database_sync_to_async
def get_user_from_id(user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        user = None
    return user


class JsonTokenAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        await close_connections()
        query_string = parse_qs(scope["query_string"].decode("utf-8"))
        token = query_string.get("token", [None])[0]
        if token:
            try:
                # Decode token
                payload = jwt.decode(token, api_settings.SIGNING_KEY, algorithms=[api_settings.ALGORITHM])
                user_id = payload.get("user_id")
                if user_id:
                    user = await get_user_from_id(user_id)
                    scope['user'] = user
                else:
                    scope['user'] = None
            except (InvalidToken, TokenError, jwt.DecodeError) as e:
                print(f"Failed to authenticate: {str(e)}")
                scope['user'] = None
        else:
            print("No token provided")
            scope['user'] = None

        return await self.inner(scope, receive, send)


JsonTokenAuthMiddlewareStack = lambda inner: JsonTokenAuthMiddleware(inner)
