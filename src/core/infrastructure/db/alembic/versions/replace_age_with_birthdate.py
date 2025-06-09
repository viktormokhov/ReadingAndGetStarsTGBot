"""Replace age with birthdate

Revision ID: replace_age_with_birthdate
Revises: 
Create Date: 2025-06-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import date, datetime, timedelta


# revision identifiers, used by Alembic.
revision = 'replace_age_with_birthdate'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add birthdate column
    op.add_column('users', sa.Column('birthdate', sa.Date(), nullable=True))
    
    # Convert age to birthdate (approximate)
    # This is an approximation - we set birthdate to January 1st of the year that would result in the current age
    conn = op.get_bind()
    
    # Get current year
    current_year = datetime.now().year
    
    # Get all users with age
    users = conn.execute(sa.text("SELECT id, age FROM users WHERE age IS NOT NULL")).fetchall()
    
    # Update birthdate based on age
    for user_id, age in users:
        if age is not None:
            # Calculate birth year (approximate)
            birth_year = current_year - age
            # Set birthdate to January 1st of birth year
            birthdate = date(birth_year, 1, 1)
            conn.execute(
                sa.text("UPDATE users SET birthdate = :birthdate WHERE id = :id"),
                {"birthdate": birthdate, "id": user_id}
            )
    
    # Drop age column
    op.drop_column('users', 'age')


def downgrade():
    # Add age column
    op.add_column('users', sa.Column('age', sa.Integer(), nullable=True))
    
    # Convert birthdate to age
    conn = op.get_bind()
    
    # Get current date
    today = date.today()
    
    # Get all users with birthdate
    users = conn.execute(sa.text("SELECT id, birthdate FROM users WHERE birthdate IS NOT NULL")).fetchall()
    
    # Update age based on birthdate
    for user_id, birthdate in users:
        if birthdate is not None:
            # Calculate age
            age = today.year - birthdate.year
            if (today.month, today.day) < (birthdate.month, birthdate.day):
                age -= 1
            conn.execute(
                sa.text("UPDATE users SET age = :age WHERE id = :id"),
                {"age": age, "id": user_id}
            )
    
    # Drop birthdate column
    op.drop_column('users', 'birthdate')