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

En este repositorio voy a ir subiendo el proyecto y trabajando con Git, ramas y Pull Requests, y
más adelante lo meteré en un contenedor de Docker.

## Cómo está organizado

```
├── src/                    La API (lo que se ejecuta en el servidor)
│   ├── main.py             Aplicación FastAPI con todos los endpoints
│   ├── schemas.py          Esquemas de Pydantic para validar lo que entra y sale
│   ├── models/             Producto, Usuario y Pedido
│   └── services/           TiendaService (la lógica de la tienda) y las excepciones
├── cliente/cliente.py      Un cliente en Python que prueba la API con requests
├── frontend/               Una web para usar la tienda (Streamlit, o HTML + JavaScript)
└── requirements.txt        Las librerías que hacen falta
```

## Cómo ejecutarlo en local

Primero instala las librerías:

```bash
python -m pip install -r requirements.txt
```

Luego arranca la API desde la carpeta `src`:

```bash
cd src
uvicorn main:app --reload
```

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

## Ramas

En `main` está la versión que funciona. Cada cosa nueva la hago en su propia rama
(`feature/algo`, por ejemplo `feature/docker`) y cuando está terminada la junto con `main` mediante
un Pull Request.
