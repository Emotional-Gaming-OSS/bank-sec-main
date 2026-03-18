"""
Initial database schema
Create all tables for BankSec Enterprise

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('username', sa.String(length=80), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password_hash', sa.String(length=200), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_modules', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('scores', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('current_scenario_id', sa.Integer(), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('preferences', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['current_scenario_id'], ['scenarios.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    
    # Create indexes for users
    op.create_index('ix_users_username_active', 'users', ['username', 'is_active'], unique=False)
    op.create_index('ix_users_email_active', 'users', ['email', 'is_active'], unique=False)
    op.create_index('ix_users_role_active', 'users', ['role', 'is_active'], unique=False)
    op.create_index('ix_users_last_login', 'users', ['last_login'], unique=False)
    
    # Create scenarios table
    op.create_table(
        'scenarios',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('difficulty', sa.String(length=20), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('estimated_time', sa.Integer(), nullable=False),
        sa.Column('max_score', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('initial_state', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('correct_actions', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('attack_indicators', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('educational_content', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for scenarios
    op.create_index('ix_scenarios_difficulty_active', 'scenarios', ['difficulty', 'is_active'], unique=False)
    op.create_index('ix_scenarios_category_active', 'scenarios', ['category', 'is_active'], unique=False)
    op.create_index('ix_scenarios_created_by', 'scenarios', ['created_by'], unique=False)
    op.create_index('ix_scenarios_title_gin', 'scenarios', ['title'], unique=False, postgresql_using='gin')
    
    # Create scenario_attempts table
    op.create_table(
        'scenario_attempts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('scenario_id', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('time_taken', sa.Integer(), nullable=True),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('completed', sa.Boolean(), nullable=False),
        sa.Column('current_step', sa.Integer(), nullable=False),
        sa.Column('actions_taken', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('flags_detected', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('mistakes_made', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['scenario_id'], ['scenarios.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for scenario_attempts
    op.create_index('ix_attempts_user_scenario', 'scenario_attempts', ['user_id', 'scenario_id'], unique=False)
    op.create_index('ix_attempts_user_completed', 'scenario_attempts', ['user_id', 'completed'], unique=False)
    op.create_index('ix_attempts_scenario_completed', 'scenario_attempts', ['scenario_id', 'completed'], unique=False)
    op.create_index('ix_attempts_start_time', 'scenario_attempts', ['start_time'], unique=False)
    op.create_index('ix_attempts_score', 'scenario_attempts', ['score'], unique=False)
    op.create_index('ix_attempts_time_taken', 'scenario_attempts', ['time_taken'], unique=False)
    
    # Create transactions table
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('transaction_id', sa.String(length=50), nullable=False),
        sa.Column('scenario_id', sa.Integer(), nullable=True),
        sa.Column('from_account', sa.String(length=50), nullable=False),
        sa.Column('to_account', sa.String(length=50), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('is_suspicious', sa.Boolean(), nullable=False),
        sa.Column('flags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('verification_required', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['scenario_id'], ['scenarios.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('transaction_id')
    )
    
    # Create indexes for transactions
    op.create_index('ix_transactions_scenario_status', 'transactions', ['scenario_id', 'status'], unique=False)
    op.create_index('ix_transactions_suspicious', 'transactions', ['is_suspicious'], unique=False)
    op.create_index('ix_transactions_timestamp', 'transactions', ['created_at'], unique=False)
    op.create_index('ix_transactions_amount', 'transactions', ['amount'], unique=False)
    op.create_index('ix_transactions_from_account', 'transactions', ['from_account'], unique=False)
    op.create_index('ix_transactions_to_account', 'transactions', ['to_account'], unique=False)
    
    # Create security_logs table
    op.create_table(
        'security_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for security_logs
    op.create_index('ix_security_logs_user_event', 'security_logs', ['user_id', 'event_type'], unique=False)
    op.create_index('ix_security_logs_timestamp', 'security_logs', ['created_at'], unique=False)
    op.create_index('ix_security_logs_severity', 'security_logs', ['severity'], unique=False)
    op.create_index('ix_security_logs_ip', 'security_logs', ['ip_address'], unique=False)
    op.create_index('ix_security_logs_event_time', 'security_logs', ['event_type', 'created_at'], unique=False)
    
    # Create user_sessions table
    op.create_table(
        'user_sessions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('session_token', sa.String(length=500), nullable=False),
        sa.Column('refresh_token', sa.String(length=500), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('refresh_token'),
        sa.UniqueConstraint('session_token')
    )
    
    # Create indexes for user_sessions
    op.create_index('ix_sessions_user_active', 'user_sessions', ['user_id', 'is_active'], unique=False)
    op.create_index('ix_sessions_token_active', 'user_sessions', ['session_token', 'is_active'], unique=False)
    op.create_index('ix_sessions_expires', 'user_sessions', ['expires_at'], unique=False)


def downgrade() -> None:
    # Drop all tables in reverse order
    op.drop_table('user_sessions')
    op.drop_table('security_logs')
    op.drop_table('transactions')
    op.drop_table('scenario_attempts')
    op.drop_table('scenarios')
    op.drop_table('users')