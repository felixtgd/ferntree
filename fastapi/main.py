from enum import Enum

from models import SimulationModel

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


class RoofTilt(int, Enum):
    flat = 0
    tilted30 = 30
    tilted45 = 45


class RoofAzimuth(int, Enum):
    south = 0
    south_east = -45
    south_west = 45
    east = -90
    west = 90
    north_east = -135
    north_west = 135
    north = 180


app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/dashboard/pv-calc")
async def pv_calc(sim_model: SimulationModel):
    print(sim_model.model_dump())
    return {"status": "Simulation started", "model": sim_model.model_dump()}
