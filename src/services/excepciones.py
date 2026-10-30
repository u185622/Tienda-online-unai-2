"""Errores de negocio que puede lanzar la capa de servicios de la tienda."""


class TiendaError(Exception):
    """Error base de la lógica de la tienda."""


class UsuarioNoEncontradoError(TiendaError):
    """El usuario indicado no existe en la tienda."""

    def __init__(self, usuario_id: str) -> None:
        """Construye el mensaje a partir del identificador buscado."""
        super().__init__(f"Usuario no encontrado: {usuario_id}")


class ProductoNoEncontradoError(TiendaError):
    """El producto indicado no existe en el inventario."""

    def __init__(self, producto_id: str) -> None:
        """Construye el mensaje a partir del identificador buscado."""
        super().__init__(f"Producto no encontrado: {producto_id}")


class UsuarioNoEsClienteError(TiendaError):
    """El usuario existe pero no es un cliente, por lo que no puede hacer pedidos."""

    def __init__(self, usuario_id: str) -> None:
        """Construye el mensaje a partir del identificador del usuario."""
        super().__init__(f"El usuario {usuario_id} no es un cliente y no puede realizar pedidos")


class StockInsuficienteError(TiendaError):
    """No hay stock suficiente de un producto para la cantidad solicitada."""

    def __init__(self, producto_id: str, disponible: int, solicitado: int) -> None:
        """Construye el mensaje indicando el stock disponible y el solicitado."""
        super().__init__(
            f"Stock insuficiente para el producto {producto_id}: "
            f"disponible {disponible}, solicitado {solicitado}"
        )
