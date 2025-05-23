"""added topic description

Revision ID: 4ef6f7bc94f6
Revises: 927577b68b2e
Create Date: 2025-05-08 03:10:59.039062

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4ef6f7bc94f6'
down_revision = '927577b68b2e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('topic', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('topic', schema=None) as batch_op:
        batch_op.drop_column('description')

    # ### end Alembic commands ###
