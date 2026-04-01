from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Callable
from uuid import uuid4
from domain.exceptions import EntityNotFoundError

T = TypeVar('T')


class Repository(ABC, Generic[T]):
    @abstractmethod
    def add(self, entity: T) -> T: ...

    @abstractmethod
    def get(self, id: str) -> T | None: ...

    @abstractmethod
    def update(self, entity: T) -> T: ...

    @abstractmethod
    def delete(self, id: str) -> bool: ...

    @abstractmethod
    def find_all(self) -> list[T]: ...

    @abstractmethod
    def find_by(self, predicate: Callable[[T], bool]) -> list[T]: ...


class InMemoryRepository(Repository[T]):
    def __init__(self):
        self._storage: dict[str, T] = {}

    def add(self, entity: T) -> T:
        entity_id = getattr(entity, 'id', None)
        if not entity_id or entity_id in self._storage:
            if entity_id in self._storage:
                del self._storage[entity_id]
            entity.id = str(uuid4())
        self._storage[entity.id] = entity
        return entity

    def get(self, id: str) -> T | None:
        return self._storage.get(id)

    def update(self, entity: T) -> T:
        if entity.id not in self._storage:
            raise EntityNotFoundError(f"Entity with id '{entity.id}' not found")
        self._storage[entity.id] = entity
        return entity

    def delete(self, id: str) -> bool:
        if id not in self._storage:
            return False
        del self._storage[id]
        return True

    def find_all(self) -> list[T]:
        return list(self._storage.values())

    def find_by(self, predicate: Callable[[T], bool]) -> list[T]:
        return [entity for entity in self._storage.values() if predicate(entity)]
