# Frontend Dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./
COPY . ./
RUN npm install && npm run build

FROM node:20-alpine AS prod
WORKDIR /app
COPY --from=build /app/build ./build
COPY --from=build /app/package.json ./
RUN npm install --omit=dev
EXPOSE 3000
ENV NODE_ENV=production
CMD ["node", "build"]
