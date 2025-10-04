import importlib
from logging.config import fileConfig
import os
import alembic_postgresql_enum # noqa: F401
from sqlalchemy import create_engine
from sqlalchemy import pool
from sqlmodel import SQLModel
from alembic import context

from config.config import get_learnhouse_config

lh_config = get_learnhouse_config()

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

base_dir = 'src/db'
base_module_path = 'src.db'

for root, dirs, files in os.walk(base_dir):
    module_files = [f for f in files if f.endswith('.py') and f != '__init__.py']
    path_diff = os.path.relpath(root, base_dir)
    if path_diff == '.':
        current_module_base = base_module_path
    else:
        current_module_base = f"{base_module_path}.{path_diff.replace(os.sep, '.')}"
    
    for file_name in module_files:
        module_name = file_name[:-3]
        full_module_path = f"{current_module_base}.{module_name}"
        importlib.import_module(full_module_path)

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = lh_config.database_config.sql_connection_string
    if url is None:
        raise ValueError("Database URL not configured in environment variables")
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    database_url = lh_config.database_config.sql_connection_string
    if database_url is None:
        raise ValueError("Database URL not configured in environment variables")
    
    connectable = create_engine(database_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
