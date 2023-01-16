import gettext
import logging
from pathlib import Path
from typing import Mapping, Sequence

import sqlalchemy as sa
from databases.backends.postgres import Record
from fastapi_pagination import Page
from fastapi_pagination.ext.databases import paginate

from dataset_image_annotator.api.v1.schemas import UserItem, ImageSampleItem
from dataset_image_annotator.db.helpers import get_query
from dataset_image_annotator.db.models import UserGroup, User, ImageSample

logger = logging.getLogger(__name__)
t = gettext.translation('base', Path(Path(__file__).parent, 'locale'), fallback=True, languages=['lv_LV'])
_ = t.gettext


async def get_users(database, search: Mapping[str, str] | None = None, order_by: str | None = None) -> Page[UserItem]:
    query = sa.select([User])
    result = await paginate(database, query)

    return result


async def get_user(database, user_id: str) -> Record:
    query = sa.select([User]).where(User.id == user_id)

    return await database.fetch_row(query)


async def get_user_groups(database, search: Mapping[str, str] | None = None,
                          order_by: str | None = None) -> Sequence[UserGroup]:
    query = sa.select([UserGroup]).order_by(UserGroup.name)
    result = await database.fetch_all(query)

    return result


async def get_image_samples(database, search: Mapping[str, str] | None = None,
                            order_by: str | None = None) -> Page[ImageSampleItem]:
    columns = {
        'id': (ImageSample.id, False, int, True),
        'filename': (ImageSample.filename, True, str, False),
        'checksum': (ImageSample.checksum, True, str, False),
        'location': (ImageSample.location, True, str, False),
    }
    where_clause, order_by_clause = get_query(search, order_by, columns)
    query = sa.select([ImageSample.id, ImageSample.location]).order_by(order_by_clause)

    if where_clause is not None:
        query = query.where(where_clause)

    result = await database.fetch_all(query)

    return result
