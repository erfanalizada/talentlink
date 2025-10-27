# Use official Keycloak base image
FROM quay.io/keycloak/keycloak:25.0

# Copy Oracle JDBC driver (for your Oracle Autonomous DB)
COPY drivers/ojdbc11.jar /opt/keycloak/providers/

# Build Keycloak with custom providers and configuration
RUN /opt/keycloak/bin/kc.sh build

# Expose default Keycloak port
EXPOSE 8080

# Start Keycloak in production mode
ENTRYPOINT ["/opt/keycloak/bin/kc.sh", "start"]
