from dataclasses import dataclass
from uuid import UUID

import psycopg
from psycopg.sql import SQL, Literal

from backoff.decorator import backoff
from config.settings import settings


@dataclass
class PostgresEnricher:
    cursor: psycopg.ClientCursor

    @backoff(
	    start_sleep_time=settings.backoff_seconds,
        exceptions=(
            psycopg.OperationalError,
        )
    )
    def get_film_works(
	    self,
	    film_work_ids: set[UUID],
    ) -> list[dict]:
	    if not film_work_ids:
		    return []
    
	    query = SQL("""
	                SELECT
	                    id,
	                    title,
	                    description,
	                    rating AS imdb_rating
	                FROM content.film_work
	                WHERE id IN ({film_work_ids});
	                """).format(
		    film_work_ids=SQL(", ").join(
			    Literal(film_work_id)
			    for film_work_id in film_work_ids
		    ),
	    )
	    
	    return self.cursor.execute(query).fetchall()

    @backoff(
	    start_sleep_time=settings.backoff_seconds,
        exceptions=(
            psycopg.OperationalError,
        )
    )
    def get_persons(
        self,
        film_work_ids: set[UUID],
    ) -> list[dict]:

        if not film_work_ids:
            return []

        query = SQL("""
            SELECT
                pfw.film_work_id,
                p.id,
                p.full_name,
                pfw.role
            FROM content.person_film_work pfw
            JOIN content.person p
                ON p.id = pfw.person_id
            WHERE pfw.film_work_id IN ({film_work_ids});
        """).format(
            film_work_ids=SQL(", ").join(
                Literal(film_work_id)
                for film_work_id in film_work_ids
            ),
        )

        return self.cursor.execute(query).fetchall()

    @backoff(
	    start_sleep_time=settings.backoff_seconds,
        exceptions=(
            psycopg.OperationalError,
        )
    )
    def get_genres(
        self,
        film_work_ids: set[UUID],
    ) -> list[dict]:

        if not film_work_ids:
            return []

        query = SQL("""
            SELECT
                gfw.film_work_id,
                g.id,
                g.name
            FROM content.genre_film_work gfw
            JOIN content.genre g
                ON g.id = gfw.genre_id
            WHERE gfw.film_work_id IN ({film_work_ids});
        """).format(
            film_work_ids=SQL(", ").join(
                Literal(film_work_id)
                for film_work_id in film_work_ids
            ),
        )

        return self.cursor.execute(query).fetchall()
