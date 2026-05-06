"""Add DB constraints for revenue

Revision ID: 40ae4a9db2bc
Revises: 67f04a4e85e1
Create Date: 2026-05-06 01:36:21.216152

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '40ae4a9db2bc'
down_revision: Union[str, Sequence[str], None] = '67f04a4e85e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("post_queue", schema=None) as batch_op:
        batch_op.create_check_constraint(
            "check_revenue_positive",
            "revenue >= 0"
        )

def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("post_queue", schema=None) as batch_op:
        batch_op.drop_constraint("check_revenue_positive", type_="check")
