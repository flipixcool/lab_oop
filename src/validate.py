from typing import Any


class Validators:
    @staticmethod
    def validate_not_empty(value: Any, field_name: str):
        if value is None or (isinstance(value, str) and not value.strip()) or (isinstance(value, list) and len(value) == 0):
            raise ValueError(f"{field_name} не может быть пустым")

    @staticmethod
    def validate_positive(value: float | int | None, field_name: str):
        if value is None:
            raise ValueError(f"{field_name} не может быть пустым")
        if value < 0:
            raise ValueError(f"{field_name} не может быть меньше 0")

    @staticmethod
    def validate_range(value: int | None, field_name: str, min_val: int, max_val: int):
        if value is None:
            raise ValueError(f"{field_name} не может быть пустым")
        if not min_val <= value <= max_val:
            raise ValueError(f"{field_name} должен быть от {min_val} до {max_val}")
