from typing import TypeVar, Generic, Callable, Iterator

T = TypeVar('T')


class EntityCollection(Generic[T]):
    def __init__(self, items: list[T] | None = None):
        self._items: list[T] = list(items) if items else []

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[T]:
        return iter(self._items)

    def __getitem__(self, index: int) -> T:
        return self._items[index]

    def __repr__(self) -> str:
        return f"EntityCollection({self._items!r})"

    def add(self, item: T) -> None:
        self._items.append(item)

    def remove(self, item: T) -> None:
        self._items.remove(item)

    def filter(self, predicate: Callable[[T], bool]) -> "EntityCollection[T]":
        return EntityCollection([item for item in self._items if predicate(item)])

    def sort(self, key: Callable[[T], any], reverse: bool = False) -> "EntityCollection[T]":
        return EntityCollection(sorted(self._items, key=key, reverse=reverse))

    def find(self, predicate: Callable[[T], bool]) -> T | None:
        return next((item for item in self._items if predicate(item)), None)

    def to_list(self) -> list[T]:
        return list(self._items)
