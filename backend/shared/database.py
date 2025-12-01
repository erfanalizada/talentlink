"""
Database utilities for PostgreSQL
"""
import os
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()


class Database:
    """Database connection manager"""

    def __init__(self, database_url: str = None, db_name: str = "talentlink"):
        self.database_url = database_url or os.getenv("DATABASE_URL")

        if not self.database_url:
            logger.warning(f"DATABASE_URL not set, using default for {db_name}")
            self.database_url = f"postgresql://postgres:postgres@localhost:5432/{db_name}"

        # Create SQLAlchemy engine
        self.engine = create_engine(
            self.database_url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )

        # Create session factory
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        logger.info(f"Database engine created for: {db_name}")

    @contextmanager
    def get_db_connection(self):
        """Get raw psycopg2 connection (for simple queries)"""
        conn = None
        try:
            conn = psycopg2.connect(self.database_url)
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    @contextmanager
    def get_db_session(self):
        """Get SQLAlchemy session (for ORM queries)"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Session error: {e}")
            raise
        finally:
            session.close()

    def execute_query(self, query: str, params: dict = None):
        """Execute a query and return results"""
        with self.get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params or {})
                try:
                    return cur.fetchall()
                except:
                    return None

    def execute_command(self, command: str, params: dict = None):
        """Execute a command (INSERT, UPDATE, DELETE)"""
        with self.get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(command, params or {})
                return cur.rowcount

    def init_schema(self):
        """Initialize database schema"""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database schema initialized")

    def drop_schema(self):
        """Drop all tables (for testing)"""
        Base.metadata.drop_all(bind=self.engine)
        logger.warning("Database schema dropped")


def parse_database_url(url: str = None):
    """Parse DATABASE_URL into components"""
    url = url or os.getenv("DATABASE_URL")
    if not url:
        return {
            "host": "localhost",
            "port": 5432,
            "database": "talentlink",
            "user": "postgres",
            "password": "postgres"
        }

    # Parse PostgreSQL URL
    import urllib.parse as urlparse
    urlparse.uses_netloc.append("postgres")
    parsed = urlparse.urlparse(url)

    return {
        "host": parsed.hostname,
        "port": parsed.port or 5432,
        "database": parsed.path[1:] if parsed.path else "talentlink",
        "user": parsed.username,
        "password": parsed.password
    }
