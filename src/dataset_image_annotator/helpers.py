import asyncio
import datetime
import logging

from asyncpg import CannotConnectNowError

from dataset_image_annotator.conf import settings

logger = logging.getLogger(__name__)


def date_from_string(string: str, fmt: str = '%d.%m.%Y') -> datetime.date:
    try:
        return datetime.datetime.strptime(string, fmt).date()
    except ValueError:
        return datetime.date.fromisoformat(string)


def datetime_from_string(string: str) -> datetime.datetime:
    try:
        return datetime.datetime.strptime(string, '%d.%m.%Y %H:%M:%S')
    except ValueError:
        return datetime.datetime.fromisoformat(string)


def date_range(start_date, end_date):
    for n in range(int((end_date - start_date).days + 1)):
        yield start_date + datetime.timedelta(days=n)


async def connect_to_db(database):
    logger.info('Waiting for services')
    logger.debug(f'DB_DSN: {settings.db_dsn}')
    timeout = 0.001
    total_timeout = 0

    for i in range(15):
        try:
            await database.connect()
        except (ConnectionRefusedError, CannotConnectNowError):
            timeout *= 2
            await asyncio.sleep(timeout)
            total_timeout += timeout
        else:
            break
    else:
        msg = f'Unable to connect database for {int(total_timeout)}s'
        logger.error(msg)
        raise ConnectionRefusedError(msg)


def tries(times):
    def func_wrapper(f):
        async def wrapper(*args, **kwargs):
            for time in range(times if times > 0 else 1):
                # noinspection PyBroadException
                try:
                    return await f(*args, **kwargs)
                except Exception as exc:
                    if time >= times:
                        raise exc

        return wrapper

    return func_wrapper
