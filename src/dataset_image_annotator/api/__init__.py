import uvicorn

from dataset_image_annotator.api.http import app
from dataset_image_annotator.conf import settings


if __name__ == '__main__':
    uvicorn.run(app, host=settings.service_addr, port=settings.service_port)
