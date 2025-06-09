import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool, engine_from_config
from sqlalchemy.engine import Connection

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.infrastructure.db.models import Base
from config.settings import get_db_settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

db_settings = get_db_settings()
section = config.get_section(config.config_ini_section)
section['sqlalchemy.url'] = db_settings.db_url_sync

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = section['sqlalchemy.url']
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        do_run_migrations(connection)
    connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
