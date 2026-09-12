import time
from dataclasses import dataclass

from state.state import ETLState

from .elasticsearch_loader import ElasticsearchLoader
from .film_work_transformer import FilmWorkTransformer
from .pg_enricher import PostgresEnricher
from .pg_merger import FilmWorkMerger
from .pg_producer import PostgresProducer


@dataclass
class ETLPipeline:
    producer: PostgresProducer
    enricher: PostgresEnricher
    merger: FilmWorkMerger
    transformer: FilmWorkTransformer
    loader: ElasticsearchLoader
    state: ETLState

    def run(self) -> None:
        while True:
            changed = self.producer.extract(
                film_work_checkpoint=self.state.get_checkpoint("film_work"),
                person_checkpoint=self.state.get_checkpoint("person"),
                genre_checkpoint=self.state.get_checkpoint("genre"),
            )

            if not changed.film_work_ids:
                time.sleep(1)
                continue

            film_works = self.enricher.get_film_works(changed.film_work_ids)

            persons = self.enricher.get_persons(changed.film_work_ids)

            genres = self.enricher.get_genres(changed.film_work_ids)

            merged = self.merger.merge(
                film_works=film_works,
                persons=persons,
                genres=genres,
            )

            documents = self.transformer.transform_batch(merged)

            self.loader.load(documents)

            self.state.set_checkpoint(
                "film_work",
                changed.film_work_checkpoint,
            )

            self.state.set_checkpoint(
                "person",
                changed.person_checkpoint,
            )

            self.state.set_checkpoint(
                "genre",
                changed.genre_checkpoint,
            )
