"""Alembic environment: runs revisions against the configured PostgreSQL database.

The URL comes from the `JSF_DATABASE_*` settings. A caller that already holds a
connection, such as a test, passes it as `config.attributes["connection"]`.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import Connection, create_engine
from sqlalchemy.pool import NullPool

from job_status_found.app.alembic_metadata import metadata
from job_status_found.features.core import get_settings

_SET_LOCK_TIMEOUT = "SET LOCAL lock_timeout = '5s'"
"""SQL that makes a revision fail after waiting 5 s for a table lock.

Without it, a revision that alters a live table would queue every request
behind its lock.
"""

config = context.config

# The command line gets Alembic's logging; a caller that passes its own
# connection keeps the logging it already configured.
if config.config_file_name is not None and "connection" not in config.attributes:
    fileConfig(config.config_file_name)


def run_migrations_offline() -> None:
    """Write the migration SQL to standard output without connecting."""
    context.configure(
        url=get_settings().database_url,
        target_metadata=metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.execute(_SET_LOCK_TIMEOUT)
        context.run_migrations()


def run_migrations_on(connection: Connection) -> None:
    """Run the pending revisions over an open connection.

    `alembic check` and autogenerate also compare server defaults and, by name,
    `CHECK` constraints. They never compare a `CHECK` constraint's text, a
    primary key, or a partial index's condition.

    Args:
        connection: The connection to the database being migrated.
    """
    context.configure(
        connection=connection,
        target_metadata=metadata,
        compare_server_default=True,
        autogenerate_plugins=["alembic.autogenerate.*", "alembic.ext.checkconstraint_byname"],
    )
    with context.begin_transaction():
        context.execute(_SET_LOCK_TIMEOUT)
        context.run_migrations()


def run_migrations_online() -> None:
    """Run the pending revisions against the database, connecting if needed.

    Raises:
        TypeError: The caller passed something other than a SQLAlchemy
            `Connection` as `config.attributes["connection"]`.
    """
    connection = config.attributes.get("connection")
    if isinstance(connection, Connection):
        run_migrations_on(connection)
        return
    if connection is not None:
        msg = f'config.attributes["connection"] must be a Connection, not {type(connection)}.'
        raise TypeError(msg)
    engine = create_engine(get_settings().database_url, poolclass=NullPool)
    try:
        with engine.connect() as new_connection:
            run_migrations_on(new_connection)
    finally:
        engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
