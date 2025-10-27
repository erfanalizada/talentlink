# Use official Keycloak image (v25+ with Quarkus)
FROM quay.io/keycloak/keycloak:25.0

# Copy Oracle JDBC driver
COPY drivers/ojdbc11.jar /opt/keycloak/providers/

# Enable health and metrics endpoints
ENV KC_HEALTH_ENABLED=true
ENV KC_METRICS_ENABLED=true

# Build optimized Keycloak distribution
RUN /opt/keycloak/bin/kc.sh build

# Start Keycloak (optimized)
ENTRYPOINT ["/opt/keycloak/bin/kc.sh", "start", "--optimized"]
