class ShopError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f"ShopError: {self.message}"


class InsufficientStockError(ShopError):
    def __init__(self, product_name: str, requested: int, available: int):
        self.product_name = product_name
        self.requested = requested
        self.available = available
        super().__init__(
            f"Not enough stock for '{product_name}': requested {requested}, available {available}"
        )

    def __str__(self):
        return (
            f"InsufficientStockError: '{self.product_name}' — "
            f"requested {self.requested}, available {self.available}"
        )
