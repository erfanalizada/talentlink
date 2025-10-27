// package app;  // <-- comment this out unless you're organizing packages

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

import oracle.ucp.jdbc.PoolDataSource;
import oracle.ucp.jdbc.PoolDataSourceFactory;

public class TestOracleUCP {

    // Replace with your Oracle ADB credentials
    private static final String DB_USER = "keycloak_user";
    private static final String DB_PASSWORD = "Keycloak123!";

    // TCPS connection string for your region & service
    private static final String CONNECT_STRING =
        "(description=" +
        " (retry_count=20)(retry_delay=3)" +
        " (address=(protocol=tcps)(port=1522)(host=adb.eu-amsterdam-1.oraclecloud.com))" +
        " (connect_data=(service_name=g49f31b19d33266_keycloakauth_high.adb.oraclecloud.com))" +
        " (security=(ssl_server_dn_match=yes)))";

    private static final String CONN_FACTORY_CLASS_NAME =
        "oracle.jdbc.replay.OracleConnectionPoolDataSourceImpl";

    private PoolDataSource poolDataSource;

    public TestOracleUCP() throws SQLException {
        poolDataSource = PoolDataSourceFactory.getPoolDataSource();
        poolDataSource.setConnectionFactoryClassName(CONN_FACTORY_CLASS_NAME);

        // Important: Thin mode over TCPS
        poolDataSource.setURL("jdbc:oracle:thin:@" + CONNECT_STRING);

        // Set credentials
        poolDataSource.setUser(DB_USER);
        poolDataSource.setPassword(DB_PASSWORD);
        poolDataSource.setConnectionPoolName("JDBC_UCP_POOL");

        // TLS truststore configuration
        System.setProperty("javax.net.ssl.trustStore", "truststore.jks");
        System.setProperty("javax.net.ssl.trustStorePassword", "changeit");
    }

    public void testConnection() {
        try (Connection conn = poolDataSource.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery("SELECT 1 FROM DUAL")) {

            if (rs.next()) {
                System.out.println("✅ Oracle UCP TLS connection successful! Query result: " + rs.getInt(1));
            }

        } catch (SQLException e) {
            System.err.println("❌ Connection failed: " + e.getMessage());
            e.printStackTrace();
        }
    }

    public static void main(String[] args) {
        try {
            TestOracleUCP uds = new TestOracleUCP();
            uds.testConnection();
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
