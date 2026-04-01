import pytest
from domain.validators import Validators
from domain.exceptions import ShopError, ValidationError, InsufficientStockError


class TestExceptionsStr:
    def test_shop_error_str(self):
        e = ShopError("something went wrong")
        assert str(e) == "ShopError: something went wrong"

    def test_validation_error_str_with_field(self):
        e = ValidationError("не может быть пустым", "Имя")
        assert "[Имя]" in str(e)

    def test_validation_error_str_without_field(self):
        e = ValidationError("что-то пошло не так")
        assert str(e) == "ValidationError: что-то пошло не так"

    def test_insufficient_stock_error_str(self):
        e = InsufficientStockError("Пицца", 5, 2)
        assert "Пицца" in str(e)
        assert "5" in str(e)
        assert "2" in str(e)


class TestValidateNotEmpty:
    def test_none_raises(self):
        with pytest.raises(ValidationError):
            Validators.validate_not_empty(None, "field")

    def test_empty_string_raises(self):
        with pytest.raises(ValidationError):
            Validators.validate_not_empty("", "field")

    def test_whitespace_string_raises(self):
        with pytest.raises(ValidationError):
            Validators.validate_not_empty("   ", "field")

    def test_empty_list_raises(self):
        with pytest.raises(ValidationError):
            Validators.validate_not_empty([], "field")

    def test_valid_string_passes(self):
        Validators.validate_not_empty("hello", "field")

    def test_valid_list_passes(self):
        Validators.validate_not_empty([1, 2], "field")


class TestValidatePositive:
    def test_negative_raises(self):
        with pytest.raises(ValidationError):
            Validators.validate_positive(-1, "field")

    def test_zero_raises(self):
        with pytest.raises(ValidationError):
            Validators.validate_positive(0, "field")

    def test_none_raises(self):
        with pytest.raises(ValidationError):
            Validators.validate_positive(None, "field")

    def test_positive_passes(self):
        Validators.validate_positive(1, "field")
        Validators.validate_positive(0.01, "field")


class TestValidateNonNegative:
    def test_negative_raises(self):
        with pytest.raises(ValidationError):
            Validators.validate_non_negative(-1, "field")

    def test_none_raises(self):
        with pytest.raises(ValidationError):
            Validators.validate_non_negative(None, "field")

    def test_zero_passes(self):
        Validators.validate_non_negative(0, "field")

    def test_positive_passes(self):
        Validators.validate_non_negative(5, "field")


class TestValidateRange:
    def test_below_min_raises(self):
        with pytest.raises(ValidationError):
            Validators.validate_range(-1, "field", 0, 100)

    def test_above_max_raises(self):
        with pytest.raises(ValidationError):
            Validators.validate_range(101, "field", 0, 100)

    def test_none_raises(self):
        with pytest.raises(ValidationError):
            Validators.validate_range(None, "field", 0, 100)

    def test_on_min_boundary_passes(self):
        Validators.validate_range(0, "field", 0, 100)

    def test_on_max_boundary_passes(self):
        Validators.validate_range(100, "field", 0, 100)

    def test_inside_range_passes(self):
        Validators.validate_range(50, "field", 0, 100)


class TestValidateType:
    def test_wrong_type_raises(self):
        with pytest.raises(ValidationError):
            Validators.validate_type("string", "field", int)

    def test_correct_type_passes(self):
        Validators.validate_type(42, "field", int)
        Validators.validate_type("hello", "field", str)


class TestValidateEnum:
    def test_value_not_in_allowed_raises(self):
        with pytest.raises(ValidationError):
            Validators.validate_enum("vip", "field", ["active", "inactive"])

    def test_value_in_allowed_passes(self):
        Validators.validate_enum("active", "field", ["active", "inactive"])
