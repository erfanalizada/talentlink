import oracledb

DB_USER = "keycloak_user"
DB_PASSWORD = "Keycloak123!"
CONNECT_STRING = '(description=(retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1521)(host=adb.eu-amsterdam-1.oraclecloud.com))(connect_data=(service_name=g49f31b19d33266_keycloakauth_high.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))'

def run_app():
    try:
        pool = oracledb.create_pool(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=CONNECT_STRING
        )
        with pool.acquire() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM DUAL")
                result = cursor.fetchone()
                if result:
                    print(f"✅ Connected successfully! Query result: {result[0]}")
    except oracledb.Error as e:
        print(f"❌ Oracle connection failed: {str(e)}")
    except Exception as e:
        import traceback
        traceback.print_exc() 

if __name__ == "__main__":
    run_app()
