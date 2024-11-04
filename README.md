# Ferntree

## Overview

Ferntree is an open-source tool for designing, simulating and analysing solar energy systems. Our independent, free-to-use calculator allows you to:

- Design and simulate various energy systems
- Compare different setups
- Customize financial parameters
- Assess investment potential

With Ferntree, you can experiment freely with system designs, financial scenarios, and energy options.

## Features

- User-friendly web interface for system design
- Detailed simulation of solar energy systems
- Financial analysis and investment assessment
- Integration with real-world solar irradiance data
- Open-source and transparent calculations

## Technology Stack

- **Frontend**: [NextJS](https://nextjs.org/docs) (React framework)
- **Backend**: [FastAPI](https://fastapi.tiangolo.com) (Python web framework)
- **Database**: [MongoDB](https://www.mongodb.com)
- **Energy System Simulation**: Custom Python [simulation tool](./sim/ferntree/)
## Key Components

### 1. Ferntree simulation engine

The [simulation engine](./sim/ferntree/) is a custom tool for modeling and simulating energy systems. It is used for timeseries simulation of the operation of energy systems for single-family homes consisting of baseload electricity demand, photovoltaic system for electricity generation, and battery energy storage. The engine is implemented in Python and is integrated with the FastAPI backend. See the [ferntree sim README](./sim/ferntree/README.md) for more details.

### 2. FastAPI backend

The [backend](./backend/) is built using FastAPI and provides the API endpoints for interacting with the simulation engine and the MongoDB database. See the [backend README](./backend/README.md) for more details.

### 3. NextJS frontend

The [frontend](./app/) is built using NextJS and provides the user interface of the web app. See the [frontend README](./app/README.md) for more details.

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 14+
- MongoDB

### Installation

1. Clone the repository: `git clone https://github.com/felixtgd/ferntree.git`
2. Set up a virtual environment (optional but recommended): `python -m venv venv` & `source venv/bin/activate`
3. Install the backend dependencies: `pip install -r requirements.txt`
4. Install the frontend dependencies: `npm install`
5. Set up environment variables (see Configuration section below)

### Running the Application

1. Start the backend server: `uvicorn backend.main:app --reload`
2. In a new terminal, start the frontend server: `npm run dev`
3. Open your browser and navigate to `http://localhost:3000`

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


## Contributions

Contributions to improve the application and add more features are welcome. Please open an issue, submit a pull request, or send an email to contact@ferntree.dev.

## License

This project is licensed under the MIT License. See [LICENSE](./LICENSE) for details.
