"""
Tests for Google integration endpoints (feat-13)
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timedelta
from passlib.context import CryptContext

from app.models.user import User
from app.models.google import GoogleConnection

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


class TestGoogleOAuthInitiation:
    """Tests for feat-13: Google OAuth initiation"""

    def test_get_auth_url_returns_google_oauth_url(self, client, test_db):
        """Get auth URL returns Google OAuth URL with correct parameters"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())
        user = User(
            email="test@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(user)
        db.commit()

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "test@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Get OAuth URL - patch at the router module level
        with patch('app.routers.integrations.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(
                google_client_id="test-client-id",
                google_client_secret="test-secret",
                google_redirect_uri="http://localhost:8000/api/integrations/google/callback"
            )
            response = client.get(
                "/api/integrations/google/auth",
                headers={"Authorization": f"Bearer {token}"}
            )

        assert response.status_code == 200
        data = response.json()
        assert "authorization_url" in data
        assert "accounts.google.com" in data["authorization_url"]
        assert "client_id=" in data["authorization_url"]
        assert "redirect_uri=" in data["authorization_url"]
        assert "scope=" in data["authorization_url"]

    def test_get_auth_url_without_credentials_returns_401(self, client, test_db):
        """Get auth URL without authentication returns 401"""
        response = client.get("/api/integrations/google/auth")
        assert response.status_code == 401 or response.status_code == 403


class TestGoogleOAuthCallback:
    """Tests for feat-13: Google OAuth callback"""

    @pytest.mark.asyncio
    def test_callback_stores_tokens_in_database(self, client, test_db):
        """OAuth callback stores refresh token in google_connections table"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())
        user = User(
            email="callback@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Mock the token exchange
        mock_tokens = {
            "access_token": "test-access-token",
            "refresh_token": "test-refresh-token",
            "expires_in": 3600
        }

        with patch('app.routers.integrations.exchange_code_for_tokens', new_callable=AsyncMock) as mock_exchange:
            mock_exchange.return_value = mock_tokens

            response = client.get(
                f"/api/integrations/google/callback?code=test-code&state={user.id}",
                follow_redirects=False
            )

        assert response.status_code == 302
        assert "google=connected" in response.headers.get("location", "")

        # Verify token stored in database
        db.expire_all()
        connection = db.query(GoogleConnection).filter(
            GoogleConnection.user_id == user.id
        ).first()

        assert connection is not None
        assert connection.refresh_token == "test-refresh-token"
        assert connection.access_token == "test-access-token"
        assert connection.token_expiry is not None

    def test_callback_with_invalid_state_returns_400(self, client, test_db):
        """OAuth callback with invalid state returns 400"""
        response = client.get(
            "/api/integrations/google/callback?code=test-code&state=invalid-uuid",
            follow_redirects=False
        )
        assert response.status_code == 400

    def test_callback_with_nonexistent_user_returns_400(self, client, test_db):
        """OAuth callback with nonexistent user returns 400"""
        import uuid
        fake_user_id = str(uuid.uuid4())
        response = client.get(
            f"/api/integrations/google/callback?code=test-code&state={fake_user_id}",
            follow_redirects=False
        )
        assert response.status_code == 400


class TestGoogleDisconnect:
    """Tests for feat-13: Google disconnect"""

    def test_disconnect_removes_stored_tokens(self, client, test_db):
        """Disconnect removes stored tokens from database"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create user
        user = User(
            email="disconnect@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create Google connection
        connection = GoogleConnection(
            user_id=user.id,
            access_token="test-access-token",
            refresh_token="test-refresh-token",
            token_expiry=datetime.utcnow() + timedelta(hours=1)
        )
        db.add(connection)
        db.commit()

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "disconnect@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Disconnect
        with patch('httpx.AsyncClient.post', new_callable=AsyncMock):
            response = client.delete(
                "/api/integrations/google",
                headers={"Authorization": f"Bearer {token}"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["disconnected"] is True

        # Verify token removed from database
        db.expire_all()
        connection = db.query(GoogleConnection).filter(
            GoogleConnection.user_id == user.id
        ).first()
        assert connection is None

    def test_disconnect_without_connection_returns_404(self, client, test_db):
        """Disconnect without existing connection returns 404"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create user without Google connection
        user = User(
            email="noconnection@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(user)
        db.commit()

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "noconnection@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Try to disconnect
        response = client.delete(
            "/api/integrations/google",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404


class TestGoogleConnectionStatus:
    """Tests for feat-13: Google connection status"""

    def test_status_returns_connected_when_tokens_exist(self, client, test_db):
        """Status returns connected=true when tokens exist"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create user
        user = User(
            email="status@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create Google connection
        connection = GoogleConnection(
            user_id=user.id,
            access_token="test-access-token",
            refresh_token="test-refresh-token",
            token_expiry=datetime.utcnow() + timedelta(hours=1)
        )
        db.add(connection)
        db.commit()

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "status@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Get status
        with patch('app.routers.integrations.get_google_user_email', new_callable=AsyncMock) as mock_email:
            mock_email.return_value = "google@example.com"
            response = client.get(
                "/api/integrations/google/status",
                headers={"Authorization": f"Bearer {token}"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["connected"] is True
        assert data["email"] == "google@example.com"

    def test_status_returns_not_connected_when_no_tokens(self, client, test_db):
        """Status returns connected=false when no tokens"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create user without Google connection
        user = User(
            email="nostatus@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(user)
        db.commit()

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "nostatus@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Get status
        response = client.get(
            "/api/integrations/google/status",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["connected"] is False


class TestTokenRefresh:
    """Tests for feat-13: Token refresh logic"""

    def test_expired_token_gets_refreshed(self, client, test_db):
        """Expired access token gets refreshed when checking status"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create user
        user = User(
            email="refresh@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create Google connection with expired token
        connection = GoogleConnection(
            user_id=user.id,
            access_token="old-access-token",
            refresh_token="test-refresh-token",
            token_expiry=datetime.utcnow() - timedelta(hours=1)  # Expired
        )
        db.add(connection)
        db.commit()

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "refresh@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Mock the token refresh
        mock_tokens = {
            "access_token": "new-access-token",
            "expires_in": 3600
        }

        with patch('app.routers.integrations.refresh_access_token', new_callable=AsyncMock) as mock_refresh:
            mock_refresh.return_value = mock_tokens
            with patch('app.routers.integrations.get_google_user_email', new_callable=AsyncMock) as mock_email:
                mock_email.return_value = "refreshed@example.com"
                response = client.get(
                    "/api/integrations/google/status",
                    headers={"Authorization": f"Bearer {token}"}
                )

        assert response.status_code == 200

        # Verify token was refreshed
        mock_refresh.assert_called_once()

        # Check database was updated
        db.expire_all()
        connection = db.query(GoogleConnection).filter(
            GoogleConnection.user_id == user.id
        ).first()
        assert connection.access_token == "new-access-token"
