from contextlib import closing

from database.elasticsearch.client import ElasticsearchClient
from database.postgres.client import PostgresClient
from etl.elasticsearch_loader import ElasticsearchLoader
from etl.film_work_transformer import FilmWorkTransformer
from etl.main import ETLPipeline
from etl.pg_enricher import PostgresEnricher
from etl.pg_merger import FilmWorkMerger
from etl.pg_producer import PostgresProducer
from logger import logger
from state.state import ETLState, JsonFileStorage


def main() -> None:
    storage = JsonFileStorage("state.json")
    state = ETLState(storage)

    with (
        closing(PostgresClient.create()) as postgres,
        closing(ElasticsearchClient.create()) as elasticsearch,
    ):
        producer = PostgresProducer(
            postgres=postgres,
        )

        enricher = PostgresEnricher(
            postgres=postgres,
        )

        merger = FilmWorkMerger()

        transformer = FilmWorkTransformer()

        loader = ElasticsearchLoader(
            elasticsearch=elasticsearch,
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
