from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.finances_router import router as finances_router
from src.api.models_router import router as models_router
from src.api.simulations_router import router as simulations_router
from src.database.postgres import pool


# Create a FastAPI instance
@asynccontextmanager
async def lifespan(_: FastAPI):
    """Open and close the database pool for the application lifetime.

    Args:
        _ (FastAPI): The application instance.

    """
    await pool.open()
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
