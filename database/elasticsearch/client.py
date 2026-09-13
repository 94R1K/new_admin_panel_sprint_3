import contextlib
from dataclasses import dataclass

from config.settings import settings
from elasticsearch import Elasticsearch


@dataclass
class ElasticsearchClient:
    client: Elasticsearch

    @classmethod
    def create(cls) -> "ElasticsearchClient":
        return cls(
            client=Elasticsearch(
                settings.elasticsearch_host,
                max_retries=0,
            ),
        )

    def reconnect(self) -> None:
        with contextlib.suppress(Exception):
            self.client.close()

        self.client = Elasticsearch(
            settings.elasticsearch_host,
            max_retries=0,
        )

    def close(self) -> None:
        self.client.close()
