"""Capa de servicios que centraliza las operaciones de la tienda online."""

from typing import Dict, List

from models.pedido import Pedido
from models.producto import Producto, ProductoElectronico, ProductoRopa
from models.usuario import Administrador, Cliente, Usuario
from services.excepciones import (
    ProductoNoEncontradoError,
    StockInsuficienteError,
    UsuarioNoEncontradoError,
    UsuarioNoEsClienteError,
)


class TiendaService:
    """Intermediario entre los usuarios y los productos de la tienda."""

    def __init__(self) -> None:
        """Inicializa los almacenes en memoria de usuarios, productos y pedidos."""
        self.usuarios: Dict[str, Usuario] = {}
        self.productos: Dict[str, Producto] = {}
        self.pedidos: List[Pedido] = []

    # --- Usuarios ---

    def registrar_usuario(self, tipo: str, **atributos: str) -> Usuario:
        """Registra un nuevo usuario del tipo indicado ('cliente' o 'administrador')."""
        if tipo == "cliente":
            usuario: Usuario = Cliente(**atributos)
        elif tipo == "administrador":
            usuario = Administrador(**atributos)
        else:
            raise ValueError(f"Tipo de usuario desconocido: {tipo}")

        self.usuarios[usuario.id] = usuario
        return usuario

    def obtener_usuario(self, usuario_id: str) -> Usuario:
        """Devuelve el usuario con el identificador indicado."""
        usuario = self.usuarios.get(usuario_id)
        if usuario is None:
            raise UsuarioNoEncontradoError(usuario_id)
        return usuario

    def listar_usuarios(self) -> List[Usuario]:
        """Devuelve la lista de todos los usuarios registrados."""
        return list(self.usuarios.values())

    # --- Productos ---

    def crear_producto(self, tipo: str, **atributos) -> Producto:
        """Construye un producto del tipo indicado y lo añade al inventario."""
        if tipo == "generico":
            producto: Producto = Producto(**atributos)
        elif tipo == "electronico":
            producto = ProductoElectronico(**atributos)
        elif tipo == "ropa":
            producto = ProductoRopa(**atributos)
        else:
            raise ValueError(f"Tipo de producto desconocido: {tipo}")

        return self.agregar_producto(producto)

    def agregar_producto(self, producto: Producto) -> Producto:
        """Añade al inventario un producto ya construido de cualquier categoría."""
        self.productos[producto.id] = producto
        return producto

    def obtener_producto(self, producto_id: str) -> Producto:
        """Devuelve el producto con el identificador indicado."""
        producto = self.productos.get(producto_id)
        if producto is None:
            raise ProductoNoEncontradoError(producto_id)
        return producto

    def eliminar_producto(self, producto_id: str) -> None:
        """Elimina un producto del inventario a partir de su identificador."""
        if self.productos.pop(producto_id, None) is None:
            raise ProductoNoEncontradoError(producto_id)

    def listar_productos(self) -> List[Producto]:
        """Devuelve la lista de todos los productos disponibles en la tienda."""
        return list(self.productos.values())

    # --- Pedidos ---

    def realizar_pedido(self, usuario_id: str, cantidades: Dict[str, int]) -> Pedido:
        """Verifica usuario y stock, genera el pedido y descuenta el inventario."""
        usuario = self.obtener_usuario(usuario_id)
        if not isinstance(usuario, Cliente):
            raise UsuarioNoEsClienteError(usuario_id)

        # Se valida todo el pedido antes de tocar el stock.
        productos_pedido: Dict[Producto, int] = {}
        for producto_id, cantidad in cantidades.items():
            producto = self.obtener_producto(producto_id)
            if not producto.hay_stock(cantidad):
                raise StockInsuficienteError(producto_id, producto.stock, cantidad)
            productos_pedido[producto] = cantidad

        for producto, cantidad in productos_pedido.items():
            producto.actualizar_stock(-cantidad)

        pedido = Pedido(usuario, productos_pedido)
        self.pedidos.append(pedido)
        return pedido

    def listar_pedidos_usuario(self, usuario_id: str) -> List[Pedido]:
        """Lista los pedidos de un usuario ordenados por fecha."""
        self.obtener_usuario(usuario_id)
        pedidos_usuario = [pedido for pedido in self.pedidos if pedido.cliente.id == usuario_id]
        return sorted(pedidos_usuario, key=lambda pedido: pedido.fecha)
