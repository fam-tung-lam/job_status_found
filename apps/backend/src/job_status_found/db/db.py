"""PostgreSQL access shared by every feature: declarative base, engine, and sessions."""

from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager
from datetime import datetime
from ipaddress import IPv4Address, IPv6Address
from typing import Annotated, Any, ClassVar
from uuid import UUID

from fastapi import FastAPI, Request
from sqlalchemy import URL, DateTime, LargeBinary, MetaData, Text, Uuid, text
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy.types import TypeEngine

type IpAddress = IPv4Address | IPv6Address
"""A client IP address, stored as PostgreSQL `inet` and read back as an `ipaddress` value."""

type JsonValue = str | int | float | bool | list[JsonValue] | dict[str, JsonValue] | None
"""A value JSON can represent."""

type JsonObject = dict[str, JsonValue]
"""A JSON object, stored as PostgreSQL `jsonb`."""

type SurrogateKey = Annotated[
    UUID, mapped_column(primary_key=True, server_default=text("uuidv7()"))
]
"""A `uuid` primary key the database generates with `uuidv7()`, so keys sort by creation time.

Annotate a column as `Mapped[SurrogateKey]`.
"""


class Base(DeclarativeBase):
    """Declarative base for every feature's mapped tables.

    Declare a column with its annotation alone, such as `email: Mapped[str]`, and
    its constraints and indexes in `__table_args__`. The annotation picks the
    column type the schema conventions require: `str` is `text`, `datetime` is
    `timestamptz`, `bytes` is `bytea`, `UUID` is `uuid`, `IpAddress` is `inet`,
    and `JsonObject` is `jsonb`; `| None` makes the column nullable.
    """

    metadata = MetaData(
        naming_convention={
            "pk": "pk_%(table_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "uq": "uq_%(table_name)s_%(column_0_N_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "ix": "ix_%(table_name)s_%(column_0_N_name)s",
        },
    )
    """Every mapped table, with deterministic constraint and index names.

    A later revision can alter or drop a constraint or index by its name.
    """

    type_annotation_map: ClassVar[Mapping[object, TypeEngine[Any]]] = {
        str: Text(),
        datetime: DateTime(timezone=True),
        bytes: LargeBinary(),
        UUID: Uuid(),
        IpAddress: INET(),
        # A Python `None` becomes SQL `NULL`, never the JSON value `null`.
        JsonObject: JSONB(none_as_null=True),
    }
    """The column type each annotated Python type maps to."""


class DatabaseSessionFactory(async_sessionmaker[AsyncSession]):
    """Creates the sessions of the engine the application's lifespan opened.

    It exists as its own class so that an `isinstance` check on the untyped
    application state narrows to a factory of `AsyncSession`, which keeps the
    request session's type sound.
    """


@asynccontextmanager
async def open_database(app: FastAPI, database_url: URL) -> AsyncIterator[None]:
    """Own the application's database engine for the life of the process.

    The engine opens no connection until the first request uses a session, so
    starting the application does not require a reachable database. Pooled
    connections are checked before use, so a database restart costs no failed
    request, and error messages never include SQL parameters, which can hold
    secrets or personal data.

    Args:
        app: The application whose requests receive sessions from this engine.
        database_url: The URL of the database to open.

    Yields:
        Control while the application serves requests; the engine's
        connections close when the block exits.
    """
    engine = create_async_engine(database_url, pool_pre_ping=True, hide_parameters=True)
    app.state.database_session_factory = DatabaseSessionFactory(engine, expire_on_commit=False)
    try:
        yield
    finally:
        del app.state.database_session_factory
        await engine.dispose()


async def get_database_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Provide one database session for the current request.

    The session closes when the request ends and rolls back any transaction the
    use case left uncommitted. Committing stays the use case's decision.

    Args:
        request: The current request, whose application opened the database.

    Yields:
        A session bound to the configured database.

    Raises:
        RuntimeError: The application serves requests outside its lifespan, so
            no database is open.
    """
    session_factory = getattr(request.app.state, "database_session_factory", None)
    if not isinstance(session_factory, DatabaseSessionFactory):
        msg = "No database is open; the application's lifespan opens it before requests."
        raise RuntimeError(msg)
    async with session_factory() as session:
        yield session
