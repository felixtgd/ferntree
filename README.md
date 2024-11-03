# Ferntree

## Overview

Ferntree is an open-source tool to help you make informed decisions when you're ciónsidering a solar system for your home. Our solar calculator allows you to:

- Design and simulate various energy systems
- Compare different setups
- Customize financial parameters
- Assess investment potential

Ferntree aims to help you in your decision-making process by allowing to experiment freely with system designs, financial scenarios, and energy options.

## Technology Stack

- **FastAPI**: A fast, asynchronous web framework for building APIs with Python.
- **MongoDB**: A document-based NoSQL database for storing user data, models, simulation data and financial results.
- **NextJS**: A React framework for building web applications.
- **Ferntree**: A custom simulation tool for detailed energy system modeling and simulation.

## Key Components

### 1. Ferntree simulation engine

The [simulation engine](./sim/ferntree/) is a custom tool for modeling and simulating energy systems. It is used for timeseries simulation of the operation of energy systems for single-family homes consisting of baseload electricity demand, photovoltaic system for electricity generation, and battery energy storage. The engine is implemented in Python and is integrated with the FastAPI backend. See the [ferntree sim README](./sim/ferntree/README.md) for more details.

### 2. FastAPI backend

The [backend](./backend/) is built using FastAPI and provides the API endpoints for interacting with the simulation engine and the MongoDB database. See the [backend README](./backend/README.md) for more details.

### 3. NextJS frontend

The [frontend](./frontend/) is built using NextJS and provides the user interface of the web app. See the [frontend README](./frontend/README.md) for more details.

## Getting Started

- Clone the repository
- Set up a MongoDB instance and create a database
- Install the required backend dependencies by running `pip install -r requirements.txt`
- Install the required frontend dependencies by running `npm install`
- Start the backend server by running `uvicorn backend.main:app --reload`
- Start the frontend server by running `npm run dev`


## Configuration

The application uses environment variables for configuration. Ensure the following variables are set:
- `MONGODB_URI`: The connection string for your MongoDB instance
- `MONGODB_DATABASE`: The name of the database to use
- `FRONTEND_BASE_URI`: The base URI for the frontend application. Can be a comma-separated list. The backend will only accept requests from these URIs.
- `BACKEND_BASE_URI`: The base URI for the backend application. Used by the frontend to make API requests.
- `NODE_ENV`: The environment in which the application is running (development, production, etc.)
- `AUTH_SECRET`: NextAuth secret key for token generation
- `AUTH_GITHUB_ID`: GitHub OAuth client ID
- `AUTH_GITHUB_SECRET`: GitHub OAuth client secret
- `AUTH_GOOGLE_ID`: Google OAuth client ID
- `AUTH_GOOGLE_SECRET`: Google OAuth client secret
- `EMAIL_HOST`: SMTP server host
- `EMAIL_PORT`: SMTP server port
- `EMAIL_SENDER`: Email address for sending emails for user signup
- `EMAIL_PASS`: Password for the email sender
- `EMAIL_RECEIVER`: Email address for receiving emails from contact form


## Contributing

Contributions to improve the simulation engine, add new features, or enhance the API are welcome. Please follow the standard GitHub pull request process to submit your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](../LICENSE) file for details.
