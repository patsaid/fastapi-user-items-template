"""
This is the main module of the FastAPI application.

It sets up the FastAPI application, configures logging, and defines the routes
    for various endpoints.

Routes:
- GET /: Returns a message directing users to visit /docs for server documentation.
- GET /heartbeat: Returns a message indicating the status of the database connection.

"""

import logging
import logging.config

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import FRONTEND_URL
from app.db.database import check_db_connection
from app.routes.auth.handler import auth_router
from app.routes.category.handler import categories_router
from app.routes.items.handler import items_router
from app.routes.users.handler import user_router

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
    """
    Root endpoint of the FastAPI application.

    Returns:
        dict: A dictionary containing a message directing users to visit /docs
            for server documentation.
    """
    return {"message": "Visit /docs for server documentation"}


@app.get("/heartbeat", tags=["heartbeat"])
async def heartbeat():
    """
    Heartbeat endpoint of the FastAPI application.

    Returns:
        dict: A dictionary containing a message indicating the status of the database connection.

    Raises:
        HTTPException: If there is an error in the database connection.
    """
    if check_db_connection():
        return {"message": "Database connection is healthy."}

    raise HTTPException(status_code=500, detail="Database connection error")


app.include_router(categories_router)
app.include_router(items_router)
app.include_router(user_router)
app.include_router(auth_router)
