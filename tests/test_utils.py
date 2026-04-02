import pytest
from domain.utils import format_customer_id, format_product_id, format_order_id, parse_id


class TestFormatIds:
    def test_format_customer_id(self):
        assert format_customer_id(1) == "C-001"
        assert format_customer_id(42) == "C-042"
        assert format_customer_id(999) == "C-999"

    def test_format_product_id(self):
        assert format_product_id(1) == "P-001"
        assert format_product_id(7) == "P-007"

    def test_format_order_id(self):
        assert format_order_id(1) == "O-001"
        assert format_order_id(100) == "O-100"


class TestParseId:
    def test_parse_customer_id(self):
        assert parse_id("C-001") == 1
        assert parse_id("C-042") == 42

    def test_parse_product_id(self):
        assert parse_id("P-007") == 7

    def test_parse_order_id(self):
        assert parse_id("O-100") == 100
