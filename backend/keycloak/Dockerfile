# Use official Keycloak base image
FROM quay.io/keycloak/keycloak:25.0

# Copy Oracle JDBC driver and TLS truststore
COPY drivers/ojdbc11.jar /opt/keycloak/providers/
COPY truststore.jks /opt/keycloak/conf/truststore.jks

# Environment variables for Keycloak
ENV KC_DB=oracle
ENV KC_DB_URL="jdbc:oracle:thin:@(description=(retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1521)(host=adb.eu-amsterdam-1.oraclecloud.com))(connect_data=(service_name=g49f31b19d33266_keycloakauth_high.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))"
ENV KC_DB_USERNAME=keycloak_user
ENV KC_DB_PASSWORD=Keycloak123!
ENV JAVA_OPTS_APPEND="-Djavax.net.ssl.trustStore=/opt/keycloak/conf/truststore.jks -Djavax.net.ssl.trustStorePassword=changeit"

# Build Keycloak image with the Oracle driver
RUN /opt/keycloak/bin/kc.sh build

EXPOSE 8080

# Start Keycloak in production mode
ENTRYPOINT ["/opt/keycloak/bin/kc.sh", "start", "--optimized"]
