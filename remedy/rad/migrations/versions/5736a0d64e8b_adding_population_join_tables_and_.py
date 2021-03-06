"""Adding population join tables and backrefs.

Revision ID: 5736a0d64e8b
Revises: 4a09ad931d71
Create Date: 2015-07-30 22:35:57.458000

"""

# revision identifiers, used by Alembic.
revision = '5736a0d64e8b'
down_revision = '4a09ad931d71'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('userpopulation',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('population_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['population_id'], ['population.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'population_id')
    )
    op.create_table('resourcepopulation',
    sa.Column('resource_id', sa.Integer(), nullable=False),
    sa.Column('population_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['population_id'], ['population.id'], ),
    sa.ForeignKeyConstraint(['resource_id'], ['resource.id'], ),
    sa.PrimaryKeyConstraint('resource_id', 'population_id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('resourcepopulation')
    op.drop_table('userpopulation')
    ### end Alembic commands ###
