# Frontend - React dashboard (build then serve with nginx)
FROM node:20-alpine AS builder

WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
# Point to backend services (same host in Docker; browser will use relative URLs if served behind same origin)
ENV VITE_PLANNING_API=/api/planning
ENV VITE_OPERATIONS_API=/api/operations
ENV VITE_ANALYTICS_API=/api/analytics
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
# Proxy API calls to backend services
RUN echo 'server { \
  listen 80; \
  root /usr/share/nginx/html; \
  index index.html; \
  location / { try_files $uri $uri/ /index.html; } \
  location /api/planning/ { proxy_pass http://planning-service:8000/api/; proxy_http_version 1.1; proxy_set_header Host $host; proxy_set_header X-Real-IP $remote_addr; } \
  location /api/operations/ { proxy_pass http://operations-service:8001/api/; proxy_http_version 1.1; proxy_set_header Host $host; proxy_set_header X-Real-IP $remote_addr; } \
  location /api/analytics/ { proxy_pass http://analytics-service:8002/api/; proxy_http_version 1.1; proxy_set_header Host $host; proxy_set_header X-Real-IP $remote_addr; } \
}' > /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
