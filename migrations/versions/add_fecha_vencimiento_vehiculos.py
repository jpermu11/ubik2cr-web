"""add fecha vencimiento vehiculos

Revision ID: add_fecha_vencimiento_vehiculos
Revises: add_vehiculos_agencias
Create Date: 2026-01-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_fecha_vencimiento_vehiculos'
down_revision = 'adaptar_noticias_resenas'
branch_labels = None
depends_on = None


def upgrade():
    # Agregar fecha de vencimiento y bandera de notificación
    op.add_column('vehiculos', sa.Column('fecha_vencimiento', sa.DateTime(), nullable=True))
    op.add_column('vehiculos', sa.Column('notificacion_vencimiento_enviada', sa.Boolean(), nullable=True, server_default=sa.text('false')))

    # Índices para consultas por vencimiento/notificación
    op.create_index('ix_vehiculos_fecha_vencimiento', 'vehiculos', ['fecha_vencimiento'], unique=False)
    op.create_index('ix_vehiculos_notificacion_vencimiento_enviada', 'vehiculos', ['notificacion_vencimiento_enviada'], unique=False)


def downgrade():
    op.drop_index('ix_vehiculos_notificacion_vencimiento_enviada', table_name='vehiculos')
    op.drop_index('ix_vehiculos_fecha_vencimiento', table_name='vehiculos')
    op.drop_column('vehiculos', 'notificacion_vencimiento_enviada')
    op.drop_column('vehiculos', 'fecha_vencimiento')
