"""add rating columns to video

Revision ID: c49a9b09c9f2
Revises: c4b130a0a513
Create Date: 2024-11-15 08:58:16.036264

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c49a9b09c9f2'
down_revision: Union[str, None] = 'c4b130a0a513'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('question')
    op.drop_table('answer')
    op.drop_index('ix_users_id', table_name='users')
    op.add_column('video', sa.Column('rating_sum', sa.Float(), nullable=True))
    op.add_column('video', sa.Column('rating_count', sa.Integer(), nullable=True))
    op.add_column('video', sa.Column('rating_average', sa.Float(), nullable=True))
    op.add_column('video', sa.Column('view_count', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('video', 'view_count')
    op.drop_column('video', 'rating_average')
    op.drop_column('video', 'rating_count')
    op.drop_column('video', 'rating_sum')
    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    op.create_table('answer',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('content', sa.TEXT(), nullable=False),
    sa.Column('create_date', sa.DATETIME(), nullable=False),
    sa.Column('question_id', sa.INTEGER(), nullable=True),
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.Column('modify_date', sa.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['question_id'], ['question.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('question',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('subject', sa.VARCHAR(), nullable=False),
    sa.Column('content', sa.TEXT(), nullable=False),
    sa.Column('create_date', sa.DATETIME(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.Column('modify_date', sa.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
