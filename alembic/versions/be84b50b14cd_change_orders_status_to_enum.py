"""change_orders_status_to_enum

Revision ID: be84b50b14cd
Revises: 734a241af81a
Create Date: 2026-09-07 22:14:53.689198

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'be84b50b14cd'
down_revision: Union[str, Sequence[str], None] = '734a241af81a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    orderstatus = sa.Enum(
        'PENDING', 'CONFIRMED', 'COOKING', 'READY', 'DELIVERED', 'CANCELLED',
        name='orderstatus',
    )
    orderstatus.create(op.get_bind(), checkfirst=True)
    op.alter_column(
        'orders', 'status',
        existing_type=sa.VARCHAR(length=20),
        type_=orderstatus,
        existing_nullable=False,
        postgresql_using='status::orderstatus',
    )


def downgrade() -> None:
    op.alter_column(
        'orders', 'status',
        existing_type=sa.Enum(
            'PENDING', 'CONFIRMED', 'COOKING', 'READY', 'DELIVERED', 'CANCELLED',
            name='orderstatus',
        ),
        type_=sa.VARCHAR(length=20),
        existing_nullable=False,
        postgresql_using='status::varchar',
    )
    sa.Enum(name='orderstatus').drop(op.get_bind(), checkfirst=True)
