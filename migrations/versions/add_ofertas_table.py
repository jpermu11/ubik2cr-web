"""add ofertas table

Revision ID: add_ofertas
Revises: add_resenas
Create Date: 2026-01-05 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'add_ofertas'
down_revision = 'add_resenas'
branch_labels = None
depends_on = None


def upgrade():
    # Crear tabla ofertas
    op.create_table(
        'ofertas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('negocio_id', sa.Integer(), nullable=False),
        sa.Column('titulo', sa.String(length=200), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('imagen_url', sa.String(length=500), nullable=False),
        sa.Column('fecha_inicio', sa.DateTime(), nullable=True),
        sa.Column('fecha_caducidad', sa.DateTime(), nullable=False),
        sa.Column('estado', sa.String(length=20), nullable=True, server_default='activa'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['negocio_id'], ['negocios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ofertas_negocio_fecha', 'ofertas', ['negocio_id', 'fecha_caducidad'])
    op.create_index('ix_ofertas_estado_fecha', 'ofertas', ['estado', 'fecha_caducidad'])
    op.create_index(op.f('ix_ofertas_negocio_id'), 'ofertas', ['negocio_id'], unique=False)
    op.create_index(op.f('ix_ofertas_fecha_inicio'), 'ofertas', ['fecha_inicio'], unique=False)
    op.create_index(op.f('ix_ofertas_fecha_caducidad'), 'ofertas', ['fecha_caducidad'], unique=False)
    op.create_index(op.f('ix_ofertas_estado'), 'ofertas', ['estado'], unique=False)
    op.create_index(op.f('ix_ofertas_created_at'), 'ofertas', ['created_at'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_ofertas_created_at'), table_name='ofertas')
    op.drop_index(op.f('ix_ofertas_estado'), table_name='ofertas')
    op.drop_index(op.f('ix_ofertas_fecha_caducidad'), table_name='ofertas')
    op.drop_index(op.f('ix_ofertas_fecha_inicio'), table_name='ofertas')
    op.drop_index(op.f('ix_ofertas_negocio_id'), table_name='ofertas')
    op.drop_index('ix_ofertas_estado_fecha', table_name='ofertas')
    op.drop_index('ix_ofertas_negocio_fecha', table_name='ofertas')
    op.drop_table('ofertas')

