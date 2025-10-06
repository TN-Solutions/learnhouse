"""add_media_file_table

Revision ID: ed11bbbb6077
Revises: 63ecb81aa026
Create Date: 2025-10-04 16:24:21.604463

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa # noqa: F401
import sqlmodel # noqa: F401


# revision identifiers, used by Alembic.
revision: str = 'ed11bbbb6077'
down_revision: Union[str, None] = '63ecb81aa026'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('mediafile',
    sa.Column('file_uuid', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('storage_backend', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('file_path', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('file_url', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('content_type', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('file_size', sa.Integer(), nullable=False),
    sa.Column('resource_type', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('resource_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uploaded_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_media_files_resource', 'mediafile', ['resource_type', 'resource_id'], unique=False)
    op.create_index(op.f('ix_mediafile_file_uuid'), 'mediafile', ['file_uuid'], unique=True)
    op.create_index(op.f('ix_mediafile_resource_id'), 'mediafile', ['resource_id'], unique=False)
    op.create_index(op.f('ix_mediafile_resource_type'), 'mediafile', ['resource_type'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_mediafile_resource_type'), table_name='mediafile')
    op.drop_index(op.f('ix_mediafile_resource_id'), table_name='mediafile')
    op.drop_index(op.f('ix_mediafile_file_uuid'), table_name='mediafile')
    op.drop_index('ix_media_files_resource', table_name='mediafile')
    op.drop_table('mediafile')
