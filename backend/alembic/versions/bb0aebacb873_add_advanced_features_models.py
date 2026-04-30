"""Add advanced features models

Revision ID: bb0aebacb873
Revises: 19aba6d08f08
Create Date: 2026-04-30 01:49:21.515956

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bb0aebacb873'
down_revision: Union[str, Sequence[str], None] = '19aba6d08f08'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
