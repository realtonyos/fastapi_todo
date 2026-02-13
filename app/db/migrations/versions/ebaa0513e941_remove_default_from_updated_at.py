"""remove default from updated_at

Revision ID: ebaa0513e941
Revises: 81c9cf8865ff
Create Date: 2026-02-12 23:44:24.462434

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ebaa0513e941'
down_revision: Union[str, Sequence[str], None] = '81c9cf8865ff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Убираем DEFAULT у updated_at в таблице users
    op.alter_column('users', 'updated_at',
                    existing_type=sa.DateTime(),
                    server_default=None,
                    existing_nullable=False)
    
    # Убираем DEFAULT у updated_at в таблице tasks
    op.alter_column('tasks', 'updated_at',
                    existing_type=sa.DateTime(),
                    server_default=None,
                    existing_nullable=False)


def downgrade() -> None:
    # Возвращаем DEFAULT обратно (на случай отката)
    op.alter_column('users', 'updated_at',
                    existing_type=sa.DateTime(),
                    server_default=sa.text('now()'),
                    existing_nullable=False)
    
    op.alter_column('tasks', 'updated_at',
                    existing_type=sa.DateTime(),
                    server_default=sa.text('now()'),
                    existing_nullable=False)
