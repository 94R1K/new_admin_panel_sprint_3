from dataclasses import dataclass

from elastic_transport import ConnectionError as ElasticConnectionError
from elastic_transport import ConnectionTimeout as ElasticConnectionTimeout
from elasticsearch.helpers import BulkIndexError, bulk

from backoff.decorator import backoff
from config.settings import settings
from database.elasticsearch.client import ElasticsearchClient
from logger import logger


@dataclass
class ElasticsearchLoader:
    elasticsearch: ElasticsearchClient

    @backoff(
        start_sleep_time=settings.backoff_seconds,
        exceptions=(
            ElasticConnectionError,
            ElasticConnectionTimeout,
        ),
        reconnect=lambda loader: loader.elasticsearch.reconnect(),
    )
    def load(self, documents: list[dict]) -> None:
        if not documents:
            return

        try:
            bulk(
                self.elasticsearch.client,
                documents,
            )
        except BulkIndexError as exc:
            logger.exception(
                "Не удалось загрузить %d документов. Первые ошибки: %s",
                len(exc.errors),
                exc.errors[:3],
            )
            raise
