# Stage 1: Build Flutter Web
FROM cirrusci/flutter:3.24.0 AS build
WORKDIR /app

# Copy source code
COPY . .

# Build Flutter web app in release mode
RUN flutter build web --release

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Copy built Flutter web files into Nginx html directory
COPY --from=build /app/build/web /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Run Nginx
CMD ["nginx", "-g", "daemon off;"]
