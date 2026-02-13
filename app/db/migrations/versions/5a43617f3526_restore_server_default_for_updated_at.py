"""restore server_default for updated_at

Revision ID: 5a43617f3526
Revises: 218d794c8095
Create Date: 2026-02-13 01:00:45.360141

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5a43617f3526'
down_revision: Union[str, Sequence[str], None] = '218d794c8095'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
