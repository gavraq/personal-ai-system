"""
Pytest fixtures for testing
"""
import os
import pytest
import redis
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import get_db
from app.models.base import Base

# Import all models to register them with Base metadata
from app.models.user import User, UserRole
from app.models.deal import Deal, DealMember
from app.models.google import GoogleConnection


# Use test database (same PostgreSQL but different schema for isolation)
# The test database URL comes from environment or defaults to the Docker database
# Inside Docker container, use 'db' host; outside use 'localhost:5433'
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    os.getenv("DATABASE_URL", "postgresql://fop_user:fop_password@db:5432/fop_db")
)

# Redis URL for testing
TEST_REDIS_URL = os.getenv(
    "TEST_REDIS_URL",
    os.getenv("REDIS_URL", "redis://redis:6379/0")
)

engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency with test database"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def test_db():
    """Create test database tables before each test and clean up after"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Clean up - truncate all tables to reset state
    with engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE google_connections, deal_members, deals, users CASCADE"))
        conn.commit()


@pytest.fixture(scope="function")
def test_redis():
    """Clear Redis test data before each test"""
    try:
        redis_client = redis.from_url(TEST_REDIS_URL, decode_responses=True)
        # Clear blacklist keys
        for key in redis_client.scan_iter("blacklist:*"):
            redis_client.delete(key)
        for key in redis_client.scan_iter("user_blacklist:*"):
            redis_client.delete(key)
        yield redis_client
    except redis.RedisError:
        # Redis not available, skip cleanup
        yield None


@pytest.fixture(scope="function")
def client(test_db, test_redis):
    """Create test client with database override"""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
