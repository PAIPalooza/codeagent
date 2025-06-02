"""add_features_field_to_projects

Revision ID: 6a723c60c15d
Revises: 5035b2cf0f19
Create Date: 2025-05-31 23:20:45.582968

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6a723c60c15d'
down_revision: Union[str, None] = '5035b2cf0f19'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add features column (JSON type for SQLite compatibility)
    op.add_column('projects', sa.Column('features', sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove features column
    op.drop_column('projects', 'features')
