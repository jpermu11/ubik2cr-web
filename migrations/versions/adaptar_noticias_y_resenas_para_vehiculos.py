"""adaptar noticias y resenas para vehiculos

Revision ID: adaptar_noticias_resenas
Revises: add_vehiculos_agencias
Create Date: 2026-01-12 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'adaptar_noticias_resenas'
down_revision = 'add_vehiculos_agencias'
branch_labels = None
depends_on = None


def upgrade():
    # Adaptar tabla noticias para agencias
    # Agregar columna agencia_id
    op.add_column('noticias', sa.Column('agencia_id', sa.Integer(), nullable=True))
    op.create_index('ix_noticias_agencia_id', 'noticias', ['agencia_id'], unique=False)
    op.create_foreign_key('fk_noticias_agencia_id', 'noticias', 'agencias', ['agencia_id'], ['id'])
    
    # Hacer fecha_caducidad obligatoria (NOT NULL)
    # Primero, establecer un valor por defecto para registros existentes
    op.execute("UPDATE noticias SET fecha_caducidad = fecha + INTERVAL '30 days' WHERE fecha_caducidad IS NULL")
    op.alter_column('noticias', 'fecha_caducidad', nullable=False)
    
    # Adaptar tabla resenas para vendedores/agencias
    # Agregar columnas vendedor_id y agencia_id
    op.add_column('resenas', sa.Column('vendedor_id', sa.Integer(), nullable=True))
    op.add_column('resenas', sa.Column('agencia_id', sa.Integer(), nullable=True))
    op.create_index('ix_resenas_vendedor_id', 'resenas', ['vendedor_id'], unique=False)
    op.create_index('ix_resenas_agencia_id', 'resenas', ['agencia_id'], unique=False)
    op.create_foreign_key('fk_resenas_vendedor_id', 'resenas', 'usuarios', ['vendedor_id'], ['id'])
    op.create_foreign_key('fk_resenas_agencia_id', 'resenas', 'agencias', ['agencia_id'], ['id'])
    
    # Actualizar rol por defecto de usuarios a VENDEDOR
    op.execute("UPDATE usuarios SET rol = 'VENDEDOR' WHERE rol = 'OWNER' OR rol IS NULL")


def downgrade():
    # Revertir cambios en resenas
    op.drop_constraint('fk_resenas_agencia_id', 'resenas', type_='foreignkey')
    op.drop_constraint('fk_resenas_vendedor_id', 'resenas', type_='foreignkey')
    op.drop_index('ix_resenas_agencia_id', table_name='resenas')
    op.drop_index('ix_resenas_vendedor_id', table_name='resenas')
    op.drop_column('resenas', 'agencia_id')
    op.drop_column('resenas', 'vendedor_id')
    
    # Revertir cambios en noticias
    op.alter_column('noticias', 'fecha_caducidad', nullable=True)
    op.drop_constraint('fk_noticias_agencia_id', 'noticias', type_='foreignkey')
    op.drop_index('ix_noticias_agencia_id', table_name='noticias')
    op.drop_column('noticias', 'agencia_id')
    
    # Revertir rol de usuarios
    op.execute("UPDATE usuarios SET rol = 'OWNER' WHERE rol = 'VENDEDOR'")
