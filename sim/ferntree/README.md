# Ferntree Simulation Engine

## Overview

The Ferntree Simulation Engine is a custom tool for simulating the operation of sustainable energy systems. It is used to model residential photovoltaic systems consisting of baseload electricity demand, photovoltaic system for electricity generation, and battery energy storage. The operation of the system's individual components is simulated for one year on an hourly timebase using real-world solar irradiance data of the given location.

The engine is implemented in Python and is integrated with the FastAPI backend and MongoDb database.

## Key Components

### 1. [ferntree.py](./ferntree.py)

The main function to run the simulation. It takes the model id and simulation id pointing to the specification docs in the database as input and builds & runs the simulation. The function can also be called from the command line with `python sim/ferntree/ferntree.py --sim_id sim_id --model_id model_id`.

### 2. [sim_builder.py](./sim_builder.py)

The class to build the simulation and the system model. It gets the simulation and model specs from the database and creates the system model with baseload, PV system, and battery.

### 3. [database](./components/database/)

The module containing the MongoDB Client for interacting with the database. It contains functions to get the model and simulation specs from the database and to store the simulation results.

### 4. [ctrl](./components/ctrl/)

This module contains controller devices. Right now, there exists only one battery controller with a simple greedy strategy to maximise self-consumption, and one experimental controller for a heating system, that isn't implemented yet. In the future, it would be great to add more control algorithms for the battery to let users try different strategies.

### 5. [dev](./components/dev/)

The module containing the devices of the system model. It contains the devices for the baseload, PV system, battery, smart meter and the house (parent device to aggregate all components). There are a also experimental devices for a heating system, but they are not implemented yet.

### 6. [host](./components/host/)

The SimHost class is the main component of the simulation. It is responsible for:
- Setting up the simulation environment
- Handling weather data
- Running the simulation, i.e. triggering each time tick
- Saving the results to the database

### 7. [models](./components/models/)

This module only contains some thermal models I tried for the heating system. It's only experimental and not used in the simulation yet.
