from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context as alembic_context
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.models import Base
from app.core.config import settings

config = alembic_context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
target_metadata = Base.metadata

DATABASE_URL = settings.DATABASE_URL
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables.")

config.set_main_option('sqlalchemy.url', DATABASE_URL)

def run_migrations_offline():
    alembic_context.configure(url=DATABASE_URL, target_metadata=target_metadata, literal_binds=True)
    with alembic_context.begin_transaction():
        alembic_context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section) or {},
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
        future=True,
    )
    with connectable.connect() as connection:
        alembic_context.configure(connection=connection, target_metadata=target_metadata)
        with alembic_context.begin_transaction():
            alembic_context.run_migrations()

if alembic_context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online() 