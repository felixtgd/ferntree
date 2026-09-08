"""Assemble the FastAPI application and manage its resources."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers.finances_router import router as finances_router
from src.api.routers.models_router import router as models_router
from src.api.routers.simulations_router import router as simulations_router
from src.db.async_client.client import DatabaseClient
from src.db.async_client.pool import pool


# Create a FastAPI instance
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Open and close the database pool for the application lifetime.

    Args:
        app (FastAPI): The application instance.

    Yields:
        None: Control to the application while the database pool is open.

    """
    await pool.open()
    app.state.db_client = DatabaseClient()
    try:
        yield
    finally:
        await pool.close()


app: FastAPI = FastAPI(lifespan=lifespan)
app.include_router(simulations_router)
app.include_router(finances_router)
app.include_router(models_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
