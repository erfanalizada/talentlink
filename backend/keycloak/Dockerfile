# Use official Keycloak image
FROM quay.io/keycloak/keycloak:25.0

# Switch to root to add files
USER root

# Copy Oracle JDBC driver and truststore
COPY drivers/ojdbc11.jar /opt/keycloak/providers/
COPY truststore.jks /opt/keycloak/truststore.jks

# Safety check – fail the build if the truststore wasn’t copied
RUN if [ ! -f /opt/keycloak/truststore.jks ]; then \
      echo "ERROR: truststore.jks missing!" && exit 1; \
    fi

# Build Keycloak configuration
RUN /opt/keycloak/bin/kc.sh build

# Drop back to keycloak user
USER keycloak

# Expose HTTP port
EXPOSE 8080

# Start Keycloak
ENTRYPOINT ["/opt/keycloak/bin/kc.sh", "start"]
