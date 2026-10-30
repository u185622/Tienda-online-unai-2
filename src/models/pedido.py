"""Modelo de pedido para la tienda online."""

import uuid
from datetime import datetime
from typing import Dict

from models.producto import Producto
from models.usuario import Cliente


class Pedido:
    """Pedido realizado por un cliente sobre uno o varios productos."""

    def __init__(self, cliente: Cliente, productos: Dict[Producto, int]) -> None:
        """Crea un pedido asignándole un identificador único y la fecha actual."""
        self.id: str = str(uuid.uuid4())
        self.cliente: Cliente = cliente
        self.productos: Dict[Producto, int] = productos
        self.fecha: datetime = datetime.now()

    def calcular_total(self) -> float:
        """Calcula el importe total del pedido según precios y cantidades."""
        return sum(producto.precio * cantidad for producto, cantidad in self.productos.items())

    def __str__(self) -> str:
        """Devuelve un resumen legible del pedido."""
        return (
            f"Pedido [{self.id}] de {self.cliente.nombre} - "
            f"{self.fecha:%Y-%m-%d %H:%M} - Total: {self.calcular_total():.2f} EUR"
        )
