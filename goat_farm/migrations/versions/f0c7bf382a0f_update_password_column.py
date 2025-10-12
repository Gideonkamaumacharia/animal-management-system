"""Update password column

Revision ID: f0c7bf382a0f
Revises: c87787199a2a
Create Date: 2025-10-12 08:46:44.139488

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f0c7bf382a0f'
down_revision = 'c87787199a2a'
branch_labels = None
depends_on = None


def upgrade():
    # ### CORRECTED COMMANDS ###
    # Use alter_column to safely rename the existing column while keeping the data.
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('password_hash', new_column_name='password')
    # ### END CORRECTED COMMANDS ###


def downgrade():
    # ### CORRECTED COMMANDS ###
    # The reverse operation for downgrading the database.
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('password', new_column_name='password_hash')
    # ### END CORRECTED COMMANDS ###