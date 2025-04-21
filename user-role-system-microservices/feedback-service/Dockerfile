# feedback-service/Dockerfile
FROM node:16

WORKDIR /app

COPY package.json /app
RUN npm install

COPY . /app

EXPOSE 5003

CMD ["node", "server.js"]
