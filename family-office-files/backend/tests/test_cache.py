"""
Tests for Redis caching functionality (Phase 6.6)
"""
import pytest
from uuid import uuid4
from datetime import datetime
from passlib.context import CryptContext

from app.models.user import User
from app.models.deal import Deal, DealMember
from app.core.cache import (
    cache_user,
    get_cached_user,
    invalidate_user_cache,
    get_cached_user_id_by_email,
    cache_deal,
    get_cached_deal,
    invalidate_deal_cache,
    cache_deal_membership,
    get_cached_deal_membership,
    invalidate_deal_membership_cache,
    invalidate_user_memberships_cache,
    get_cache_stats,
    clear_all_cache,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


class TestUserCaching:
    """Tests for user caching functions"""

    def test_cache_user_and_retrieve(self, test_redis):
        """Cache user data and retrieve it"""
        if test_redis is None:
            pytest.skip("Redis not available")

        user_id = uuid4()
        user_data = {
            "id": str(user_id),
            "email": "test@example.com",
            "role": "admin",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Cache the user
        result = cache_user(user_id, user_data)
        assert result is True

        # Retrieve from cache
        cached = get_cached_user(user_id)
        assert cached is not None
        assert cached["id"] == str(user_id)
        assert cached["email"] == "test@example.com"
        assert cached["role"] == "admin"

    def test_cache_miss_returns_none(self, test_redis):
        """Cache miss returns None"""
        if test_redis is None:
            pytest.skip("Redis not available")

        user_id = uuid4()
        cached = get_cached_user(user_id)
        assert cached is None

    def test_invalidate_user_cache(self, test_redis):
        """Invalidate user cache removes entry"""
        if test_redis is None:
            pytest.skip("Redis not available")

        user_id = uuid4()
        user_data = {
            "id": str(user_id),
            "email": "invalidate@example.com",
            "role": "partner",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Cache the user
        cache_user(user_id, user_data)
        assert get_cached_user(user_id) is not None

        # Invalidate
        result = invalidate_user_cache(user_id, "invalidate@example.com")
        assert result is True

        # Verify removed
        assert get_cached_user(user_id) is None
        assert get_cached_user_id_by_email("invalidate@example.com") is None

    def test_email_to_id_lookup(self, test_redis):
        """Email to user ID lookup works"""
        if test_redis is None:
            pytest.skip("Redis not available")

        user_id = uuid4()
        user_data = {
            "id": str(user_id),
            "email": "lookup@example.com",
            "role": "viewer",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        cache_user(user_id, user_data)

        # Lookup by email
        found_id = get_cached_user_id_by_email("lookup@example.com")
        assert found_id == user_id


class TestDealCaching:
    """Tests for deal caching functions"""

    def test_cache_deal_and_retrieve(self, test_redis):
        """Cache deal data and retrieve it"""
        if test_redis is None:
            pytest.skip("Redis not available")

        deal_id = uuid4()
        deal_data = {
            "id": str(deal_id),
            "title": "Test Deal",
            "description": "A test deal",
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Cache the deal
        result = cache_deal(deal_id, deal_data)
        assert result is True

        # Retrieve from cache
        cached = get_cached_deal(deal_id)
        assert cached is not None
        assert cached["title"] == "Test Deal"
        assert cached["status"] == "active"

    def test_invalidate_deal_cache(self, test_redis):
        """Invalidate deal cache removes entry"""
        if test_redis is None:
            pytest.skip("Redis not available")

        deal_id = uuid4()
        deal_data = {
            "id": str(deal_id),
            "title": "To Invalidate",
            "status": "draft",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        cache_deal(deal_id, deal_data)
        assert get_cached_deal(deal_id) is not None

        invalidate_deal_cache(deal_id)
        assert get_cached_deal(deal_id) is None


class TestDealMembershipCaching:
    """Tests for deal membership caching functions"""

    def test_cache_membership_and_retrieve(self, test_redis):
        """Cache membership and retrieve it"""
        if test_redis is None:
            pytest.skip("Redis not available")

        deal_id = uuid4()
        user_id = uuid4()

        # Cache membership
        result = cache_deal_membership(deal_id, user_id, is_member=True, role_override="partner")
        assert result is True

        # Retrieve
        cached = get_cached_deal_membership(deal_id, user_id)
        assert cached is not None
        assert cached["is_member"] is True
        assert cached["role_override"] == "partner"

    def test_cache_non_membership(self, test_redis):
        """Cache non-membership (user not in deal)"""
        if test_redis is None:
            pytest.skip("Redis not available")

        deal_id = uuid4()
        user_id = uuid4()

        # Cache non-membership
        cache_deal_membership(deal_id, user_id, is_member=False)

        # Retrieve
        cached = get_cached_deal_membership(deal_id, user_id)
        assert cached is not None
        assert cached["is_member"] is False

    def test_invalidate_specific_membership(self, test_redis):
        """Invalidate specific user's membership in a deal"""
        if test_redis is None:
            pytest.skip("Redis not available")

        deal_id = uuid4()
        user_id_1 = uuid4()
        user_id_2 = uuid4()

        # Cache two memberships
        cache_deal_membership(deal_id, user_id_1, is_member=True)
        cache_deal_membership(deal_id, user_id_2, is_member=True)

        # Invalidate only user_1
        invalidate_deal_membership_cache(deal_id, user_id_1)

        # user_1 should be gone, user_2 should remain
        assert get_cached_deal_membership(deal_id, user_id_1) is None
        assert get_cached_deal_membership(deal_id, user_id_2) is not None

    def test_invalidate_all_deal_memberships(self, test_redis):
        """Invalidate all memberships for a deal"""
        if test_redis is None:
            pytest.skip("Redis not available")

        deal_id = uuid4()
        user_ids = [uuid4() for _ in range(3)]

        # Cache multiple memberships
        for uid in user_ids:
            cache_deal_membership(deal_id, uid, is_member=True)

        # Invalidate all for the deal
        invalidate_deal_membership_cache(deal_id)

        # All should be gone
        for uid in user_ids:
            assert get_cached_deal_membership(deal_id, uid) is None

    def test_invalidate_user_memberships_across_deals(self, test_redis):
        """Invalidate a user's memberships across all deals"""
        if test_redis is None:
            pytest.skip("Redis not available")

        user_id = uuid4()
        deal_ids = [uuid4() for _ in range(3)]

        # Cache memberships in multiple deals
        for did in deal_ids:
            cache_deal_membership(did, user_id, is_member=True)

        # Invalidate user's memberships across all deals
        invalidate_user_memberships_cache(user_id)

        # All should be gone
        for did in deal_ids:
            assert get_cached_deal_membership(did, user_id) is None


class TestCacheIntegration:
    """Integration tests for caching with API endpoints"""

    def test_user_lookup_uses_cache(self, client, test_db, test_redis):
        """User lookup in deps.py uses cache"""
        if test_redis is None:
            pytest.skip("Redis not available")

        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create user
        user = User(
            email="cached_user@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Login to get token
        login_response = client.post(
            "/api/auth/login",
            json={"email": "cached_user@test.com", "password": "password123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Make authenticated request - should populate cache
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

        # Verify user is now in cache
        cached = get_cached_user(user.id)
        assert cached is not None
        assert cached["email"] == "cached_user@test.com"

    def test_membership_add_invalidates_cache(self, client, test_db, test_redis):
        """Adding a deal member invalidates the cache"""
        if test_redis is None:
            pytest.skip("Redis not available")

        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin and target user
        admin = User(
            email="admin_inv@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        target_user = User(
            email="target@test.com",
            password_hash=get_password_hash("password123"),
            role="viewer"
        )
        db.add(admin)
        db.add(target_user)
        db.commit()
        db.refresh(admin)
        db.refresh(target_user)

        # Login as admin
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_inv@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create a deal
        deal_response = client.post(
            "/api/deals",
            json={"title": "Cache Test Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = deal_response.json()["id"]

        # Pre-populate cache with non-member status
        cache_deal_membership(deal_id, target_user.id, is_member=False)

        # Add member via API
        add_response = client.post(
            f"/api/deals/{deal_id}/members",
            json={"user_id": str(target_user.id)},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert add_response.status_code == 201

        # Cache should be invalidated (None means cache miss, will be refetched)
        cached = get_cached_deal_membership(deal_id, target_user.id)
        # After invalidation, it should be None (not the old False value)
        assert cached is None

    def test_role_change_invalidates_user_cache(self, client, test_db, test_redis):
        """Changing a user's role invalidates their cache"""
        if test_redis is None:
            pytest.skip("Redis not available")

        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin and target user
        admin = User(
            email="admin_role@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        target = User(
            email="target_role@test.com",
            password_hash=get_password_hash("password123"),
            role="viewer"
        )
        db.add(admin)
        db.add(target)
        db.commit()
        db.refresh(admin)
        db.refresh(target)

        # Pre-populate cache
        cache_user(target.id, {
            "id": str(target.id),
            "email": target.email,
            "role": "viewer",
            "created_at": target.created_at,
            "updated_at": target.updated_at
        })

        # Login as admin
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_role@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Change target's role
        response = client.put(
            f"/api/users/{target.id}/role",
            json={"role": "partner"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

        # User cache should be invalidated
        cached = get_cached_user(target.id)
        assert cached is None


class TestCacheStats:
    """Tests for cache statistics"""

    def test_get_cache_stats(self, test_redis):
        """Get cache statistics"""
        if test_redis is None:
            pytest.skip("Redis not available")

        stats = get_cache_stats()
        assert "hits" in stats or "error" in stats


class TestClearCache:
    """Tests for clearing all cache"""

    def test_clear_all_cache(self, test_redis):
        """Clear all cache entries"""
        if test_redis is None:
            pytest.skip("Redis not available")

        # Add some cache entries
        user_id = uuid4()
        deal_id = uuid4()

        cache_user(user_id, {
            "id": str(user_id),
            "email": "clear@test.com",
            "role": "viewer",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        cache_deal(deal_id, {
            "id": str(deal_id),
            "title": "Clear Test",
            "status": "draft",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        cache_deal_membership(deal_id, user_id, is_member=True)

        # Clear all
        result = clear_all_cache()
        assert result is True

        # Verify all cleared
        assert get_cached_user(user_id) is None
        assert get_cached_deal(deal_id) is None
        assert get_cached_deal_membership(deal_id, user_id) is None
