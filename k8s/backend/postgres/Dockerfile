# Use official PostgreSQL base image
FROM postgres:16

# Optional: Copy initialization SQL files if you have them
# COPY init.sql /docker-entrypoint-initdb.d/

# Set environment variables
ENV POSTGRES_USER=keycloak
ENV POSTGRES_PASSWORD=StrongPassword123
ENV POSTGRES_DB=keycloak

# Expose the PostgreSQL port
EXPOSE 5432
