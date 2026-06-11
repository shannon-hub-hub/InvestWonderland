"""Apply PostgreSQL schema and create ORM tables."""

from pathlib import Path

from sqlalchemy import text

from app.db.models import Base
from app.db.session import engine

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "db" / "schema.sql"
MIGRATIONS_DIR = Path(__file__).resolve().parents[1] / "db" / "migrations"


def _run_sql_file(conn, path: Path) -> None:
    sql = path.read_text()
    for statement in sql.split(";"):
        stmt = statement.strip()
        if stmt:
            conn.execute(text(stmt))


def main():
    with engine.begin() as conn:
        for migration in sorted(MIGRATIONS_DIR.glob("*.sql")):
            _run_sql_file(conn, migration)
            print(f"Applied migration {migration.name}")
        _run_sql_file(conn, SCHEMA_PATH)
    Base.metadata.create_all(bind=engine)
    print(f"Database initialized from {SCHEMA_PATH}")


if __name__ == "__main__":
    main()
