"""add mensajes table

Revision ID: add_mensajes
Revises: add_fecha_caducidad
Create Date: 2026-01-08 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "add_mensajes"
down_revision = "add_fecha_caducidad"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "mensajes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("negocio_id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=True),
        sa.Column("nombre_remitente", sa.String(length=100), nullable=False),
        sa.Column("email_remitente", sa.String(length=180), nullable=False),
        sa.Column("asunto", sa.String(length=200), nullable=False),
        sa.Column("mensaje", sa.Text(), nullable=False),
        sa.Column("leido", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("respondido", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["negocio_id"], ["negocios.id"], ),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_mensajes_negocio_leido", "mensajes", ["negocio_id", "leido"])
    op.create_index("ix_mensajes_negocio_fecha", "mensajes", ["negocio_id", "created_at"])
    op.create_index("ix_mensajes_email_remitente", "mensajes", ["email_remitente"])
    op.create_index("ix_mensajes_leido", "mensajes", ["leido"])
    op.create_index("ix_mensajes_respondido", "mensajes", ["respondido"])
    op.create_index("ix_mensajes_negocio_id", "mensajes", ["negocio_id"])
    op.create_index("ix_mensajes_usuario_id", "mensajes", ["usuario_id"])


def downgrade():
    op.drop_index("ix_mensajes_usuario_id", table_name="mensajes")
    op.drop_index("ix_mensajes_negocio_id", table_name="mensajes")
    op.drop_index("ix_mensajes_respondido", table_name="mensajes")
    op.drop_index("ix_mensajes_leido", table_name="mensajes")
    op.drop_index("ix_mensajes_email_remitente", table_name="mensajes")
    op.drop_index("ix_mensajes_negocio_fecha", table_name="mensajes")
    op.drop_index("ix_mensajes_negocio_leido", table_name="mensajes")
    op.drop_table("mensajes")


