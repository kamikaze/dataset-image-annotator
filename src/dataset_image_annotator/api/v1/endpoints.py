import logging
import uuid
from functools import wraps
from inspect import signature
from typing import Sequence

from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from fastapi.responses import ORJSONResponse
from fastapi_pagination import Page
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend, JWTStrategy, CookieTransport
from pydantic import Json
from python3_commons.db import connect_to_db
from sqlalchemy.ext.asyncio import AsyncSession

from dataset_image_annotator import core
from dataset_image_annotator.api import users
from dataset_image_annotator.api.users import get_user_manager
from dataset_image_annotator.api.v1.schemas import (
    UserCreate, UserUpdate, UserItem, UserGroup, UserRead, ImageSampleItem
)
from dataset_image_annotator.conf import settings
from dataset_image_annotator.core import upload_handler
from dataset_image_annotator.db.models import User
from dataset_image_annotator.db.user_db_helpers import get_async_session

logger = logging.getLogger(__name__)
router = APIRouter()
cookie_transport = CookieTransport(cookie_max_age=3600)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.auth_secret.get_secret_value(), lifetime_seconds=3600)


auth_backend = AuthenticationBackend(name='cluserauth', transport=cookie_transport, get_strategy=get_jwt_strategy)
auth_backends = [auth_backend, ]
fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    auth_backends
)
get_current_user = fastapi_users.current_user(active=True)
get_current_superuser = fastapi_users.current_user(active=True, superuser=True)
auth_router = fastapi_users.get_auth_router(auth_backend, requires_verification=True)
users_router = fastapi_users.get_users_router(UserRead, UserUpdate, requires_verification=True)


def _handle_exceptions_helper(status_code, *args):
    if args:
        raise HTTPException(status_code=status_code, detail=args[0])
    else:
        raise HTTPException(status_code=status_code)


def handle_exceptions(func):
    signature(func)

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except PermissionError as e:
            return _handle_exceptions_helper(status.HTTP_401_UNAUTHORIZED, *e.args)
        except LookupError as e:
            return _handle_exceptions_helper(status.HTTP_404_NOT_FOUND, *e.args)
        except ValueError as e:
            return _handle_exceptions_helper(status.HTTP_400_BAD_REQUEST, *e.args)

    return wrapper


@router.get('/users', response_class=ORJSONResponse, tags=['Admin'])
@handle_exceptions
async def get_users(search: Json | None = None, order_by: str | None = None,
                    user=Depends(get_current_superuser),
                    session: AsyncSession = Depends(get_async_session)) -> Page[UserItem]:
    return await core.get_users(session, search, order_by)


@router.post('/users', response_class=ORJSONResponse, tags=['Admin'])
@handle_exceptions
async def create_user(new_user: UserCreate, user=Depends(get_current_superuser)) -> UserItem:
    return await users.create_user(new_user)


@router.get('/user-groups', response_class=ORJSONResponse, tags=['Admin'])
@handle_exceptions
async def get_user_groups(search: Json | None = None, order_by: str | None = None,
                          user=Depends(get_current_user),
                          session: AsyncSession = Depends(get_async_session)) -> Sequence[UserGroup]:
    return await core.get_user_groups(session, search, order_by)


@router.post('/raw-file', response_class=ORJSONResponse, tags=['Admin'])
@handle_exceptions
async def upload_raw_file(image_file: UploadFile = File(...), user=Depends(get_current_superuser),
                          session: AsyncSession = Depends(get_async_session)) -> bool:
    if not image_file.filename:
        raise HTTPException(status_code=400, detail='Missing file')

    try:
        response = await upload_handler.handle_raw_file(session, image_file)
    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e))

    return response


@router.get('/image-samples', response_class=ORJSONResponse, tags=['Images'])
@handle_exceptions
async def get_image_samples(session: AsyncSession = Depends(get_async_session), search: Json | None = None,
                            order_by: str | None = None) -> Page[ImageSampleItem]:
    return await core.get_image_samples(session, search, order_by)
