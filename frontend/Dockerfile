FROM --platform=linux/amd64 node:14-alpine

WORKDIR /frontend
COPY package.json .
COPY package-lock.json .
##RUN which python
RUN npm ci
COPY . .
RUN npm run build
