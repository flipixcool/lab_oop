def format_customer_id(id: int) -> str:
    return f"C-{id:03d}"


def format_product_id(id: int) -> str:
    return f"P-{id:03d}"


def format_order_id(id: int) -> str:
    return f"O-{id:03d}"


def parse_id(formatted: str) -> int:
    return int(formatted.split("-")[1])
