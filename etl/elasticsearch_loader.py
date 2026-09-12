from dataclasses import dataclass

from elastic_transport import ConnectionError as ElasticConnectionError
from elastic_transport import ConnectionTimeout as ElasticConnectionTimeout
from elasticsearch.helpers import BulkIndexError, bulk

from backoff.decorator import backoff
from config.settings import settings
from elasticsearch import Elasticsearch


@dataclass
class ElasticsearchLoader:
    client: Elasticsearch

    @backoff(
        start_sleep_time=settings.backoff_seconds,
        exceptions=(
            ElasticConnectionError,
            ElasticConnectionTimeout,
        ),
    )
    def load(self, documents: list[dict]) -> None:
	    if not documents:
		    return
	    
	    try:
		    bulk(
			    self.client,
			    documents,
		    )
	    except BulkIndexError as exc:
		    print(exc.errors[:3])
		    raise
