"""empty message

Revision ID: f8cf69635038
Revises: 4647cb8fe558
Create Date: 2021-06-06 16:46:47.592930

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f8cf69635038'
down_revision = '4647cb8fe558'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('show', sa.Column('start_time', sa.DateTime(), nullable=True))
    op.drop_column('show', 'time')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('show', sa.Column('time', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_column('show', 'start_time')
    # ### end Alembic commands ###
