"""Added foreign key field to influencer

Revision ID: c693e4c8b60b
Revises: f33eeb51c667
Create Date: 2022-12-26 20:29:55.424285

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c693e4c8b60b'
down_revision = 'f33eeb51c667'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('influencers', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'influencers', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'influencers', type_='foreignkey')
    op.drop_column('influencers', 'user_id')
    # ### end Alembic commands ###
