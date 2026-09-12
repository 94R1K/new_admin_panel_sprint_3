import abc
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass
class Checkpoint:
    modified: datetime
    id: UUID | None = None


class BaseStorage(abc.ABC):
    """Абстрактное хранилище состояния."""

    @abc.abstractmethod
    def save_state(self, state: dict[str, Any]) -> None:
        """Сохранить состояние."""

    @abc.abstractmethod
    def retrieve_state(self) -> dict[str, Any]:
        """Получить состояние."""


class JsonFileStorage(BaseStorage):
    """Хранилище состояния в JSON-файле."""

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def save_state(self, state: dict[str, Any]) -> None:
        with open(self.file_path, "w") as file:
            json.dump(state, file, indent=2)

    def retrieve_state(self) -> dict[str, Any]:
        try:
            with open(self.file_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}


class ETLState:
    """Класс для работы с состоянием ETL."""

    def __init__(self, storage: BaseStorage) -> None:
        self.storage = storage
        self.data = storage.retrieve_state()

    def set_checkpoint(
        self,
        key: str,
        checkpoint: Checkpoint,
    ) -> None:
        self.data[key] = {
            "modified": checkpoint.modified.isoformat(),
            "id": str(checkpoint.id) if checkpoint.id else None,
        }

        self.storage.save_state(self.data)

    def get_checkpoint(
        self,
        key: str,
    ) -> Checkpoint | None:
        data = self.data.get(key)

        if data is None:
            return None

        return Checkpoint(
            modified=datetime.fromisoformat(data["modified"]),
            id=UUID(data["id"]) if data["id"] else None,
        )
