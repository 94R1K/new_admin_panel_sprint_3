import psycopg
from psycopg.rows import dict_row

from config.settings import settings
from elasticsearch import Elasticsearch
from etl.elasticsearch_loader import ElasticsearchLoader
from etl.film_work_transformer import FilmWorkTransformer
from etl.main import ETLPipeline
from etl.pg_enricher import PostgresEnricher
from etl.pg_merger import FilmWorkMerger
from etl.pg_producer import PostgresProducer
from logger import logger
from state.state import ETLState, JsonFileStorage


def main() -> None:
    postgres_dsl = {
        "dbname": settings.postgres_db,
        "user": settings.postgres_user,
        "password": settings.postgres_password,
        "host": settings.postgres_host,
        "port": settings.postgres_port,
    }

    elasticsearch_dsl = {
        "hosts": [settings.elasticsearch_host],
    }

    storage = JsonFileStorage("state.json")
    state = ETLState(storage)

    with (
        psycopg.connect(
            **postgres_dsl,
            row_factory=dict_row,
            cursor_factory=psycopg.ClientCursor,
        ) as pg_conn,
        pg_conn.cursor() as pg_cursor,
        Elasticsearch(**elasticsearch_dsl) as es_client,
    ):
        producer = PostgresProducer(
            cursor=pg_cursor,
        )

        enricher = PostgresEnricher(
            cursor=pg_cursor,
        )

        merger = FilmWorkMerger()

        transformer = FilmWorkTransformer()

        loader = ElasticsearchLoader(
            client=es_client,
        )

        pipeline = ETLPipeline(
            producer=producer,
            enricher=enricher,
            merger=merger,
            transformer=transformer,
            loader=loader,
            state=state,
        )

        pipeline.run()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("Ошибка при переносе данных из PostgreSQL в Elasticsearch")
        raise
