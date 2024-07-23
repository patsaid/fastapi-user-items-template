import logging
import logging.config

from fastapi import FastAPI, HTTPException
from app.db.database import check_db_connection
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import FRONTEND_URL
from app.routes.users.handler import user_router
from app.routes.auth.handler import auth_router
from app.routes.items.handler import items_router
from app.routes.category.handler import categories_router


logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Visit /docs for server documentation"}


# Heartbeat endpoint
@app.get("/heartbeat", tags=["heartbeat"])
async def heartbeat():
    if check_db_connection():
        return {"message": "Database connection is healthy."}
    else:
        raise HTTPException(status_code=500, detail="Database connection error")


app.include_router(categories_router)
app.include_router(items_router)
app.include_router(user_router)
app.include_router(auth_router)
