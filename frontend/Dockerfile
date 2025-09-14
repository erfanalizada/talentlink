# 1. Build Flutter web
FROM ghcr.io/cirruslabs/flutter:latest AS build
WORKDIR /app
COPY talentlink_frontend ./talentlink_frontend
WORKDIR /app/talentlink_frontend
RUN flutter build web --release

# 2. Serve with Nginx
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/talentlink_frontend/build/web /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
