"""Esquemas Pydantic de entrada (peticiones) y salida (respuestas) de la API."""

from datetime import datetime
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, model_validator

from models.pedido import Pedido
from models.producto import Producto, ProductoElectronico, ProductoRopa
from models.usuario import Cliente, Usuario

EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


# --- Usuarios ---

class UsuarioCreate(BaseModel):
    """Datos necesarios para registrar un usuario."""

    nombre: str = Field(min_length=1, examples=["Juan"])
    email: str = Field(pattern=EMAIL_PATTERN, examples=["juan@planetexpress.com"])
    tipo: Literal["cliente", "administrador"] = "cliente"
    direccion: Optional[str] = Field(default=None, examples=["Calle Delivery 1"])

    @model_validator(mode="after")
    def validar_direccion(self) -> "UsuarioCreate":
        """Los clientes deben indicar una dirección postal."""
        if self.tipo == "cliente" and not self.direccion:
            raise ValueError("La dirección postal es obligatoria para los clientes")
        return self

    def atributos(self) -> Dict[str, str]:
        """Devuelve los atributos que espera el constructor del tipo de usuario."""
        atributos = {"nombre": self.nombre, "email": self.email}
        if self.tipo == "cliente":
            atributos["direccion"] = self.direccion
        return atributos


class UsuarioRead(BaseModel):
    """Información de un usuario devuelta al cliente."""

    id: str
    nombre: str
    email: str
    es_admin: bool
    tipo: Literal["cliente", "administrador"]
    direccion: Optional[str] = None


# --- Productos ---

class ProductoCreate(BaseModel):
    """Datos necesarios para crear un producto de cualquier tipo."""

    tipo: Literal["generico", "electronico", "ropa"] = "generico"
    nombre: str = Field(min_length=1, examples=["Portátil"])
    precio: float = Field(gt=0, examples=[899.99])
    stock: int = Field(ge=0, examples=[10])
    meses_garantia: Optional[int] = Field(default=None, ge=0, examples=[24])
    talla: Optional[str] = Field(default=None, examples=["M"])
    color: Optional[str] = Field(default=None, examples=["Azul"])

    @model_validator(mode="after")
    def validar_atributos_tipo(self) -> "ProductoCreate":
        """Comprueba que los atributos adicionales encajan con el tipo de producto."""
        es_electronico = self.tipo == "electronico"
        es_ropa = self.tipo == "ropa"

        if es_electronico and self.meses_garantia is None:
            raise ValueError("Los productos electrónicos requieren 'meses_garantia'")
        if es_ropa and (not self.talla or not self.color):
            raise ValueError("Los productos de ropa requieren 'talla' y 'color'")
        if not es_electronico and self.meses_garantia is not None:
            raise ValueError("'meses_garantia' solo aplica a productos electrónicos")
        if not es_ropa and (self.talla is not None or self.color is not None):
            raise ValueError("'talla' y 'color' solo aplican a productos de ropa")
        return self

    def atributos(self) -> Dict[str, object]:
        """Devuelve los atributos que espera el constructor del tipo de producto."""
        return self.model_dump(exclude={"tipo"}, exclude_none=True)


class ProductoRead(BaseModel):
    """Información de un producto devuelta al cliente."""

    id: str
    tipo: Literal["generico", "electronico", "ropa"]
    nombre: str
    precio: float
    stock: int
    meses_garantia: Optional[int] = None
    talla: Optional[str] = None
    color: Optional[str] = None


# --- Pedidos ---

class PedidoItemCreate(BaseModel):
    """Línea de pedido: producto y cantidad solicitada."""

    producto_id: str
    cantidad: int = Field(gt=0, examples=[1])


class PedidoCreate(BaseModel):
    """Datos necesarios para crear un pedido."""

    cliente_id: str
    items: List[PedidoItemCreate] = Field(min_length=1)

    def cantidades(self) -> Dict[str, int]:
        """Agrupa las líneas por producto sumando las cantidades repetidas."""
        cantidades: Dict[str, int] = {}
        for item in self.items:
            cantidades[item.producto_id] = cantidades.get(item.producto_id, 0) + item.cantidad
        return cantidades


class PedidoItemRead(BaseModel):
    """Línea de un pedido devuelta al cliente."""

    producto_id: str
    nombre: str
    precio_unitario: float
    cantidad: int
    subtotal: float


class PedidoRead(BaseModel):
    """Pedido completo devuelto al cliente."""

    id: str
    fecha: datetime
    cliente_id: str
    cliente_nombre: str
    total: float
    items: List[PedidoItemRead]


# --- Conversión de objetos de dominio a esquemas de salida ---

def usuario_a_read(usuario: Usuario) -> UsuarioRead:
    """Convierte un Usuario del dominio en su esquema de respuesta."""
    return UsuarioRead(
        id=usuario.id,
        nombre=usuario.nombre,
        email=usuario.email,
        es_admin=usuario.is_admin(),
        tipo="cliente" if isinstance(usuario, Cliente) else "administrador",
        direccion=getattr(usuario, "direccion", None),
    )


def producto_a_read(producto: Producto) -> ProductoRead:
    """Convierte un Producto del dominio en su esquema de respuesta."""
    if isinstance(producto, ProductoElectronico):
        tipo = "electronico"
    elif isinstance(producto, ProductoRopa):
        tipo = "ropa"
    else:
        tipo = "generico"

    return ProductoRead(
        id=producto.id,
        tipo=tipo,
        nombre=producto.nombre,
        precio=producto.precio,
        stock=producto.stock,
        meses_garantia=getattr(producto, "meses_garantia", None),
        talla=getattr(producto, "talla", None),
        color=getattr(producto, "color", None),
    )


def pedido_a_read(pedido: Pedido) -> PedidoRead:
    """Convierte un Pedido del dominio en su esquema de respuesta."""
    items = [
        PedidoItemRead(
            producto_id=producto.id,
            nombre=producto.nombre,
            precio_unitario=producto.precio,
            cantidad=cantidad,
            subtotal=round(producto.precio * cantidad, 2),
        )
        for producto, cantidad in pedido.productos.items()
    ]
    return PedidoRead(
        id=pedido.id,
        fecha=pedido.fecha,
        cliente_id=pedido.cliente.id,
        cliente_nombre=pedido.cliente.nombre,
        total=round(pedido.calcular_total(), 2),
        items=items,
    )
