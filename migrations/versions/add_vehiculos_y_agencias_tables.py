"""add vehiculos y agencias tables

Revision ID: add_vehiculos_agencias
Revises: add_provincia_canton_distrito
Create Date: 2026-01-12 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_vehiculos_agencias'
down_revision = 'add_provincia_canton_distrito'
branch_labels = None
depends_on = None


def upgrade():
    # Agregar campos a usuarios para sistema de vehículos
    op.add_column('usuarios', sa.Column('tipo_usuario', sa.String(length=20), nullable=True, server_default='individual'))
    op.add_column('usuarios', sa.Column('agencia_id', sa.Integer(), nullable=True))
    op.create_index('ix_usuarios_tipo_usuario', 'usuarios', ['tipo_usuario'], unique=False)
    op.create_index('ix_usuarios_agencia_id', 'usuarios', ['agencia_id'], unique=False)
    
    # Crear tabla agencias
    op.create_table('agencias',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('telefono', sa.String(length=20), nullable=True),
        sa.Column('whatsapp', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=180), nullable=True),
        sa.Column('ubicacion', sa.String(length=200), nullable=True),
        sa.Column('provincia', sa.String(length=50), nullable=True),
        sa.Column('canton', sa.String(length=100), nullable=True),
        sa.Column('distrito', sa.String(length=100), nullable=True),
        sa.Column('latitud', sa.Float(), nullable=True),
        sa.Column('longitud', sa.Float(), nullable=True),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('imagen_url', sa.String(length=500), nullable=True),
        sa.Column('estado', sa.String(length=20), nullable=True, server_default='pendiente'),
        sa.Column('es_vip', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_agencias_owner_id', 'agencias', ['owner_id'], unique=False)
    op.create_index('ix_agencias_nombre', 'agencias', ['nombre'], unique=False)
    op.create_index('ix_agencias_estado', 'agencias', ['estado'], unique=False)
    op.create_index('ix_agencias_provincia', 'agencias', ['provincia'], unique=False)
    
    # Crear tabla vehiculos
    op.create_table('vehiculos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('agencia_id', sa.Integer(), nullable=True),
        sa.Column('marca', sa.String(length=50), nullable=False),
        sa.Column('modelo', sa.String(length=100), nullable=False),
        sa.Column('año', sa.Integer(), nullable=False),
        sa.Column('precio', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('kilometraje', sa.Integer(), nullable=True),
        sa.Column('tipo_vehiculo', sa.String(length=50), nullable=False),
        sa.Column('transmision', sa.String(length=20), nullable=True),
        sa.Column('combustible', sa.String(length=30), nullable=True),
        sa.Column('color', sa.String(length=50), nullable=True),
        sa.Column('estado_vehiculo', sa.String(length=20), nullable=True, server_default='usado'),
        sa.Column('descripcion', sa.Text(), nullable=False),
        sa.Column('provincia', sa.String(length=50), nullable=True),
        sa.Column('canton', sa.String(length=100), nullable=True),
        sa.Column('distrito', sa.String(length=100), nullable=True),
        sa.Column('telefono', sa.String(length=20), nullable=True),
        sa.Column('whatsapp', sa.String(length=20), nullable=True),
        sa.Column('imagen_url', sa.String(length=500), nullable=True),
        sa.Column('estado', sa.String(length=20), nullable=True, server_default='pendiente'),
        sa.Column('es_vip', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('destacado', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('fecha_venta', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['usuarios.id'], ),
        sa.ForeignKeyConstraint(['agencia_id'], ['agencias.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_vehiculos_owner_id', 'vehiculos', ['owner_id'], unique=False)
    op.create_index('ix_vehiculos_agencia_id', 'vehiculos', ['agencia_id'], unique=False)
    op.create_index('ix_vehiculos_marca', 'vehiculos', ['marca'], unique=False)
    op.create_index('ix_vehiculos_modelo', 'vehiculos', ['modelo'], unique=False)
    op.create_index('ix_vehiculos_año', 'vehiculos', ['año'], unique=False)
    op.create_index('ix_vehiculos_precio', 'vehiculos', ['precio'], unique=False)
    op.create_index('ix_vehiculos_kilometraje', 'vehiculos', ['kilometraje'], unique=False)
    op.create_index('ix_vehiculos_tipo_vehiculo', 'vehiculos', ['tipo_vehiculo'], unique=False)
    op.create_index('ix_vehiculos_transmision', 'vehiculos', ['transmision'], unique=False)
    op.create_index('ix_vehiculos_combustible', 'vehiculos', ['combustible'], unique=False)
    op.create_index('ix_vehiculos_estado_vehiculo', 'vehiculos', ['estado_vehiculo'], unique=False)
    op.create_index('ix_vehiculos_estado', 'vehiculos', ['estado'], unique=False)
    op.create_index('ix_vehiculos_provincia', 'vehiculos', ['provincia'], unique=False)
    op.create_index('ix_vehiculos_marca_modelo', 'vehiculos', ['marca', 'modelo'], unique=False)
    op.create_index('ix_vehiculos_estado_precio', 'vehiculos', ['estado', 'precio'], unique=False)
    op.create_index('ix_vehiculos_año_precio', 'vehiculos', ['año', 'precio'], unique=False)
    op.create_index('ix_vehiculos_tipo_estado', 'vehiculos', ['tipo_vehiculo', 'estado'], unique=False)
    op.create_index('ix_vehiculos_provincia_estado', 'vehiculos', ['provincia', 'estado'], unique=False)
    
    # Crear tabla imagenes_vehiculo
    op.create_table('imagenes_vehiculo',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vehiculo_id', sa.Integer(), nullable=False),
        sa.Column('imagen_url', sa.String(length=500), nullable=False),
        sa.Column('orden', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['vehiculo_id'], ['vehiculos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_imagenes_vehiculo_vehiculo_id', 'imagenes_vehiculo', ['vehiculo_id'], unique=False)
    op.create_index('ix_imagenes_vehiculo_orden', 'imagenes_vehiculo', ['orden'], unique=False)
    
    # Crear tabla favoritos_vehiculos
    op.create_table('favoritos_vehiculos',
        sa.Column('usuario_id', sa.Integer(), nullable=False),
        sa.Column('vehiculo_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ),
        sa.ForeignKeyConstraint(['vehiculo_id'], ['vehiculos.id'], ),
        sa.PrimaryKeyConstraint('usuario_id', 'vehiculo_id')
    )
    
    # Agregar foreign key de usuarios a agencias
    op.create_foreign_key('fk_usuarios_agencia_id', 'usuarios', 'agencias', ['agencia_id'], ['id'])


def downgrade():
    # Eliminar foreign key
    op.drop_constraint('fk_usuarios_agencia_id', 'usuarios', type_='foreignkey')
    
    # Eliminar tablas
    op.drop_table('favoritos_vehiculos')
    op.drop_table('imagenes_vehiculo')
    op.drop_table('vehiculos')
    op.drop_table('agencias')
    
    # Eliminar columnas de usuarios
    op.drop_index('ix_usuarios_agencia_id', table_name='usuarios')
    op.drop_index('ix_usuarios_tipo_usuario', table_name='usuarios')
    op.drop_column('usuarios', 'agencia_id')
    op.drop_column('usuarios', 'tipo_usuario')
