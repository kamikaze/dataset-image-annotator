import logging

import sqlalchemy as sa
from fastapi_users.exceptions import UserAlreadyExists
from passlib import pwd

from dataset_image_annotator.api.users import create_user
from dataset_image_annotator.api.v1.schemas import UserCreate
from dataset_image_annotator.conf import settings
from dataset_image_annotator.db import database
from dataset_image_annotator.db.models import User

logger = logging.getLogger()


async def bootstrap_db():
    user_count = await database.fetch_val(sa.select([sa.func.count(User.id)]))

    if user_count == 0:
        logger.warning('No users in database')

        if settings.bootstrap_user_email:
            logger.info('Bootstrapping a user in database')
            password = pwd.genword(length=16, entropy=52)

            try:
                await create_user(
                    UserCreate(
                        email=settings.bootstrap_user_email,
                        password=password,
                        is_superuser=True,
                        is_active=True,
                        is_verified=True
                    )
                )
                logger.debug(f'Bootstrap user: {settings.bootstrap_user_email} / {password}')
            except UserAlreadyExists:
                logger.warning(f'User {settings.bootstrap_user_email} already exist')
