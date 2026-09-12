from datetime import datetime
from typing import TypedDict
from uuid import UUID


class Person(TypedDict):
    id: UUID
    modified: datetime


class FilmWork(TypedDict):
    id: UUID
    modified: datetime
