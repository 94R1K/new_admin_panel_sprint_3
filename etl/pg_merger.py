from collections import defaultdict
from dataclasses import dataclass
from uuid import UUID


@dataclass
class FilmWorkMerger:
	
	def merge(
		self,
		film_works: list[dict],
		persons: list[dict],
		genres: list[dict],
	) -> list[dict]:
		
		persons_by_film_work: dict[UUID, list[dict]] = defaultdict(list)
		genres_by_film_work: dict[UUID, list[str]] = defaultdict(list)
		
		for person in persons:
			persons_by_film_work[
				person["film_work_id"]
			].append(
				{
					"id": person["id"],
					"full_name": person["full_name"],
					"role": person["role"],
				}
			)
		
		for genre in genres:
			genres_by_film_work[
				genre["film_work_id"]
			].append(
				genre["name"]
			)
		
		result = []
		
		for film_work in film_works:
			film_work_id = film_work["id"]
			
			result.append(
				{
					"id": film_work_id,
					"title": film_work["title"],
					"description": film_work["description"],
					"imdb_rating": film_work["imdb_rating"],
					"persons": persons_by_film_work.get(
						film_work_id,
						[],
					),
					"genres": genres_by_film_work.get(
						film_work_id,
						[],
					),
				}
			)
		
		return result
