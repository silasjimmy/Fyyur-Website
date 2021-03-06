"""empty message

Revision ID: 4647cb8fe558
Revises: ad73c1f79731
Create Date: 2021-06-06 16:16:25.749278

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4647cb8fe558'
down_revision = 'ad73c1f79731'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venue', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    op.drop_column('venue', 'looking_for_talent')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venue', sa.Column('looking_for_talent', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('venue', 'seeking_talent')
    # ### end Alembic commands ###
