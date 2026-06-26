import logging
import os
import sys


from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
load_dotenv()

from .auth import auth_check  # noqa: E402
from .auth import router as auth_router  # noqa: E402
from .db import startup as db_startup  # noqa: E402
from .tasks.api import router as tasks_router  # noqa: E402
from .users.api import router as users_router  # noqa: E402

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(
    logging.Formatter(
        "%(asctime)s [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s"
    )
)
logger.addHandler(handler)

ENV = os.environ.get('DEPLOY_ENV', 'dev')

config: dict
if ENV == 'dev':
    origins = ['*']  # set to all for dev purposes
    config = {
        'debug': True
    }
else:
    FRONTEND_ORIGIN = os.environ.get('FRONTEND_ORIGIN')
    assert FRONTEND_ORIGIN is not None, 'frontend origin must be specified for non-dev envs'
    origins = [FRONTEND_ORIGIN]
    config = {
        'debug': False,
        'docs_url': None,
        'redoc_url': None,
        'openapi_url': None
    }


app = FastAPI(
    title="TODO-Backend",
    description="Backend for TODO app",
    version="0.1.0",
    **config
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["POST", "GET", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization"],
)


@app.on_event("startup")
def startup():
    logger.info("Starting up...")
    db_startup()
    logger.info("Startup complete.")


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(tasks_router, dependencies=[Depends(auth_check)])
