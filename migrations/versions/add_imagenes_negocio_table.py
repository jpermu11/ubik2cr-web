"""add imagenes_negocio table

Revision ID: add_imagenes_negocio
Revises: add_productos_tags_to_negocios
Create Date: 2026-01-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = 'add_imagenes_negocio'
down_revision = 'add_productos_tags_to_negocios'
branch_labels = None
depends_on = None


def upgrade():
    # Crear tabla imagenes_negocio
    op.create_table(
        'imagenes_negocio',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('negocio_id', sa.Integer(), nullable=False),
        sa.Column('imagen_url', sa.String(length=500), nullable=False),
        sa.Column('orden', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['negocio_id'], ['negocios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_imagenes_negocio_negocio_id', 'imagenes_negocio', ['negocio_id'], unique=False)
    op.create_index('ix_imagenes_negocio_orden', 'imagenes_negocio', ['orden'], unique=False)
    op.create_index('ix_imagenes_negocio_created_at', 'imagenes_negocio', ['created_at'], unique=False)


def downgrade():
    op.drop_index('ix_imagenes_negocio_created_at', table_name='imagenes_negocio')
    op.drop_index('ix_imagenes_negocio_orden', table_name='imagenes_negocio')
    op.drop_index('ix_imagenes_negocio_negocio_id', table_name='imagenes_negocio')
    op.drop_table('imagenes_negocio')
