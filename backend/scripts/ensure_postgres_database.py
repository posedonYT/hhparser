"""До миграций: ждёт PostgreSQL и создаёт БД из DATABASE_URL, если её ещё нет."""

from __future__ import annotations

import os
import re
import sys
import time

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import OperationalError

# Только безопасные идентификаторы без кавычек в CREATE DATABASE
_SAFE_DB_NAME = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def main() -> None:
    raw = os.environ.get("DATABASE_URL", "")
    if not raw.startswith("postgresql"):
        return

    url = make_url(raw)
    dbname = url.database
    if not dbname or not _SAFE_DB_NAME.match(dbname):
        print("ensure_postgres_database: пропуск — не PostgreSQL или некорректное имя БД", file=sys.stderr)
        return

    admin_url = url.set(database="postgres")

    last_error: Exception | None = None
    for attempt in range(60):
        try:
            engine = create_engine(
                admin_url,
                isolation_level="AUTOCOMMIT",
                pool_pre_ping=True,
                connect_args={"connect_timeout": 5},
            )
            with engine.connect() as conn:
                exists = conn.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :n"),
                    {"n": dbname},
                ).scalar()
                if exists != 1:
                    conn.execute(text(f"CREATE DATABASE {dbname}"))
            engine.dispose()
            return
        except OperationalError as e:
            last_error = e
            time.sleep(1)

    print(f"ensure_postgres_database: не удалось подключиться к PostgreSQL: {last_error}", file=sys.stderr)
    raise SystemExit(1) from last_error


if __name__ == "__main__":
    main()
