import logging
import sys

from .auth import auth_check, router as auth_router
from .db import startup as db_startup
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .tasks.api import router as tasks_router
from .users.api import router as users_router

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(
    logging.Formatter(
        "%(asctime)s [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s"
    )
)
logger.addHandler(handler)


app = FastAPI(
    debug=True,
    title="TODO-Backend",
    description="Backend for TODO app",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    logger.info("Starting up...")
    db_startup()
    logger.info("Startup complete.")


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(tasks_router, dependencies=[Depends(auth_check)])
