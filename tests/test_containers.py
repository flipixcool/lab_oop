import pytest
from domain.containers import EntityCollection


@pytest.fixture
def col():
    return EntityCollection([1, 2, 3, 4, 5])


class TestEntityCollectionInit:
    def test_empty_collection(self):
        c = EntityCollection()
        assert len(c) == 0

    def test_with_initial_items(self, col):
        assert len(col) == 5

    def test_does_not_mutate_original_list(self):
        original = [1, 2, 3]
        c = EntityCollection(original)
        c.add(4)
        assert len(original) == 3


class TestMagicMethods:
    def test_len(self, col):
        assert len(col) == 5

    def test_iter(self, col):
        assert list(col) == [1, 2, 3, 4, 5]

    def test_getitem(self, col):
        assert col[0] == 1
        assert col[-1] == 5

    def test_repr(self, col):
        assert "EntityCollection" in repr(col)


class TestBusinessMethods:
    def test_add(self, col):
        col.add(6)
        assert len(col) == 6
        assert col[-1] == 6

    def test_remove(self, col):
        col.remove(3)
        assert len(col) == 4
        assert 3 not in list(col)

    def test_filter_returns_new_collection(self, col):
        result = col.filter(lambda x: x % 2 == 0)
        assert list(result) == [2, 4]
        assert len(col) == 5  # оригинал не изменился

    def test_filter_empty_result(self, col):
        result = col.filter(lambda x: x > 100)
        assert len(result) == 0

    def test_sort_returns_new_collection(self):
        c = EntityCollection([3, 1, 2])
        result = c.sort(key=lambda x: x)
        assert list(result) == [1, 2, 3]
        assert list(c) == [3, 1, 2]  # оригинал не изменился

    def test_sort_reverse(self):
        c = EntityCollection([1, 2, 3])
        result = c.sort(key=lambda x: x, reverse=True)
        assert list(result) == [3, 2, 1]

    def test_find_existing(self, col):
        assert col.find(lambda x: x == 3) == 3

    def test_find_not_found(self, col):
        assert col.find(lambda x: x == 99) is None

    def test_to_list_returns_copy(self, col):
        lst = col.to_list()
        assert lst == [1, 2, 3, 4, 5]
        lst.append(99)
        assert len(col) == 5  # оригинал не изменился
