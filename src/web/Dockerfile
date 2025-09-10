FROM node:20-alpine AS build

# make the 'app' folder the current working directory
WORKDIR /app

COPY . .

# Set environment variables for build
ENV VITE_API_BASE_URL=http://localhost:3100
ENV VITE_APPLICATIONINSIGHTS_CONNECTION_STRING=

# install project dependencies
RUN npm ci
RUN npm run build

FROM nginx:alpine

WORKDIR /usr/share/nginx/html
COPY --from=build /app/dist .
COPY --from=build /app/nginx/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["/bin/sh", "-c", "nginx -g \"daemon off;\""]
