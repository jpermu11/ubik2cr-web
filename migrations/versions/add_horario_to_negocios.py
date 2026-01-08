"""add horario y abierto_24h a negocios

Revision ID: add_horario
Revises: add_ofertas
Create Date: 2026-01-08 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "add_horario"
down_revision = "add_ofertas"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("negocios", sa.Column("horario", sa.String(length=300), nullable=True))
    op.add_column(
        "negocios",
        sa.Column("abierto_24h", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.create_index("ix_negocios_abierto_24h", "negocios", ["abierto_24h"])


def downgrade():
    op.drop_index("ix_negocios_abierto_24h", table_name="negocios")
    op.drop_column("negocios", "abierto_24h")
    op.drop_column("negocios", "horario")


