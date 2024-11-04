# Frontend

This directory contains the NextJS frontend for the Ferntree web application. The frontend provides the user interface for designing, simulating and analysing solar energy systems. It´s written in Typescript and uses Tailwind CSS for styling.

## Features

- User signup and login with magic link authentication via email or OAuth providers (GitHub and Google)
- Static landing page with contact form for user feedback
- Energy systems modelling, with five allowed models per user
- Simulation of energy systems with detailed timeseries results and key performance indicators
- Financial analysis with system performance over useful life and economic viability metrics


## Technology Stack

- **Frontend Framework**: [NextJS](https://nextjs.org/docs) with Typescript and [Tailwind CSS](https://tailwindcss.com) for styling
- **Data Visualization**: [Tremor](https://tremor.so/docs/getting-started/installation) components
- **Icons**: [Remix Icon](https://remixicon.com)
- **User Authentication**: [Auth.js](https://authjs.dev)
- **Mail Service**: [NodeMailer](https://nodemailer.com/about/)

## Key Components

### 1. User Authentication

User authentication is handled in [auth.ts](../auth.ts), [auth.config.ts](../auth.config.ts), [middleware.ts](../middleware.ts), and [route.ts](./api/[...nextauth]/route.ts).

The login/signup page is implemented in [login](./login/).

### 2. Components

Basic components, that are reused throughout the application, are defined in the [components](./components/) directory. It contains for example buttons and their server actions, skeletons, tremor components, and chart base components.

### 3. Utils

The MongoDb client required for user authentication, the data models used throughout the application, as well as general server actions are defined in the [utils](./utils/) directory.

### 4. Workspace

The workspace is the main part of the application, where users can design, simulate, and analyze their energy systems. It is implemented in the [workspace](./workspace/) directory, which in turn contains the pages for [models](./workspace/models/), [simulations](./workspace/simulations/), and [finances](./workspace/finances/).
