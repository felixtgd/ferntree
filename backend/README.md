# Backend

## Overview

Ferntree uses a FastAPI-based backend for simulating and analyzing solar energy systems. It integrates with a MongoDB database and a custom Ferntree simulation tool for detailed energy system modeling.

## Features

- User authentication and management
- Solar system modeling and simulation
- Energy consumption and production analysis
- Financial calculations for solar installations
- Integration with PVGIS API for solar irradiance data
- Asynchronous operations for improved performance

## Technology Stack

- **FastAPI**: A modern, fast web framework for building APIs with Python.
- **MongoDB**: A document-based NoSQL database for storing user data, models, and simulation results.
- **Motor**: An asynchronous Python driver for MongoDB.
- **Pydantic**: Data validation and settings management using Python type annotations.
- **Ferntree**: A custom simulation tool for detailed energy system modeling.

## Key Components

### 1. Database Operations (`MongoClient` class)

The `MongoClient` class handles all interactions with the MongoDB database, including:
- User authentication
- Model creation, retrieval, and deletion
- Simulation data storage and retrieval
- Financial data management

### 2. Solar Data Retrieval

The application fetches solar irradiance data using the PVGIS API:
- `get_solar_data_for_location`: Retrieves solar data for a specific location.
- `api_request_solar_irr`: Makes API requests to PVGIS for hourly solar irradiance data.

### 3. Simulation Management

- `get_sim_input_data`: Prepares input data for the Ferntree simulation.
- `run_ferntree_simulation`: Executes the Ferntree simulation tool.
- `eval_sim_results`: Evaluates and processes simulation results.

### 4. Energy Analysis

- `calc_energy_kpis`: Calculates key performance indicators for energy production and consumption.
- `calc_pv_monthly_gen`: Computes monthly PV generation data.

### 5. Financial Analysis

- `calc_fin_results`: Performs financial calculations based on simulation results and user inputs.

## API Endpoints

The backend provides several API endpoints for interacting with the system:

- `/workspace/models/`: Endpoints for creating, retrieving, and deleting solar system models.
- `/workspace/simulations/`: Endpoints for running simulations and fetching results.
- `/workspace/finances/`: Endpoints for submitting financial data and retrieving financial analysis results.

## Getting Started

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in a `.env` file (MongoDB URI, database name, etc.)
4. Run the FastAPI server: `uvicorn backend.main:app --reload`

## Configuration

The application uses environment variables for configuration. Ensure the following variables are set:
- `MONGODB_URI`: The connection string for your MongoDB instance
- `MONGODB_DATABASE`: The name of the database to use

## Contributing

Contributions to improve the simulation accuracy, add new features, or enhance the API are welcome. Please follow the standard GitHub pull request process to submit your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
