FROM node:12.16.1-apline

COPY . .

CMD node server.js

EXPOSE 80