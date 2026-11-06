# Tienda Online — DevOps

Hecho por **Unai Lama Pérez** para la asignatura de Arquitectura del Software.

## ¿De qué va esto?

Es una tienda online hecha en Python. Empezó en la Práctica 1 como un programa de consola para
practicar la programación orientada a objetos, y en la Práctica 2 la convertí en una API REST con
FastAPI para poder usarla desde fuera.

En la tienda hay usuarios, productos y pedidos. Los usuarios pueden ser clientes o administradores,
y solo los clientes pueden hacer pedidos. Cuando un cliente compra algo, la API mira si queda stock
suficiente; si lo hay, crea el pedido, calcula el total y resta las unidades del inventario. Si algo
va mal (el producto no existe, no hay stock...) devuelve el código de error que toca.

Hay tres tipos de productos: los normales, los electrónicos (que tienen meses de garantía) y la ropa
(que tiene talla y color).

En este repositorio está el proyecto, trabajado con Git, ramas y Pull Requests, y la API se puede
ejecutar en un contenedor de Docker.

## Cómo está organizado

```
├── src/                    La API (lo que se ejecuta en el servidor)
│   ├── main.py             Aplicación FastAPI con todos los endpoints
│   ├── schemas.py          Esquemas de Pydantic para validar lo que entra y sale
│   ├── models/             Producto, Usuario y Pedido
│   └── services/           TiendaService (la lógica de la tienda) y las excepciones
├── cliente/cliente.py      Un cliente en Python que prueba la API con requests
├── frontend/               Una web para usar la tienda (Streamlit, o HTML + JavaScript)
├── requirements.txt        Librerías de la API (las que se instalan en la imagen de Docker)
├── requirements-clientes.txt  Librerías extra para el cliente y el frontend
├── .github/workflows/      Build, prueba y publicación automática de la imagen
├── dockerfile              Cómo se construye la imagen de Docker
└── .dockerignore           Lo que Docker no tiene que meter en la imagen
```

## Cómo ejecutarlo en local

Primero instala las librerías. Con `requirements.txt` basta para la API; si también quieres usar el
cliente y el frontend, instala `requirements-clientes.txt`, que ya incluye las dos cosas:

```bash
python -m pip install -r requirements-clientes.txt
```

Luego arranca la API desde la carpeta `src`:

```bash
cd src
python main.py
```

(También vale `uvicorn main:app --reload`, que reinicia solo cuando cambias el código.)

Y abre http://localhost:8000/docs en el navegador. Ahí sale la documentación de Swagger y se puede
probar cada endpoint directamente. Los datos se guardan en memoria, así que si reinicias el servidor
se pierde todo.

Con la API arrancada también puedes probar el cliente o el frontend:

```bash
python cliente/cliente.py
streamlit run frontend/streamlit_app.py
```

## Endpoints

| Método | Ruta | Qué hace |
|---|---|---|
| POST | `/usuarios` | Crea un usuario (cliente o administrador) |
| GET | `/usuarios` | Lista los usuarios |
| GET | `/usuarios/{usuario_id}` | Devuelve un usuario |
| GET | `/usuarios/{cliente_id}/pedidos` | Pedidos de un cliente |
| POST | `/productos` | Crea un producto (generico, electronico o ropa) |
| GET | `/productos` | Lista los productos |
| GET | `/productos/{producto_id}` | Devuelve un producto |
| DELETE | `/productos/{producto_id}` | Elimina un producto |
| POST | `/pedidos` | Crea un pedido |

Si algo sale mal, la API devuelve 400 (el usuario no es cliente), 404 (no existe el usuario o el
producto), 409 (no hay stock) o 422 (los datos no son válidos).

## Docker

La API también se puede ejecutar en un contenedor, sin tener que instalar Python ni nada más que
Docker. El `dockerfile` parte de `python:3.12-slim`, instala lo que hay en `requirements.txt`, copia
el código de `src/` y arranca la API con un usuario sin privilegios (no como root).

### Construir la imagen

Desde la carpeta raíz del repositorio:

```bash
docker build -t tienda-online:1.0 -f dockerfile .
```

### Ejecutarla

```bash
docker run --rm -p 8000:8000 tienda-online:1.0
```

El `-p 8000:8000` conecta el puerto 8000 de tu ordenador con el del contenedor. Si quieres dejarlo
funcionando en segundo plano:

```bash
docker run -d --name tienda -p 8000:8000 tienda-online:1.0
docker logs tienda      # ver lo que va imprimiendo
docker stop tienda      # pararlo
```

Y si quieres que la API escuche en otro puerto, por ejemplo el 9000:

```bash
docker run --rm -e PORT=9000 -p 9000:9000 tienda-online:1.0
```

### Variables de entorno

| Variable | Valor por defecto | Para qué sirve |
|---|---|---|
| `PORT` | `8000` | Puerto en el que escucha la API |
| `HOST` | `0.0.0.0` en Docker, `127.0.0.1` en local | Desde dónde se aceptan conexiones |

### Cómo comprobar que funciona

Al arrancar el contenedor tiene que salir algo así:

```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Después:

1. Abre http://localhost:8000/docs y tiene que salir la documentación de Swagger con todos los
   endpoints.
2. Abre http://localhost:8000/productos y tiene que devolver `[]` (la tienda empieza vacía).
3. Ejecuta el cliente de prueba, que crea usuarios, productos y pedidos y comprueba los códigos de
   respuesta. Todas las peticiones tienen que salir como `[OK]`:

   ```bash
   python cliente/cliente.py http://localhost:8000
   ```

### Publicar la imagen

La imagen se publica en GitHub Container Registry. Cada push a `main` o `feature/docker` lanza el
workflow `.github/workflows/docker.yml`, que sigue el flujo build → run → test → push: construye la
imagen, la arranca, la prueba con el cliente y, si todo va bien, la sube con las etiquetas `1.0` y
`latest`.

También se puede publicar a mano (el token de GitHub necesita el permiso `write:packages`):

```bash
docker login ghcr.io -u u185622
docker tag tienda-online:1.0 ghcr.io/u185622/tienda-online:1.0
docker tag tienda-online:1.0 ghcr.io/u185622/tienda-online:latest
docker push ghcr.io/u185622/tienda-online:1.0
docker push ghcr.io/u185622/tienda-online:latest
```

### Descargar y usar la imagen publicada

Cualquiera puede usarla sin tener el código:

```bash
docker pull ghcr.io/u185622/tienda-online:1.0
docker run --rm -p 8000:8000 ghcr.io/u185622/tienda-online:1.0
```

## Ramas

En `main` está la versión que funciona. Cada cosa nueva la hago en su propia rama
(`feature/algo`, por ejemplo `feature/docker`) y cuando está terminada la junto con `main` mediante
un Pull Request.
