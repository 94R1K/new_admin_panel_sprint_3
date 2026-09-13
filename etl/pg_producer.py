from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

import psycopg
from psycopg.sql import SQL, Literal

from backoff.decorator import backoff
from config.settings import settings
from database.postgres.client import PostgresClient
from state.state import Checkpoint


@dataclass
class ChangedFilmWorks:
    film_work_ids: set[UUID]
    film_work_checkpoint: Checkpoint | None
    person_checkpoint: Checkpoint | None
    genre_checkpoint: Checkpoint | None


@dataclass
class PostgresProducer:
    postgres: PostgresClient

    @backoff(
        start_sleep_time=settings.backoff_seconds,
        exceptions=(psycopg.OperationalError,),
        reconnect=lambda producer: producer.postgres.reconnect(),
    )
    def extract(
        self,
        film_work_checkpoint: Checkpoint | None,
        person_checkpoint: Checkpoint | None,
        genre_checkpoint: Checkpoint | None,
    ) -> ChangedFilmWorks:

        film_work_ids, new_film_work_checkpoint = self._get_changed_film_works(
            film_work_checkpoint,
        )

        person_ids, new_person_checkpoint = self._get_changed_persons(
            person_checkpoint,
        )

        genre_ids, new_genre_checkpoint = self._get_changed_genres(
            genre_checkpoint,
        )

        changed_film_work_ids = set(film_work_ids)

        changed_film_work_ids.update(self._get_film_works_by_persons(person_ids))

        changed_film_work_ids.update(self._get_film_works_by_genres(genre_ids))

        return ChangedFilmWorks(
            film_work_ids=changed_film_work_ids,
            film_work_checkpoint=new_film_work_checkpoint,
            person_checkpoint=new_person_checkpoint,
            genre_checkpoint=new_genre_checkpoint,
        )

    def _get_changed_film_works(
        self,
        checkpoint: Checkpoint | None,
    ) -> tuple[list[UUID], Checkpoint | None]:

        if checkpoint is None:
            modified = datetime.min.replace(tzinfo=UTC)
            last_id = None
        else:
            modified = checkpoint.modified
            last_id = checkpoint.id

        if last_id is None:
            query = SQL("""
                SELECT id, modified
                FROM content.film_work
                WHERE modified > {modified}
                ORDER BY modified, id
                LIMIT {batch_size};
            """).format(
                modified=Literal(modified),
                batch_size=Literal(settings.batch_size),
            )
        else:
            query = SQL("""
                SELECT id, modified
                FROM content.film_work
                WHERE (modified, id) > (
                    {modified},
                    {last_id}
                )
                ORDER BY modified, id
                LIMIT {batch_size};
            """).format(
                modified=Literal(modified),
                last_id=Literal(last_id),
                batch_size=Literal(settings.batch_size),
            )

        rows = self.postgres.cursor.execute(query).fetchall()

        if not rows:
            return [], checkpoint

        last_row = rows[-1]

        return (
            [row["id"] for row in rows],
            Checkpoint(
                modified=last_row["modified"],
                id=last_row["id"],
            ),
        )

    def _get_changed_persons(
        self,
        checkpoint: Checkpoint | None,
    ) -> tuple[list[UUID], Checkpoint | None]:

        if checkpoint is None:
            modified = datetime.min.replace(tzinfo=UTC)
            last_id = None
        else:
            modified = checkpoint.modified
            last_id = checkpoint.id

        if last_id is None:
            query = SQL("""
                SELECT id, modified
                FROM content.person
                WHERE modified > {modified}
                ORDER BY modified, id
                LIMIT {batch_size};
            """).format(
                modified=Literal(modified),
                batch_size=Literal(settings.batch_size),
            )
        else:
            query = SQL("""
                SELECT id, modified
                FROM content.person
                WHERE (modified, id) > (
                    {modified},
                    {last_id}
                )
                ORDER BY modified, id
                LIMIT {batch_size};
            """).format(
                modified=Literal(modified),
                last_id=Literal(last_id),
                batch_size=Literal(settings.batch_size),
            )

        rows = self.postgres.cursor.execute(query).fetchall()

        if not rows:
            return [], checkpoint

        last_row = rows[-1]

        return (
            [row["id"] for row in rows],
            Checkpoint(
                modified=last_row["modified"],
                id=last_row["id"],
            ),
        )

    def _get_changed_genres(
        self,
        checkpoint: Checkpoint | None,
    ) -> tuple[list[UUID], Checkpoint | None]:

        if checkpoint is None:
            modified = datetime.min.replace(tzinfo=UTC)
            last_id = None
        else:
            modified = checkpoint.modified
            last_id = checkpoint.id

        if last_id is None:
            query = SQL("""
                SELECT id, modified
                FROM content.genre
                WHERE modified > {modified}
                ORDER BY modified, id
                LIMIT {batch_size};
            """).format(
                modified=Literal(modified),
                batch_size=Literal(settings.batch_size),
            )
        else:
            query = SQL("""
                SELECT id, modified
                FROM content.genre
                WHERE (modified, id) > (
                    {modified},
                    {last_id}
                )
                ORDER BY modified, id
                LIMIT {batch_size};
            """).format(
                modified=Literal(modified),
                last_id=Literal(last_id),
                batch_size=Literal(settings.batch_size),
            )

        rows = self.postgres.cursor.execute(query).fetchall()

        if not rows:
            return [], checkpoint

        last_row = rows[-1]

        return (
            [row["id"] for row in rows],
            Checkpoint(
                modified=last_row["modified"],
                id=last_row["id"],
            ),
        )

    def _get_film_works_by_persons(
        self,
        person_ids: list[UUID],
    ) -> list[UUID]:

        if not person_ids:
            return []

        query = SQL("""
            SELECT DISTINCT film_work_id
            FROM content.person_film_work
            WHERE person_id IN ({person_ids});
        """).format(
            person_ids=SQL(", ").join(Literal(person_id) for person_id in person_ids),
        )

        rows = self.postgres.cursor.execute(query).fetchall()

        return [row["film_work_id"] for row in rows]

    def _get_film_works_by_genres(
        self,
        genre_ids: list[UUID],
    ) -> list[UUID]:

        if not genre_ids:
            return []

        query = SQL("""
            SELECT DISTINCT film_work_id
            FROM content.genre_film_work
            WHERE genre_id IN ({genre_ids});
        """).format(
            genre_ids=SQL(", ").join(Literal(genre_id) for genre_id in genre_ids),
        )

        rows = self.postgres.cursor.execute(query).fetchall()

        return [row["film_work_id"] for row in rows]
