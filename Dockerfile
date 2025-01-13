# Frontend image to run NextJS app
FROM node:20-alpine AS frontend-base
WORKDIR /usr/local/app
COPY ./frontend/package*.json ./
RUN npm install
COPY ./frontend ./
EXPOSE 3000

FROM frontend-base AS frontend-dev
CMD ["npm", "run", "dev"]

FROM frontend-base AS frontend-prod
RUN npm run build
CMD ["npm", "run", "start"]

# Backend image to run FastAPI app with simulation tool
FROM python:3.12-alpine AS backend-base
WORKDIR /usr/src/app
COPY ./backend/requirements.txt ./
RUN apt-get update && apt-get install -y build-essential
RUN pip install --no-cache-dir -r requirements.txt
COPY ./backend ./
EXPOSE 8000

FROM backend-base AS backend-dev
CMD [ "uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]

FROM backend-base AS backend-prod
CMD [ "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
