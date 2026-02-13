"""restore server_default for updated_at

Revision ID: ea70e6868739
Revises: 5a43617f3526
Create Date: 2026-02-13 01:01:34.885390

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ea70e6868739'
down_revision: Union[str, Sequence[str], None] = '5a43617f3526'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Возвращаем server_default для updated_at в таблице users
    op.alter_column('users', 'updated_at',
                    existing_type=sa.DateTime(),
                    server_default=sa.text('now()'),
                    existing_nullable=False)
    
    # То же самое для tasks, если убрал
    op.alter_column('tasks', 'updated_at',
                    existing_type=sa.DateTime(),
                    server_default=sa.text('now()'),
                    existing_nullable=False)


def downgrade() -> None:
    # Убираем server_default (на случай отката)
    op.alter_column('users', 'updated_at',
                    existing_type=sa.DateTime(),
                    server_default=None,
                    existing_nullable=False)
    
    op.alter_column('tasks', 'updated_at',
                    existing_type=sa.DateTime(),
                    server_default=None,
                    existing_nullable=False)
