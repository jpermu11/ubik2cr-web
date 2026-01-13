"""add visitas table

Revision ID: add_visitas_table
Revises: add_negocio_id_to_noticias
Create Date: 2026-01-12 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_visitas_table'
down_revision = 'add_negocio_id_to_noticias'
branch_labels = None
depends_on = None


def upgrade():
    # Crear tabla visitas para analytics
    op.create_table('visitas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ip_hash', sa.String(length=64), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('user_agent', sa.String(length=200), nullable=True),
        sa.Column('referrer', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_visitas_created_at', 'visitas', ['created_at'], unique=False)
    op.create_index('ix_visitas_ip_hash', 'visitas', ['ip_hash'], unique=False)
    op.create_index('ix_visitas_url', 'visitas', ['url'], unique=False)
    op.create_index('ix_visitas_url_created_at', 'visitas', ['url', 'created_at'], unique=False)


def downgrade():
    op.drop_index('ix_visitas_url_created_at', table_name='visitas')
    op.drop_index('ix_visitas_url', table_name='visitas')
    op.drop_index('ix_visitas_ip_hash', table_name='visitas')
    op.drop_index('ix_visitas_created_at', table_name='visitas')
    op.drop_table('visitas')
