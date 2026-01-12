"""add fecha_caducidad a noticias

Revision ID: add_fecha_caducidad
Revises: add_horario
Create Date: 2026-01-08 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "add_fecha_caducidad"
down_revision = "add_horario"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("noticias", sa.Column("fecha_caducidad", sa.DateTime(), nullable=True))
    op.create_index("ix_noticias_fecha_caducidad", "noticias", ["fecha_caducidad"])


def downgrade():
    op.drop_index("ix_noticias_fecha_caducidad", table_name="noticias")
    op.drop_column("noticias", "fecha_caducidad")


