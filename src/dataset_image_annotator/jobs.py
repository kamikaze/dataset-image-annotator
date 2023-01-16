import argparse
import asyncio
import contextlib
import logging.config

from fastapi_users.exceptions import UserAlreadyExists

from dataset_image_annotator.api.users import get_user_db, get_user_manager
from dataset_image_annotator.api.v1.schemas import UserCreate
from dataset_image_annotator.conf import settings


logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': settings.logging_format,
        },
    },
    'handlers': {
        'default': {
            'level': settings.logging_level,
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'standard',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': settings.logging_level,
            'propagate': True,
        }
    }
})

logger = logging.getLogger(__name__)


async def create_superuser():
    get_async_session_context = contextlib.asynccontextmanager(get_async_session)
    get_user_db_context = contextlib.asynccontextmanager(get_user_db)
    get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)

    try:
        async with get_async_session_context() as session:
            async with get_user_db_context(session) as user_db:
                async with get_user_manager_context(user_db) as user_manager:
                    await user_manager.create(
                        UserCreate(
                            email=settings.bootstrap_user_email,
                            password=settings.bootstrap_user_password.get_secret_value(),
                            is_superuser=True
                        )
                    )
                    logger.info(f'User created: {settings.bootstrap_user_email}')
    except UserAlreadyExists:
        logger.warning(f'User already exists: {settings.bootstrap_user_email}')


def get_parsed_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--job', type=str)

    args, args_other = parser.parse_known_args()

    return args


async def foo():
    logger.info('Foo')


async def bar():
    logger.info('Bar')


async def main():
    args = get_parsed_args()
    job_mapping = {
        'foo': foo,
        'bar': bar,
    }

    try:
        await job_mapping[args.job]()
    except KeyError:
        logger.error(f'Unknown job: "{args.job}"')


if __name__ == '__main__':
    asyncio.run(main())
