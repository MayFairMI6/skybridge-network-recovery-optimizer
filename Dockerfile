FROM node:20-alpine
WORKDIR /app
COPY app/package.json ./
COPY app/server.js ./
COPY data ./data
EXPOSE 3000
ARG APP_BUILD=local
ENV APP_BUILD=${APP_BUILD}
CMD ["npm", "start"]
