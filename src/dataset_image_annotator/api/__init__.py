import logging.config

import uvicorn

from dataset_image_annotator.api.http import app
from dataset_image_annotator.conf import settings


LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            '()': 'dataset_image_annotator.formatter.JSONFormatter',
        },
    },
    'handlers': {
        'default': {
            'level': settings.logging_level,
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'default',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default', ],
        },
        'dataset_image_annotator': {
            'handlers': ['default', ],
            'level': settings.logging_level,
            'propagate': False,
        }
    }
}
logging.config.dictConfig(LOGGING_CONFIG)

uvicorn.run(app, host=settings.service_addr, port=settings.service_port, proxy_headers=True, log_config=LOGGING_CONFIG)
