"""empty message

Revision ID: f6f7625d0e47
Revises: 76061b80da15
Create Date: 2018-06-18 18:08:53.799668

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f6f7625d0e47'
down_revision = '76061b80da15'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('indicator', sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=True))
    op.create_index(op.f('ix_indicator_is_deleted'), 'indicator', ['is_deleted'], unique=False)
    op.drop_constraint('indicator_name_product_id_key', 'indicator', type_='unique')
    op.create_unique_constraint('indicator_name_product_id_key', 'indicator', ['name', 'product_id', 'is_deleted'])
    op.create_index(op.f('ix_indicatorvalue_indicator_id'), 'indicatorvalue', ['indicator_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_indicatorvalue_indicator_id'), table_name='indicatorvalue')
    op.drop_constraint('indicator_name_product_id_key', 'indicator', type_='unique')
    op.create_unique_constraint('indicator_name_product_id_key', 'indicator', ['name', 'product_id'])
    op.drop_index(op.f('ix_indicator_is_deleted'), table_name='indicator')
    op.drop_column('indicator', 'is_deleted')
    # ### end Alembic commands ###
