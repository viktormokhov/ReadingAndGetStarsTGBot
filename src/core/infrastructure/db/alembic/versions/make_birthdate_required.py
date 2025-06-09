"""Make birthdate required

Revision ID: make_birthdate_required
Revises: replace_age_with_birthdate
Create Date: 2025-06-11 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import date, datetime

# revision identifiers, used by Alembic.
revision = 'make_birthdate_required'
down_revision = 'replace_age_with_birthdate'
branch_labels = None
depends_on = None


def upgrade():
    # Set a default birthdate for any NULL values
    # We'll use January 1, 2000 as a default birthdate
    conn = op.get_bind()
    
    # Get current year
    current_year = datetime.now().year
    
    # Default birthdate for users with NULL birthdate
    default_birthdate = date(2000, 1, 1)
    
    # Update users with NULL birthdate
    conn.execute(
        sa.text("UPDATE users SET birthdate = :birthdate WHERE birthdate IS NULL"),
        {"birthdate": default_birthdate}
    )
    
    # Make birthdate column non-nullable
    op.alter_column('users', 'birthdate', nullable=False)


def downgrade():
    # Make birthdate column nullable again
    op.alter_column('users', 'birthdate', nullable=True)