FROM node:20 AS frontend-base
WORKDIR /usr/local/app

# Install dependencies
COPY ./frontend/package*.json ./
RUN npm install

# Copy frontend files
COPY ./frontend ./

FROM frontend-base AS frontend-dev
EXPOSE 3000
CMD ["npm", "run", "dev"]
