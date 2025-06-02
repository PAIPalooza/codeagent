"""add_download_url_to_projects

Revision ID: 5035b2cf0f19
Revises: 3b89b07f7778
Create Date: 2025-05-31 16:53:25.406612

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5035b2cf0f19'
down_revision: Union[str, None] = '3b89b07f7778'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('projects', 
                 sa.Column('download_url', sa.String(length=512), nullable=True, 
                         comment='URL to download the generated ZIP file'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('projects', 'download_url')
