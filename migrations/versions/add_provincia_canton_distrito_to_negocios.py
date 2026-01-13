"""add provincia canton distrito to negocios

Revision ID: add_provincia_canton_distrito
Revises: add_visitas_table
Create Date: 2026-01-12 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_provincia_canton_distrito'
down_revision = 'add_visitas_table'
branch_labels = None
depends_on = None


def upgrade():
    # Agregar columnas de ubicación geográfica
    op.add_column('negocios', sa.Column('provincia', sa.String(length=50), nullable=True))
    op.add_column('negocios', sa.Column('canton', sa.String(length=100), nullable=True))
    op.add_column('negocios', sa.Column('distrito', sa.String(length=100), nullable=True))
    
    # Crear índices para búsquedas eficientes
    op.create_index('ix_negocios_provincia', 'negocios', ['provincia'], unique=False)
    op.create_index('ix_negocios_canton', 'negocios', ['canton'], unique=False)
    op.create_index('ix_negocios_distrito', 'negocios', ['distrito'], unique=False)
    op.create_index('ix_negocios_provincia_canton', 'negocios', ['provincia', 'canton'], unique=False)
    op.create_index('ix_negocios_provincia_canton_distrito', 'negocios', ['provincia', 'canton', 'distrito'], unique=False)


def downgrade():
    op.drop_index('ix_negocios_provincia_canton_distrito', table_name='negocios')
    op.drop_index('ix_negocios_provincia_canton', table_name='negocios')
    op.drop_index('ix_negocios_distrito', table_name='negocios')
    op.drop_index('ix_negocios_canton', table_name='negocios')
    op.drop_index('ix_negocios_provincia', table_name='negocios')
    op.drop_column('negocios', 'distrito')
    op.drop_column('negocios', 'canton')
    op.drop_column('negocios', 'provincia')
