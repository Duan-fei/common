"""20180124

Revision ID: 2b160cb9ffda
Revises: 769eb63ce8c3
Create Date: 2018-01-21 22:18:34.114946

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b160cb9ffda'
down_revision = '769eb63ce8c3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('company_name', table_name='cre_user_profile')
    op.drop_index('email', table_name='cre_user_profile')
    op.drop_index('username', table_name='cre_user_profile')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('username', 'cre_user_profile', ['username'], unique=True)
    op.create_index('email', 'cre_user_profile', ['email'], unique=True)
    op.create_index('company_name', 'cre_user_profile', ['company_name'], unique=True)
    # ### end Alembic commands ###
