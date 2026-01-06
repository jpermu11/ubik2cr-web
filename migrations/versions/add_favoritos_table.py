"""add favoritos table

Revision ID: add_favoritos
Revises: ea1ade19e2c0
Create Date: 2026-01-05 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'add_favoritos'
down_revision = 'ea1ade19e2c0'
branch_labels = None
depends_on = None


def upgrade():
    # Crear tabla favoritos
    op.create_table(
        'favoritos',
        sa.Column('usuario_id', sa.Integer(), nullable=False),
        sa.Column('negocio_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ),
        sa.ForeignKeyConstraint(['negocio_id'], ['negocios.id'], ),
        sa.PrimaryKeyConstraint('usuario_id', 'negocio_id')
    )
    op.create_index('ix_favoritos_usuario', 'favoritos', ['usuario_id'])
    op.create_index('ix_favoritos_negocio', 'favoritos', ['negocio_id'])


def downgrade():
    op.drop_index('ix_favoritos_negocio', table_name='favoritos')
    op.drop_index('ix_favoritos_usuario', table_name='favoritos')
    op.drop_table('favoritos')

