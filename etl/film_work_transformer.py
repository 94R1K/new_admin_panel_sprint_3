from dataclasses import dataclass


@dataclass
class FilmWorkTransformer:
	
	def transform(self, film_work: dict) -> dict:
		persons = film_work["persons"]
		
		directors = [
			{
				"id": str(person["id"]),
				"name": person["full_name"],
			}
			for person in persons
			if person["role"] == "director"
		]
		
		actors = [
			{
				"id": str(person["id"]),
				"name": person["full_name"],
			}
			for person in persons
			if person["role"] == "actor"
		]
		
		writers = [
			{
				"id": str(person["id"]),
				"name": person["full_name"],
			}
			for person in persons
			if person["role"] == "writer"
		]
		
		return {
			"_index": "movies",
			"_id": str(film_work["id"]),
			"_source": {
				"id": str(film_work["id"]),
				"title": film_work["title"],
				"description": film_work["description"],
				"imdb_rating": film_work["imdb_rating"],
				"genres": film_work["genres"],
				"directors_names": [
					person["full_name"]
					for person in persons
					if person["role"] == "director"
				],
				"actors_names": [
					person["full_name"]
					for person in persons
					if person["role"] == "actor"
				],
				"writers_names": [
					person["full_name"]
					for person in persons
					if person["role"] == "writer"
				],
				"directors": directors,
				"actors": actors,
				"writers": writers,
			},
		}
	
	def transform_batch(
		self,
		film_works: list[dict],
	) -> list[dict]:
		return [
			self.transform(film_work)
			for film_work in film_works
		]
