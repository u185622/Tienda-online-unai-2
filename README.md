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
