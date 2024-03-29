import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from starlette.applications import Starlette

from dataset_image_annotator.api.v1.endpoints import router, auth_router, users_router


logger = logging.getLogger(__name__)
origins = [
    'http://localhost',
    'http://localhost:3000',
    'http://localhost:8080',
    'http://localhost:5000',
]


@asynccontextmanager
async def lifespan(app: Starlette):
    yield


app = FastAPI(docs_url='/api/docs', openapi_url='/api/v1/openapi.json', lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(router, prefix='/api/v1')
app.include_router(
    auth_router,
    prefix='/api/v1/auth',
    tags=['auth'],
)
app.include_router(
    users_router,
    prefix='/api/v1/users',
    tags=['users'],
)
add_pagination(app)
