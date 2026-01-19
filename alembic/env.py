from __future__ import with_statement

import logging
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

from mcp_lab.logger_cfg import logg
from src.mcp_lab.db.migration.db_files import DatabaseFiles
from src.mcp_lab.db.migration.models import Base

# config Alembica
config = context.config
fileConfig(config.config_file_name)

# set db file path
config.set_main_option("sqlalchemy.url", DatabaseFiles.get_db_path_sqlite())

# models
target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        echo=False
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            echo=False
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()



