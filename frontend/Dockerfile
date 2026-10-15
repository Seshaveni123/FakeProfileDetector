FROM node:18-alpine

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

EXPOSE 5173

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD ["node", "-e", "const http = require('http'); const req = http.get('http://127.0.0.1:5173/', (res) => { process.exit(res.statusCode >= 200 && res.statusCode < 400 ? 0 : 1); }); req.setTimeout(3000, () => { req.destroy(); process.exit(1); }); req.on('error', () => process.exit(1));"]

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
