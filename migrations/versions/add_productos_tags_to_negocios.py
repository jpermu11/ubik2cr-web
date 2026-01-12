"""add productos_tags to negocios

Revision ID: add_productos_tags_to_negocios
Revises: add_mensajes
Create Date: 2025-01-30 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_productos_tags_to_negocios'
down_revision = 'add_mensajes'  # Fixed: changed from 'add_mensajes_table' to 'add_mensajes'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('negocios', schema=None) as batch_op:
        batch_op.add_column(sa.Column('productos_tags', sa.Text(), nullable=True))


def downgrade():
    with op.batch_alter_table('negocios', schema=None) as batch_op:
        batch_op.drop_column('productos_tags')

