"""add resenas table

Revision ID: add_resenas
Revises: add_favoritos
Create Date: 2026-01-05 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'add_resenas'
down_revision = 'add_favoritos'
branch_labels = None
depends_on = None


def upgrade():
    # Crear tabla resenas
    op.create_table(
        'resenas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('negocio_id', sa.Integer(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=True),
        sa.Column('nombre_usuario', sa.String(length=100), nullable=True),
        sa.Column('email_usuario', sa.String(length=180), nullable=True),
        sa.Column('calificacion', sa.Integer(), nullable=False),
        sa.Column('comentario', sa.Text(), nullable=True),
        sa.Column('estado', sa.String(length=20), nullable=True, server_default='aprobado'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['negocio_id'], ['negocios.id'], ),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_resenas_negocio_estado', 'resenas', ['negocio_id', 'estado'])
    op.create_index(op.f('ix_resenas_negocio_id'), 'resenas', ['negocio_id'], unique=False)
    op.create_index(op.f('ix_resenas_usuario_id'), 'resenas', ['usuario_id'], unique=False)
    op.create_index(op.f('ix_resenas_estado'), 'resenas', ['estado'], unique=False)
    op.create_index(op.f('ix_resenas_created_at'), 'resenas', ['created_at'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_resenas_created_at'), table_name='resenas')
    op.drop_index(op.f('ix_resenas_estado'), table_name='resenas')
    op.drop_index(op.f('ix_resenas_usuario_id'), table_name='resenas')
    op.drop_index(op.f('ix_resenas_negocio_id'), table_name='resenas')
    op.drop_index('ix_resenas_negocio_estado', table_name='resenas')
    op.drop_table('resenas')

