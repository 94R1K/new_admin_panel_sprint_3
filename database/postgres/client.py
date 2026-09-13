import contextlib
from dataclasses import dataclass

import psycopg
from psycopg.rows import dict_row

from config.settings import settings


@dataclass
class PostgresClient:
    connection: psycopg.Connection
    cursor: psycopg.ClientCursor

    @classmethod
    def create(cls) -> "PostgresClient":
        connection = psycopg.connect(
            dbname=settings.postgres_db,
            user=settings.postgres_user,
            password=settings.postgres_password,
            host=settings.postgres_host,
            port=settings.postgres_port,
            row_factory=dict_row,
            cursor_factory=psycopg.ClientCursor,
        )

        return cls(
            connection=connection,
            cursor=connection.cursor(),
        )

    def reconnect(self) -> None:
        with contextlib.suppress(psycopg.Error):
            self.connection.close()

        self.connection = psycopg.connect(
            dbname=settings.postgres_db,
            user=settings.postgres_user,
            password=settings.postgres_password,
            host=settings.postgres_host,
            port=settings.postgres_port,
            row_factory=dict_row,
            cursor_factory=psycopg.ClientCursor,
        )
        self.cursor = self.connection.cursor()

    def close(self) -> None:
        self.connection.close()
