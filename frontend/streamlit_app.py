"""Frontend de la tienda online con Streamlit.

No importa nada del servidor: toda la comunicación es mediante la API REST (requests).

Ejecución (con la API arrancada, desde la carpeta P2):
    streamlit run frontend/streamlit_app.py
"""

import os

import pandas as pd
import requests
import streamlit as st

# Dirección por defecto de la API. También se puede cambiar desde la barra lateral.
BASE_URL = os.environ.get("API_URL", "http://localhost:8000")


# ============================================================
# 1. Capa de acceso a la API (aquí están TODAS las peticiones HTTP)
# ============================================================

class ApiError(Exception):
    """La API ha respondido con un código de error (4xx / 5xx)."""


def api_url() -> str:
    """URL base de la API elegida en la barra lateral."""
    return st.session_state["api_url"].strip().rstrip("/")


def formatear_detalle(respuesta: requests.Response) -> str:
    """El detalle de un 422 de FastAPI es una lista de errores; el resto, un texto."""
    try:
        detalle = respuesta.json().get("detail")
    except ValueError:
        return respuesta.text or "Error desconocido"
    if isinstance(detalle, list):
        return "; ".join(e["msg"].removeprefix("Value error, ") for e in detalle)
    return detalle or "Error desconocido"


def peticion(metodo: str, ruta: str, datos: dict | None = None):
    """Realiza una petición, comprueba el código de estado y devuelve el JSON recibido."""
    respuesta = requests.request(metodo, f"{api_url()}{ruta}", json=datos, timeout=5)
    if not respuesta.ok:
        raise ApiError(f"{respuesta.status_code}: {formatear_detalle(respuesta)}")
    return None if respuesta.status_code == 204 else respuesta.json()


def listar_productos():       return peticion("GET", "/productos")                  # GET /productos
def crear_producto(datos):    return peticion("POST", "/productos", datos)          # POST /productos
def eliminar_producto(id_):   return peticion("DELETE", f"/productos/{id_}")        # DELETE /productos/{id}
def listar_usuarios():        return peticion("GET", "/usuarios")                   # GET /usuarios
def crear_usuario(datos):     return peticion("POST", "/usuarios", datos)           # POST /usuarios
def crear_pedido(datos):      return peticion("POST", "/pedidos", datos)            # POST /pedidos
def pedidos_usuario(id_):     return peticion("GET", f"/usuarios/{id_}/pedidos")    # GET /usuarios/{id}/pedidos


# ============================================================
# 2. Utilidades de interfaz
# ============================================================

TIPOS_PRODUCTO = {"generico": "Genérico", "electronico": "Electrónico", "ropa": "Ropa"}
TIPOS_USUARIO = {"cliente": "Cliente", "administrador": "Administrador"}


def euros(n: float) -> str:
    return f"{n:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def ejecutar(accion, mensaje) -> None:
    """Lanza una acción contra la API; si va bien recarga la página con un aviso, si no muestra el error."""
    try:
        resultado = accion()
    except ApiError as e:
        st.error(str(e), icon=":material/error:")
        return
    except requests.RequestException:
        st.error(f"No se pudo conectar con la API en {api_url()}", icon=":material/wifi_off:")
        return
    st.session_state["aviso"] = mensaje(resultado) if callable(mensaje) else mensaje
    st.rerun()


def detalles_producto(p: dict) -> str:
    if p["tipo"] == "electronico":
        return f"Garantía {p['meses_garantia']} meses"
    if p["tipo"] == "ropa":
        return f"Talla {p['talla']} · {p['color']}"
    return "—"


def etiqueta_producto(p: dict) -> str:
    return f"{p['nombre']} — {euros(p['precio'])} (stock {p['stock']})"


def etiqueta_usuario(u: dict) -> str:
    return f"{u['nombre']} ({u['email']})"


def etiquetas_unicas(objetos: list, etiqueta) -> dict:
    """Asocia cada id con su etiqueta; si dos se repiten, añade un id corto para distinguirlas."""
    textos = [etiqueta(o) for o in objetos]
    return {o["id"]: t if textos.count(t) == 1 else f"{t} · #{o['id'][:6]}" for o, t in zip(objetos, textos)}


# ============================================================
# 3. Cabecera, conexión y carga de datos
# ============================================================

st.set_page_config(page_title="Tienda Online", page_icon="🛒", layout="wide")
st.session_state.setdefault("api_url", BASE_URL)

with st.sidebar:
    st.header("Conexión")
    st.text_input("URL de la API", key="api_url", help="Usa la IP del equipo servidor para probar en red.")
    st.button("Recargar datos", icon=":material/refresh:", width="stretch")
    estado = st.empty()

try:
    productos = listar_productos()
    usuarios = listar_usuarios()
except (requests.RequestException, ApiError) as e:
    estado.error("Sin conexión", icon=":material/wifi_off:")
    st.title("🛒 Tienda Online")
    st.error(f"No se pudo conectar con la API en **{api_url()}**. ¿Está el servidor arrancado?\n\n`{e}`")
    st.stop()

with st.sidebar:
    estado.success("Conectado", icon=":material/check_circle:")
    st.link_button("Abrir documentación (/docs)", f"{api_url()}/docs", icon=":material/menu_book:", width="stretch")
    st.caption("Todas las operaciones de esta página se hacen mediante peticiones HTTP a la API REST.")

if "aviso" in st.session_state:
    st.toast(st.session_state.pop("aviso"), icon=":material/check_circle:")

clientes = [u for u in usuarios if not u["es_admin"]]
# Los selectores trabajan con ids; estos diccionarios permiten recuperar cada objeto.
producto_por_id = {p["id"]: p for p in productos}
usuario_por_id = {u["id"]: u for u in usuarios}
etiqueta_de_producto = etiquetas_unicas(productos, etiqueta_producto)
etiqueta_de_usuario = etiquetas_unicas(usuarios, etiqueta_usuario)

st.title("🛒 Tienda Online")
st.caption(f"Panel de gestión conectado a {api_url()}")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Productos", len(productos), border=True)
col2.metric("Unidades en stock", sum(p["stock"] for p in productos), border=True)
col3.metric("Valor del inventario", euros(sum(p["precio"] * p["stock"] for p in productos)), border=True)
col4.metric("Usuarios", len(usuarios), f"{len(clientes)} clientes", delta_color="off", border=True)

tab_productos, tab_usuarios, tab_pedido, tab_historial = st.tabs(
    [":material/inventory_2: Productos", ":material/group: Usuarios",
     ":material/add_shopping_cart: Nuevo pedido", ":material/receipt_long: Historial de pedidos"],
    key="pestana",
    on_change="rerun",
)


# ============================================================
# 4. Productos
# ============================================================

with tab_productos:
    if productos:
        tabla = pd.DataFrame([{
            "Nombre": p["nombre"],
            "Tipo": TIPOS_PRODUCTO[p["tipo"]],
            "Precio": p["precio"],
            "Stock": p["stock"],
            "Detalles": detalles_producto(p),
        } for p in productos])
        st.dataframe(tabla, hide_index=True, column_config={
            "Precio": st.column_config.NumberColumn(format="%.2f €"),
            "Stock": st.column_config.ProgressColumn(
                format="%d", min_value=0, max_value=max(max(p["stock"] for p in productos), 1)),
        })
    else:
        st.info("Todavía no hay productos.", icon=":material/info:")

    col_crear, col_eliminar = st.columns([2, 1])

    with col_crear.container(border=True):
        st.subheader("Nuevo producto")
        # El tipo va fuera del formulario para que los campos específicos aparezcan al cambiarlo.
        tipo = st.segmented_control("Tipo", TIPOS_PRODUCTO, format_func=TIPOS_PRODUCTO.get,
                                    default="generico", key="producto_tipo")
        with st.form("form-producto", clear_on_submit=True, border=False):
            nombre = st.text_input("Nombre")
            c1, c2 = st.columns(2)
            precio = c1.number_input("Precio (€)", min_value=0.01, value=10.0, step=0.5, format="%.2f")
            stock = c2.number_input("Stock", min_value=0, value=1, step=1)
            if tipo == "electronico":
                meses = st.number_input("Garantía (meses)", min_value=0, value=24, step=1)
            if tipo == "ropa":
                c3, c4 = st.columns(2)
                talla = c3.text_input("Talla")
                color = c4.text_input("Color")

            if st.form_submit_button("Crear producto", type="primary", icon=":material/add:"):
                # Solo se envían los atributos propios del tipo elegido.
                datos = {"tipo": tipo or "generico", "nombre": nombre, "precio": precio, "stock": int(stock)}
                if tipo == "electronico":
                    datos["meses_garantia"] = int(meses)
                if tipo == "ropa":
                    datos.update(talla=talla, color=color)
                ejecutar(lambda: crear_producto(datos), lambda p: f"Producto «{p['nombre']}» creado")

    with col_eliminar.container(border=True):
        st.subheader("Eliminar producto")
        if productos:
            seleccionado = producto_por_id[st.selectbox(
                "Producto", producto_por_id, format_func=etiqueta_de_producto.get)]
            confirmar = st.checkbox("Confirmo que quiero eliminarlo")
            if st.button("Eliminar", type="primary", icon=":material/delete:", disabled=not confirmar):
                ejecutar(lambda: eliminar_producto(seleccionado["id"]),
                         f"Producto «{seleccionado['nombre']}» eliminado")
        else:
            st.caption("No hay productos que eliminar.")


# ============================================================
# 5. Usuarios
# ============================================================

with tab_usuarios:
    if usuarios:
        st.dataframe(pd.DataFrame([{
            "Nombre": u["nombre"],
            "Email": u["email"],
            "Tipo": "Administrador" if u["es_admin"] else "Cliente",
            "Dirección": u.get("direccion") or "—",
        } for u in usuarios]), hide_index=True)
    else:
        st.info("Todavía no hay usuarios.", icon=":material/info:")

    with st.container(border=True):
        st.subheader("Nuevo usuario")
        tipo_usuario = st.segmented_control("Tipo", TIPOS_USUARIO, format_func=TIPOS_USUARIO.get,
                                            default="cliente", key="usuario_tipo")
        with st.form("form-usuario", clear_on_submit=True, border=False):
            c1, c2 = st.columns(2)
            nombre_usuario = c1.text_input("Nombre")
            email = c2.text_input("Email")
            if tipo_usuario != "administrador":
                direccion = st.text_input("Dirección postal")

            if st.form_submit_button("Crear usuario", type="primary", icon=":material/person_add:"):
                datos = {"tipo": tipo_usuario or "cliente", "nombre": nombre_usuario, "email": email}
                if datos["tipo"] == "cliente":
                    datos["direccion"] = direccion
                ejecutar(lambda: crear_usuario(datos), lambda u: f"Usuario «{u['nombre']}» creado")


# ============================================================
# 6. Nuevo pedido
# ============================================================

with tab_pedido:
    if not clientes or not productos:
        st.info("Para crear un pedido hace falta al menos un cliente y un producto.", icon=":material/info:")
    else:
        with st.container(border=True):
            cliente = usuario_por_id[st.selectbox(
                "Cliente", [u["id"] for u in clientes], format_func=etiqueta_de_usuario.get,
                key="pedido_cliente")]
            # Quita del carrito los productos que ya no existen (p. ej. eliminados).
            if "pedido_productos" in st.session_state:
                st.session_state["pedido_productos"] = [
                    i for i in st.session_state["pedido_productos"] if i in producto_por_id]
            elegidos = st.multiselect("Productos", producto_por_id,
                                      format_func=etiqueta_de_producto.get,
                                      placeholder="Elige uno o varios productos", key="pedido_productos")

            items, total = [], 0.0
            for p in (producto_por_id[i] for i in elegidos):
                c1, c2, c3 = st.columns([3, 1, 1], vertical_alignment="center")
                c1.write(f"**{p['nombre']}** · {euros(p['precio'])} / ud.")
                cantidad = c2.number_input("Cantidad", min_value=1, value=1, step=1,
                                           key=f"cantidad_{p['id']}", label_visibility="collapsed")
                c3.write(euros(p["precio"] * cantidad))
                items.append({"producto_id": p["id"], "cantidad": int(cantidad)})
                total += p["precio"] * cantidad

            st.divider()
            c1, c2 = st.columns([3, 1], vertical_alignment="center")
            c1.metric("Total estimado", euros(total))
            if c2.button("Realizar pedido", type="primary", icon=":material/shopping_cart_checkout:",
                         disabled=not items, width="stretch"):
                datos = {"cliente_id": cliente["id"], "items": items}

                def enviar():
                    pedido = crear_pedido(datos)
                    del st.session_state["pedido_productos"]  # vacía el carrito tras el pedido
                    return pedido

                ejecutar(enviar, lambda p: f"Pedido creado. Total: {euros(p['total'])}")


# ============================================================
# 7. Historial de pedidos de un usuario
# ============================================================

with tab_historial:
    if not usuarios:
        st.info("Todavía no hay usuarios.", icon=":material/info:")
    else:
        usuario = usuario_por_id[st.selectbox(
            "Usuario", usuario_por_id, format_func=etiqueta_de_usuario.get,
            key="historial_usuario")]
        try:
            pedidos = pedidos_usuario(usuario["id"])
        except (ApiError, requests.RequestException) as e:
            st.error(str(e), icon=":material/error:")
            pedidos = []
        else:
            if not pedidos:
                st.info("Este usuario no tiene pedidos.", icon=":material/info:")

        if pedidos:
            st.caption(f"{len(pedidos)} pedido(s) · gasto total {euros(sum(p['total'] for p in pedidos))}")
        for pedido in reversed(pedidos):  # el más reciente primero
            fecha = pd.to_datetime(pedido["fecha"]).strftime("%d/%m/%Y %H:%M")
            with st.expander(f"{fecha} — {euros(pedido['total'])}", icon=":material/receipt:"):
                st.dataframe(pd.DataFrame([{
                    "Producto": i["nombre"],
                    "Precio": i["precio_unitario"],
                    "Cantidad": i["cantidad"],
                    "Subtotal": i["subtotal"],
                } for i in pedido["items"]]), hide_index=True, column_config={
                    "Precio": st.column_config.NumberColumn(format="%.2f €"),
                    "Subtotal": st.column_config.NumberColumn(format="%.2f €"),
                })
                st.caption(f"ID del pedido: {pedido['id']}")
