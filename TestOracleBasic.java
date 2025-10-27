import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.Properties;

public class TestOracleBasic {
    public static void main(String[] args) {
        String url = "jdbc:oracle:thin:@(description=(retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1521)(host=adb.eu-amsterdam-1.oraclecloud.com))(connect_data=(service_name=g49f31b19d33266_keycloakauth_high.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))";
        Properties props = new Properties();
        props.setProperty("user", "keycloak_user");
        props.setProperty("password", "Keycloak123!");
        props.setProperty("javax.net.ssl.trustStore", "truststore.jks");
        props.setProperty("javax.net.ssl.trustStorePassword", "changeit");

        try (Connection conn = DriverManager.getConnection(url, props);
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery("SELECT 1 FROM DUAL")) {

            if (rs.next()) {
                System.out.println("✅ JDBC TLS connection successful! Query result: " + rs.getInt(1));
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
