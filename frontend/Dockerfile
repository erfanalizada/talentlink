# ----------------------------------------------------
# 1. Build Flutter web (AMD64 ONLY)
# ----------------------------------------------------
FROM --platform=linux/amd64 ghcr.io/cirruslabs/flutter:stable AS build

WORKDIR /app
COPY talentlink_frontend ./talentlink_frontend

WORKDIR /app/talentlink_frontend
RUN flutter build web --release

# ----------------------------------------------------
# 2. Serve with multi-arch Nginx 
# (works on both amd64 and arm64)
# ----------------------------------------------------
FROM nginx:stable-alpine

# Replace default nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy compiled web files (architecture-independent)
COPY --from=build /app/talentlink_frontend/build/web /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
