"""add negocio_id to noticias

Revision ID: add_negocio_id_to_noticias
Revises: add_imagenes_negocio
Create Date: 2026-01-12 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_negocio_id_to_noticias'
down_revision = 'add_imagenes_negocio'
branch_labels = None
depends_on = None


def upgrade():
    # Agregar columna negocio_id a noticias
    op.add_column('noticias', sa.Column('negocio_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_noticias_negocio_id', 'noticias', 'negocios', ['negocio_id'], ['id'])
    op.create_index('ix_noticias_negocio_id', 'noticias', ['negocio_id'], unique=False)


def downgrade():
    op.drop_index('ix_noticias_negocio_id', table_name='noticias')
    op.drop_constraint('fk_noticias_negocio_id', 'noticias', type_='foreignkey')
    op.drop_column('noticias', 'negocio_id')
