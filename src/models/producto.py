"""Modelos de producto para la tienda online."""

import uuid


class Producto:
    """Producto genérico disponible en el inventario de la tienda."""

    def __init__(self, nombre: str, precio: float, stock: int) -> None:
        """Crea un producto asignándole un identificador único automático."""
        self.id: str = str(uuid.uuid4())
        self.nombre: str = nombre
        self.precio: float = precio
        self.stock: int = stock

    def hay_stock(self, cantidad: int) -> bool:
        """Indica si hay stock suficiente para la cantidad solicitada."""
        return self.stock >= cantidad

    def actualizar_stock(self, cantidad: int) -> None:
        """Actualiza el stock (positivo para reposición, negativo para venta)."""
        self.stock += cantidad

    def __str__(self) -> str:
        """Devuelve las características principales del producto."""
        return f"[{self.id}] {self.nombre} - {self.precio:.2f} EUR (stock: {self.stock})"


class ProductoElectronico(Producto):
    """Producto electrónico con meses de garantía."""

    def __init__(self, nombre: str, precio: float, stock: int, meses_garantia: int) -> None:
        """Crea un producto electrónico añadiendo los meses de garantía."""
        super().__init__(nombre, precio, stock)
        self.meses_garantia: int = meses_garantia

    def __str__(self) -> str:
        """Devuelve las características del producto incluyendo la garantía."""
        return f"{super().__str__()} - Garantía: {self.meses_garantia} meses"


class ProductoRopa(Producto):
    """Producto de ropa con talla y color."""

    def __init__(self, nombre: str, precio: float, stock: int, talla: str, color: str) -> None:
        """Crea un producto de ropa añadiendo la talla y el color."""
        super().__init__(nombre, precio, stock)
        self.talla: str = talla
        self.color: str = color

    def __str__(self) -> str:
        """Devuelve las características del producto incluyendo talla y color."""
        return f"{super().__str__()} - Talla: {self.talla}, Color: {self.color}"
