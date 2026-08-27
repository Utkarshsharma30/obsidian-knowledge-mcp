from pathlib import Path

from database.connection import connect


def main() -> None:
    schema_path = Path(__file__).with_name("schema.sql")
    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(schema_path.read_text(encoding="utf-8"))
        connection.commit()


if __name__ == "__main__":
    main()