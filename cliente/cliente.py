"""Cliente de la API REST de la tienda online usando requests.

No importa nada del servidor: toda la comunicación es mediante peticiones HTTP.

Uso:
    python cliente.py                              # usa BASE_URL
    python cliente.py http://192.168.1.34:8000     # API en otro equipo
"""

import json
import sys

import requests

# Dirección de la API. Cambiarla por la IP del equipo servidor para la prueba en red.
BASE_URL = "http://localhost:8000"


def peticion(metodo: str, ruta: str, datos: dict | None = None, esperado: int = 200):
    """Realiza una petición, comprueba el código de estado y devuelve el JSON recibido."""
    url = f"{BASE_URL}{ruta}"
    respuesta = requests.request(metodo, url, json=datos, timeout=5)

    estado = "OK" if respuesta.status_code == esperado else "INESPERADO"
    print(f"\n{metodo} {ruta} -> {respuesta.status_code} (esperado {esperado}) [{estado}]")

    contenido = respuesta.json() if respuesta.content else None
    if contenido is not None:
        print(json.dumps(contenido, indent=2, ensure_ascii=False))
    return contenido


def titulo(texto: str) -> None:
    """Imprime un separador para cada bloque del flujo."""
    print(f"\n{'=' * 60}\n{texto}\n{'=' * 60}")


def main() -> None:
    """Ejecuta un flujo completo de uso de la tienda a través de la API."""
    print(f"Conectando con la API en {BASE_URL}")

    titulo("1. Usuarios")
    cliente = peticion("POST", "/usuarios", {
        "nombre": "Juan",
        "email": "juan@planetexpress.com",
        "tipo": "cliente",
        "direccion": "Calle Delivery 1",
    }, esperado=201)
    admin = peticion("POST", "/usuarios", {
        "nombre": "Farnsworth",
        "email": "farnsworth@planetexpress.com",
        "tipo": "administrador",
    }, esperado=201)
    peticion("GET", "/usuarios")
    peticion("GET", f"/usuarios/{cliente['id']}")

    titulo("2. Productos")
    libro = peticion("POST", "/productos", {
        "tipo": "generico", "nombre": "Libro", "precio": 14.99, "stock": 20,
    }, esperado=201)
    portatil = peticion("POST", "/productos", {
        "tipo": "electronico", "nombre": "Portátil", "precio": 899.99, "stock": 10,
        "meses_garantia": 24,
    }, esperado=201)
    camiseta = peticion("POST", "/productos", {
        "tipo": "ropa", "nombre": "Camiseta", "precio": 19.99, "stock": 50,
        "talla": "M", "color": "Verde",
    }, esperado=201)
    peticion("GET", "/productos")

    titulo("3. Pedidos")
    peticion("POST", "/pedidos", {
        "cliente_id": cliente["id"],
        "items": [
            {"producto_id": portatil["id"], "cantidad": 1},
            {"producto_id": camiseta["id"], "cantidad": 2},
        ],
    }, esperado=201)
    pedidos = peticion("GET", f"/usuarios/{cliente['id']}/pedidos")
    print(f"\n{cliente['nombre']} tiene {len(pedidos)} pedido(s); "
          f"total del último: {pedidos[-1]['total']} EUR")

    titulo("4. Gestión de errores")
    peticion("POST", "/pedidos", {
        "cliente_id": cliente["id"],
        "items": [{"producto_id": libro["id"], "cantidad": 1000}],
    }, esperado=409)
    peticion("POST", "/pedidos", {
        "cliente_id": admin["id"],
        "items": [{"producto_id": libro["id"], "cantidad": 1}],
    }, esperado=400)
    peticion("GET", "/productos/no-existe", esperado=404)
    peticion("POST", "/productos", {
        "tipo": "ropa", "nombre": "Pantalón", "precio": 39.99, "stock": 5,
    }, esperado=422)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1].rstrip("/")
    try:
        main()
    except requests.ConnectionError:
        print(f"No se pudo conectar con {BASE_URL}. ¿Está el servidor arrancado?")
