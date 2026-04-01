from typing import Any
from domain.exceptions import ValidationError


class Validators:
    @staticmethod
    def validate_not_empty(value: Any, field_name: str):
        if value is None or (isinstance(value, str) and not value.strip()) or (isinstance(value, list) and len(value) == 0):
            raise ValidationError(f"{field_name} не может быть пустым", field_name)

    @staticmethod
    def validate_positive(value: float | int | None, field_name: str):
        if value is None:
            raise ValidationError(f"{field_name} не может быть пустым", field_name)
        if value <= 0:
            raise ValidationError(f"{field_name} должен быть больше 0", field_name)

    @staticmethod
    def validate_range(value: int | None, field_name: str, min_val: int, max_val: int):
        if value is None:
            raise ValidationError(f"{field_name} не может быть пустым", field_name)
        if not min_val <= value <= max_val:
            raise ValidationError(f"{field_name} должен быть от {min_val} до {max_val}", field_name)

    @staticmethod
    def validate_type(value: Any, field_name: str, expected_type: type):
        if not isinstance(value, expected_type):
            raise ValidationError(
                f"{field_name} должен быть типа {expected_type.__name__}, получен {type(value).__name__}",
                field_name
            )

    @staticmethod
    def validate_enum(value: Any, field_name: str, allowed: list):
        if value not in allowed:
            raise ValidationError(
                f"{field_name} должен быть одним из {allowed}, получено '{value}'",
                field_name
            )
