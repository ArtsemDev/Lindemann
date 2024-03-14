"""empty message

Revision ID: 9766c92faec7
Revises: ca0d7f0e0c7a
Create Date: 2024-03-11 18:02:42.929357

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9766c92faec7'
down_revision: Union[str, None] = 'ca0d7f0e0c7a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bot_tasks', sa.Column('user_id', sa.BIGINT(), nullable=False))
    op.create_foreign_key(None, 'bot_tasks', 'bot_users', ['user_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'bot_tasks', type_='foreignkey')
    op.drop_column('bot_tasks', 'user_id')
    # ### end Alembic commands ###
