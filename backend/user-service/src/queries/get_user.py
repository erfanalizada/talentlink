"""
Get User Query and Handler
"""
from dataclasses import dataclass
from typing import Optional

import sys
sys.path.append('../../shared')
from cqrs_base import Query, QueryHandler, Result
from database import Database

from ..models.user import User


@dataclass
class GetUserByIdQuery(Query):
    """Query to get user by ID"""
    user_id: str


@dataclass
class GetUserByKeycloakIdQuery(Query):
    """Query to get user by Keycloak ID"""
    keycloak_id: str


@dataclass
class GetUserByEmailQuery(Query):
    """Query to get user by email"""
    email: str


class GetUserByIdHandler(QueryHandler[GetUserByIdQuery, Result]):
    """Handler for GetUserByIdQuery"""

    def __init__(self, db: Database):
        self.db = db

    async def handle(self, query: GetUserByIdQuery) -> Result:
        """Get user by ID"""
        try:
            with self.db.get_db_session() as session:
                user = session.query(User).filter(User.id == query.user_id).first()

                if not user:
                    return Result.fail(f"User not found: {query.user_id}")

                return Result.ok(user.to_dict())

        except Exception as e:
            return Result.fail(f"Failed to get user: {str(e)}")


class GetUserByKeycloakIdHandler(QueryHandler[GetUserByKeycloakIdQuery, Result]):
    """Handler for GetUserByKeycloakIdQuery"""

    def __init__(self, db: Database):
        self.db = db

    async def handle(self, query: GetUserByKeycloakIdQuery) -> Result:
        """Get user by Keycloak ID"""
        try:
            with self.db.get_db_session() as session:
                user = session.query(User).filter(User.keycloak_id == query.keycloak_id).first()

                if not user:
                    return Result.fail(f"User not found with Keycloak ID: {query.keycloak_id}")

                return Result.ok(user.to_dict())

        except Exception as e:
            return Result.fail(f"Failed to get user: {str(e)}")


class GetUserByEmailHandler(QueryHandler[GetUserByEmailQuery, Result]):
    """Handler for GetUserByEmailQuery"""

    def __init__(self, db: Database):
        self.db = db

    async def handle(self, query: GetUserByEmailQuery) -> Result:
        """Get user by email"""
        try:
            with self.db.get_db_session() as session:
                user = session.query(User).filter(User.email == query.email).first()

                if not user:
                    return Result.fail(f"User not found with email: {query.email}")

                return Result.ok(user.to_dict())

        except Exception as e:
            return Result.fail(f"Failed to get user: {str(e)}")
