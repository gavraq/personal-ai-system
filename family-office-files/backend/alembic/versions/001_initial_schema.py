"""Initial schema with all tables

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-01-21

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types using raw SQL
    op.execute("CREATE TYPE user_role AS ENUM ('admin', 'partner', 'viewer')")
    op.execute("CREATE TYPE deal_status AS ENUM ('draft', 'active', 'closed')")
    op.execute("CREATE TYPE file_source AS ENUM ('drive', 'gcs')")
    op.execute("CREATE TYPE file_permission AS ENUM ('view', 'edit')")
    op.execute("CREATE TYPE agent_type AS ENUM ('market_research', 'document_analysis', 'due_diligence', 'news_alerts')")
    op.execute("CREATE TYPE agent_status AS ENUM ('pending', 'running', 'completed', 'failed')")
    op.execute("CREATE TYPE message_role AS ENUM ('user', 'assistant', 'system')")

    # Create users table with enum type directly
    op.execute("""
        CREATE TABLE users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email VARCHAR(255) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role user_role NOT NULL DEFAULT 'viewer',
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """)
    op.execute("CREATE UNIQUE INDEX ix_users_email ON users (email)")

    # Create deals table
    op.execute("""
        CREATE TABLE deals (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            title VARCHAR(255) NOT NULL,
            description TEXT,
            status deal_status NOT NULL DEFAULT 'draft',
            created_by UUID NOT NULL REFERENCES users(id),
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """)

    # Create deal_members table
    op.execute("""
        CREATE TABLE deal_members (
            deal_id UUID NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            role_override VARCHAR(20),
            added_at TIMESTAMP NOT NULL DEFAULT NOW(),
            PRIMARY KEY (deal_id, user_id)
        )
    """)

    # Create files table
    op.execute("""
        CREATE TABLE files (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            deal_id UUID NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            source file_source NOT NULL,
            source_id VARCHAR(500),
            mime_type VARCHAR(100),
            size_bytes BIGINT,
            uploaded_by UUID NOT NULL REFERENCES users(id),
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
    """)

    # Create file_shares table
    op.execute("""
        CREATE TABLE file_shares (
            file_id UUID NOT NULL REFERENCES files(id) ON DELETE CASCADE,
            shared_with UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            permission file_permission NOT NULL DEFAULT 'view',
            shared_at TIMESTAMP NOT NULL DEFAULT NOW(),
            PRIMARY KEY (file_id, shared_with)
        )
    """)

    # Create google_connections table
    op.execute("""
        CREATE TABLE google_connections (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
            access_token TEXT,
            refresh_token TEXT,
            token_expiry TIMESTAMP,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """)

    # Create agent_runs table
    op.execute("""
        CREATE TABLE agent_runs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            deal_id UUID NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
            user_id UUID NOT NULL REFERENCES users(id),
            agent_type agent_type NOT NULL,
            input JSONB NOT NULL,
            output JSONB,
            status agent_status NOT NULL DEFAULT 'pending',
            error_message TEXT,
            started_at TIMESTAMP NOT NULL DEFAULT NOW(),
            completed_at TIMESTAMP
        )
    """)

    # Create agent_messages table
    op.execute("""
        CREATE TABLE agent_messages (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            agent_run_id UUID NOT NULL REFERENCES agent_runs(id) ON DELETE CASCADE,
            role message_role NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
    """)

    # Create audit_log table
    op.execute("""
        CREATE TABLE audit_log (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            actor_id UUID NOT NULL REFERENCES users(id),
            action VARCHAR(50) NOT NULL,
            entity_type VARCHAR(50) NOT NULL,
            entity_id UUID NOT NULL,
            old_value JSONB,
            new_value JSONB,
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
    """)

    # Create activity table
    op.execute("""
        CREATE TABLE activity (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            deal_id UUID NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
            actor_id UUID NOT NULL REFERENCES users(id),
            action VARCHAR(50) NOT NULL,
            details JSONB,
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
    """)

    # Create indexes for common queries
    op.execute("CREATE INDEX ix_deals_status ON deals (status)")
    op.execute("CREATE INDEX ix_deals_created_by ON deals (created_by)")
    op.execute("CREATE INDEX ix_files_deal_id ON files (deal_id)")
    op.execute("CREATE INDEX ix_agent_runs_deal_id ON agent_runs (deal_id)")
    op.execute("CREATE INDEX ix_agent_runs_status ON agent_runs (status)")
    op.execute("CREATE INDEX ix_activity_deal_id ON activity (deal_id)")
    op.execute("CREATE INDEX ix_activity_created_at ON activity (created_at)")
    op.execute("CREATE INDEX ix_audit_log_entity ON audit_log (entity_type, entity_id)")
    op.execute("CREATE INDEX ix_audit_log_created_at ON audit_log (created_at)")


def downgrade() -> None:
    # Drop indexes
    op.execute("DROP INDEX IF EXISTS ix_audit_log_created_at")
    op.execute("DROP INDEX IF EXISTS ix_audit_log_entity")
    op.execute("DROP INDEX IF EXISTS ix_activity_created_at")
    op.execute("DROP INDEX IF EXISTS ix_activity_deal_id")
    op.execute("DROP INDEX IF EXISTS ix_agent_runs_status")
    op.execute("DROP INDEX IF EXISTS ix_agent_runs_deal_id")
    op.execute("DROP INDEX IF EXISTS ix_files_deal_id")
    op.execute("DROP INDEX IF EXISTS ix_deals_created_by")
    op.execute("DROP INDEX IF EXISTS ix_deals_status")
    op.execute("DROP INDEX IF EXISTS ix_users_email")

    # Drop tables in reverse order (respecting foreign keys)
    op.execute("DROP TABLE IF EXISTS activity CASCADE")
    op.execute("DROP TABLE IF EXISTS audit_log CASCADE")
    op.execute("DROP TABLE IF EXISTS agent_messages CASCADE")
    op.execute("DROP TABLE IF EXISTS agent_runs CASCADE")
    op.execute("DROP TABLE IF EXISTS google_connections CASCADE")
    op.execute("DROP TABLE IF EXISTS file_shares CASCADE")
    op.execute("DROP TABLE IF EXISTS files CASCADE")
    op.execute("DROP TABLE IF EXISTS deal_members CASCADE")
    op.execute("DROP TABLE IF EXISTS deals CASCADE")
    op.execute("DROP TABLE IF EXISTS users CASCADE")

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS message_role")
    op.execute("DROP TYPE IF EXISTS agent_status")
    op.execute("DROP TYPE IF EXISTS agent_type")
    op.execute("DROP TYPE IF EXISTS file_permission")
    op.execute("DROP TYPE IF EXISTS file_source")
    op.execute("DROP TYPE IF EXISTS deal_status")
    op.execute("DROP TYPE IF EXISTS user_role")
