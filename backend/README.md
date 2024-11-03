# Backend

Ferntree uses a FastAPI-based backend for simulating and analyzing solar energy systems. It integrates with a MongoDB database and a custom energy system simulation tool.

## Features

- User authentication and management
- Solar system modeling and simulation
- Analysis of energy system operations
- Financial calculations for system installations
- Integration with PVGIS API for solar irradiance data
- Asynchronous operations for improved performance

## Technology Stack

- **FastAPI**: A fast, asynchronous web framework for building APIs with Python.
- **MongoDB**: A document-based NoSQL database for storing user data, models, simulation data and financial results.
- **Motor**: An asynchronous Python driver for MongoDB.
- **Pydantic**: Data validation and settings management using Python type annotations.
- **Ferntree**: A custom simulation tool for detailed energy system modeling and simulation.

## Key Components

### 1. FastAPI

The API endpoints for interacting with the backend are defined in the [`main`](./main.py) module. The FastAPI application is created in this module and includes routes for model management, simulation execution & evaluation, and financial analysis. The application can be run with `uvicorn` via `uvicorn backend.main:app --reload`.

- The backend uses the [`solar_data`](./solar_data/) module for querying the [PVGIS](https://re.jrc.ec.europa.eu/pvg_tools/en/) API for solar irradiance data and the Nominatim as well as GeoNames APIs for geolocation data.
- All simulation operations for interacting with the [`ferntree simulation engine`](../sim/ferntree/) as well as financial analysis operations are handled by the [`sim_funcs`](./utils/sim_funcs.py/) module.
- User authentication is managed in [`auth_funcs`](./utils/auth_funcs.py).

### 2. Database Operations (`MongoClient` class)

The [`MongoClient`](./database/mongodb.py) class handles all interactions with the MongoDB database, including:
- User authentication
- Model creation, retrieval, and deletion
- Simulation data storage and retrieval
- Financial data management

### 3. Pydantic models

Data validation for incoming requests, database operations and outgoing responses is handled using Pydantic models. These models are defined in the [`models`](./database/models.py) module.
