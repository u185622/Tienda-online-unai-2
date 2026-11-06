"""Punto de entrada de la aplicación: expone TiendaService como API REST con FastAPI.

Ejecución (desde la carpeta src):
    python main.py                                 # usa las variables de entorno HOST y PORT
    uvicorn main:app --reload                      # solo este equipo
    uvicorn main:app --host 0.0.0.0 --port 8000    # accesible desde la red local
"""

import os
from typing import List

import uvicorn
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

from schemas import (
    PedidoCreate,
    PedidoRead,
    ProductoCreate,
    ProductoRead,
    UsuarioCreate,
    UsuarioRead,
    pedido_a_read,
    producto_a_read,
    usuario_a_read,
)
from services.excepciones import (
    ProductoNoEncontradoError,
    StockInsuficienteError,
    UsuarioNoEncontradoError,
    UsuarioNoEsClienteError,
)
from services.tienda_service import TiendaService

app = FastAPI(
    title="Tienda Online API",
    description="API REST de la tienda online construida sobre TiendaService.",
    version="1.0.0",
)

# Permite que el frontend (servido desde otro origen o abierto como fichero) llame a la API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Única instancia del servicio: almacena usuarios, productos y pedidos en memoria.
tienda = TiendaService()


# --- Gestión de errores de negocio -> códigos HTTP ---

def _error(codigo: int, exc: Exception) -> JSONResponse:
    """Construye una respuesta de error con el mismo formato que HTTPException."""
    return JSONResponse(status_code=codigo, content={"detail": str(exc)})


@app.exception_handler(UsuarioNoEncontradoError)
@app.exception_handler(ProductoNoEncontradoError)
async def no_encontrado_handler(_: Request, exc: Exception) -> JSONResponse:
    """El recurso solicitado no existe."""
    return _error(status.HTTP_404_NOT_FOUND, exc)


@app.exception_handler(UsuarioNoEsClienteError)
@app.exception_handler(ValueError)
async def peticion_invalida_handler(_: Request, exc: Exception) -> JSONResponse:
    """La petición no tiene sentido para la lógica de la tienda."""
    return _error(status.HTTP_400_BAD_REQUEST, exc)


@app.exception_handler(StockInsuficienteError)
async def stock_insuficiente_handler(_: Request, exc: Exception) -> JSONResponse:
    """La petición entra en conflicto con el estado actual del inventario."""
    return _error(status.HTTP_409_CONFLICT, exc)


@app.get("/", include_in_schema=False)
def raiz() -> RedirectResponse:
    """Redirige la raíz a la documentación interactiva."""
    return RedirectResponse(url="/docs")


# --- Usuarios ---

@app.post(
    "/usuarios",
    response_model=UsuarioRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Usuarios"],
)
def crear_usuario(datos: UsuarioCreate) -> UsuarioRead:
    """Registra un nuevo cliente o administrador."""
    usuario = tienda.registrar_usuario(datos.tipo, **datos.atributos())
    return usuario_a_read(usuario)


@app.get("/usuarios", response_model=List[UsuarioRead], tags=["Usuarios"])
def listar_usuarios() -> List[UsuarioRead]:
    """Devuelve todos los usuarios registrados."""
    return [usuario_a_read(usuario) for usuario in tienda.listar_usuarios()]


@app.get(
    "/usuarios/{usuario_id}",
    response_model=UsuarioRead,
    tags=["Usuarios"],
    responses={404: {"description": "Usuario no encontrado"}},
)
def obtener_usuario(usuario_id: str) -> UsuarioRead:
    """Devuelve un usuario concreto."""
    return usuario_a_read(tienda.obtener_usuario(usuario_id))


@app.get(
    "/usuarios/{cliente_id}/pedidos",
    response_model=List[PedidoRead],
    tags=["Pedidos"],
    responses={404: {"description": "Usuario no encontrado"}},
)
def listar_pedidos_cliente(cliente_id: str) -> List[PedidoRead]:
    """Devuelve el historial de pedidos de un cliente ordenado por fecha."""
    return [pedido_a_read(pedido) for pedido in tienda.listar_pedidos_usuario(cliente_id)]


# --- Productos ---

@app.post(
    "/productos",
    response_model=ProductoRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Productos"],
)
def crear_producto(datos: ProductoCreate) -> ProductoRead:
    """Crea un producto genérico, electrónico o de ropa."""
    producto = tienda.crear_producto(datos.tipo, **datos.atributos())
    return producto_a_read(producto)


@app.get("/productos", response_model=List[ProductoRead], tags=["Productos"])
def listar_productos() -> List[ProductoRead]:
    """Devuelve todos los productos del inventario."""
    return [producto_a_read(producto) for producto in tienda.listar_productos()]


@app.get(
    "/productos/{producto_id}",
    response_model=ProductoRead,
    tags=["Productos"],
    responses={404: {"description": "Producto no encontrado"}},
)
def obtener_producto(producto_id: str) -> ProductoRead:
    """Devuelve un producto concreto."""
    return producto_a_read(tienda.obtener_producto(producto_id))


@app.delete(
    "/productos/{producto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Productos"],
    responses={404: {"description": "Producto no encontrado"}},
)
def eliminar_producto(producto_id: str) -> Response:
    """Elimina un producto del inventario."""
    tienda.eliminar_producto(producto_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Pedidos ---

@app.post(
    "/pedidos",
    response_model=PedidoRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Pedidos"],
    responses={
        400: {"description": "El usuario no es un cliente"},
        404: {"description": "Cliente o producto no encontrado"},
        409: {"description": "Stock insuficiente"},
    },
)
def crear_pedido(datos: PedidoCreate) -> PedidoRead:
    """Crea un pedido verificando cliente, productos y stock disponible."""
    pedido = tienda.realizar_pedido(datos.cliente_id, datos.cantidades())
    return pedido_a_read(pedido)


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "8000")),
    )
