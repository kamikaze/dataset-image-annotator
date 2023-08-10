import gettext
import logging
from pathlib import Path
from typing import Mapping, Sequence

import sqlalchemy as sa
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.ext.asyncio import AsyncSession

from dataset_image_annotator.api.v1.schemas import UserItem, ImageSampleItem
from dataset_image_annotator.db.helpers import get_query
from dataset_image_annotator.db.models import UserGroup, User, ImageSample

logger = logging.getLogger(__name__)
t = gettext.translation('base', Path(Path(__file__).parent, 'locale'), fallback=True, languages=['lv_LV'])
_ = t.gettext


async def get_users(session: AsyncSession, search: Mapping[str, str] | None = None,
                    order_by: str | None = None) -> Page[UserItem]:
    query = sa.select([User])
    result = await paginate(session, query)

    return result


async def get_user(session: AsyncSession, user_id: str) -> UserItem:
    query = sa.select(User).where(User.id == user_id)
    cursor = await session.execute(query)
    result = cursor.scalar_one()

    return result


async def get_user_groups(session: AsyncSession, search: Mapping[str, str] | None = None,
                          order_by: str | None = None) -> Sequence[UserGroup]:
    query = sa.select(UserGroup).order_by(UserGroup.name)
    cursor = await session.execute(query)
    result = cursor.scalars()

    return result


async def get_image_samples(session: AsyncSession, search: Mapping[str, str] | None = None,
                            order_by: str | None = None) -> Page[ImageSampleItem]:
    columns = {
        'id': (ImageSample.id, False, int, True),
        'filename': (ImageSample.filename, True, str, False),
        'checksum': (ImageSample.checksum, True, str, False),
        'location': (ImageSample.location, True, str, False),
    }
    where_clause, order_by_clause = get_query(search, order_by, columns)
    query = sa.select(ImageSample.id, ImageSample.location).order_by(order_by_clause)

    if where_clause is not None:
        query = query.where(where_clause)

    return await paginate(session, query)
