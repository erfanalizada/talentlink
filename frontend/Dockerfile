# ----------------------------------------------------
# 1. Build Flutter web (multi-arch compatible)
# ----------------------------------------------------
FROM ghcr.io/cirruslabs/flutter:stable AS build

WORKDIR /app
COPY talentlink_frontend ./talentlink_frontend

WORKDIR /app/talentlink_frontend
RUN flutter build web --release

# ----------------------------------------------------
# 2. Serve with correct multi-arch Nginx image
# ----------------------------------------------------
FROM nginx:stable-alpine

# Replace default nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy compiled web files
COPY --from=build /app/talentlink_frontend/build/web /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
