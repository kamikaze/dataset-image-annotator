import logging
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from dataset_image_annotator.conf import settings

logger = logging.getLogger(__name__)
timezone = ZoneInfo(settings.timezone)


async def handle_raw_file(session: AsyncSession, image_file):
    image_file_body = await image_file.read()

    return True
