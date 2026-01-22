"""Add performance indexes for common queries

Revision ID: 002_add_performance_indexes
Revises: 001_initial_schema
Create Date: 2026-01-21

Indexes added based on query pattern analysis:
- deal_members.user_id: For finding user's deal memberships
- file_shares.shared_with: For finding files shared with a user
- audit_log.actor_id: For filtering audit entries by actor
- audit_log.action: For filtering by action type
- activity.actor_id: For filtering activities by actor
- activity.action: For filtering by action type
- agent_runs.user_id: For finding user's agent runs
- deals.updated_at: For sorting deals by last update
- alerts.user_id: For finding user's alerts
- alerts.deal_id: For finding alerts by deal
- alerts.is_active: For filtering active/inactive alerts
- alert_matches.alert_id: For finding matches for an alert
- alert_matches.notified: For finding unnotified matches
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '002_add_performance_indexes'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # deal_members indexes
    op.execute("CREATE INDEX ix_deal_members_user_id ON deal_members (user_id)")

    # file_shares indexes
    op.execute("CREATE INDEX ix_file_shares_shared_with ON file_shares (shared_with)")

    # audit_log indexes (supplement existing entity index)
    op.execute("CREATE INDEX ix_audit_log_actor_id ON audit_log (actor_id)")
    op.execute("CREATE INDEX ix_audit_log_action ON audit_log (action)")

    # activity indexes (supplement existing deal_id and created_at indexes)
    op.execute("CREATE INDEX ix_activity_actor_id ON activity (actor_id)")
    op.execute("CREATE INDEX ix_activity_action ON activity (action)")

    # agent_runs indexes
    op.execute("CREATE INDEX ix_agent_runs_user_id ON agent_runs (user_id)")

    # deals indexes (for sorting by last update)
    op.execute("CREATE INDEX ix_deals_updated_at ON deals (updated_at DESC NULLS LAST)")

    # alerts indexes (if table exists)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'alerts') THEN
                EXECUTE 'CREATE INDEX IF NOT EXISTS ix_alerts_user_id ON alerts (user_id)';
                EXECUTE 'CREATE INDEX IF NOT EXISTS ix_alerts_deal_id ON alerts (deal_id)';
                EXECUTE 'CREATE INDEX IF NOT EXISTS ix_alerts_is_active ON alerts (is_active)';
            END IF;
        END $$;
    """)

    # alert_matches indexes (if table exists)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'alert_matches') THEN
                EXECUTE 'CREATE INDEX IF NOT EXISTS ix_alert_matches_alert_id ON alert_matches (alert_id)';
                EXECUTE 'CREATE INDEX IF NOT EXISTS ix_alert_matches_notified ON alert_matches (notified)';
            END IF;
        END $$;
    """)


def downgrade() -> None:
    # Drop alert_matches indexes (if table exists)
    op.execute("DROP INDEX IF EXISTS ix_alert_matches_notified")
    op.execute("DROP INDEX IF EXISTS ix_alert_matches_alert_id")

    # Drop alerts indexes (if table exists)
    op.execute("DROP INDEX IF EXISTS ix_alerts_is_active")
    op.execute("DROP INDEX IF EXISTS ix_alerts_deal_id")
    op.execute("DROP INDEX IF EXISTS ix_alerts_user_id")

    # Drop deals index
    op.execute("DROP INDEX IF EXISTS ix_deals_updated_at")

    # Drop agent_runs index
    op.execute("DROP INDEX IF EXISTS ix_agent_runs_user_id")

    # Drop activity indexes
    op.execute("DROP INDEX IF EXISTS ix_activity_action")
    op.execute("DROP INDEX IF EXISTS ix_activity_actor_id")

    # Drop audit_log indexes
    op.execute("DROP INDEX IF EXISTS ix_audit_log_action")
    op.execute("DROP INDEX IF EXISTS ix_audit_log_actor_id")

    # Drop file_shares index
    op.execute("DROP INDEX IF EXISTS ix_file_shares_shared_with")

    # Drop deal_members index
    op.execute("DROP INDEX IF EXISTS ix_deal_members_user_id")
