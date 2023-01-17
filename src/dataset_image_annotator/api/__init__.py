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
        'default_stdout': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'default',
        },
        'default_stderr': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
            'formatter': 'default',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default_stdout', 'default_stderr', ],
        },
        'dataset_image_annotator': {
            'handlers': ['default_stdout', 'default_stderr', ],
            'level': settings.logging_level,
            'propagate': False,
        }
    }
}
logging.config.dictConfig(LOGGING_CONFIG)
