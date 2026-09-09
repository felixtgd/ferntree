# Frontend image to run NextJS app
FROM node:20-alpine AS frontend-base
WORKDIR /usr/local/app
COPY ./frontend/package*.json ./
RUN npm install
COPY ./frontend ./
EXPOSE 5173

FROM frontend-base AS frontend-dev
CMD ["npm", "run", "dev"]

FROM frontend-base AS frontend-prod
RUN npm run build
CMD ["npm", "run", "start"]

# Backend image to run FastAPI app with simulation tool
FROM python:3.12-slim AS backend-base
WORKDIR /usr/src/app
COPY ./backend ./
RUN pip install uv
EXPOSE 8000

FROM backend-base AS backend-dev
RUN uv sync --frozen
CMD [ "uv", "run", "uvicorn", "src.api.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]

FROM backend-base AS backend-prod
RUN uv sync --frozen --no-dev
CMD [ "uv", "run", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
