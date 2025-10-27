# Use official Keycloak base image
FROM quay.io/keycloak/keycloak:25.0

# Copy Oracle JDBC driver
COPY drivers/ojdbc11.jar /opt/keycloak/providers/

# Add Oracle Cloud root certificate (TLS only)
RUN apt-get update && apt-get install -y ca-certificates && \
    curl -o /usr/local/share/ca-certificates/oracle_root.cer \
        https://download.oracle.com/otn_software/ssl-certs/oracle_cloud_root.cer && \
    update-ca-certificates

# Build Keycloak with custom providers and configuration
RUN /opt/keycloak/bin/kc.sh build

EXPOSE 8080

ENTRYPOINT ["/opt/keycloak/bin/kc.sh", "start"]
