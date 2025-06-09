"""Initial placeholder migration

Revision ID: initial_placeholder
Revises: 
Create Date: 2025-06-09

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'initial_placeholder'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # This is a placeholder migration that will be replaced when the user runs
    # alembic revision --autogenerate -m "Initial migration"
    pass


def downgrade() -> None:
    pass