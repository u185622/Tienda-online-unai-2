// Frontend de la tienda online: toda la comunicación con el servidor es vía la API REST.

// ============================================================
// 1. Capa de acceso a la API (aquí están TODAS las peticiones HTTP)
// ============================================================

/** URL base de la API, editable desde la cabecera de la página. */
function apiUrl() {
  return document.getElementById("api-url").value.replace(/\/+$/, "");
}

/**
 * Realiza una petición a la API, comprueba el código de estado y devuelve el JSON.
 * Si la respuesta no es 2xx, lanza un Error con el mensaje "detail" que envía FastAPI.
 */
async function peticion(metodo, ruta, cuerpo) {
  const opciones = { method: metodo, headers: {} };
  if (cuerpo !== undefined) {
    opciones.headers["Content-Type"] = "application/json";
    opciones.body = JSON.stringify(cuerpo);
  }

  const respuesta = await fetch(apiUrl() + ruta, opciones);
  const datos = respuesta.status === 204 ? null : await respuesta.json();

  if (!respuesta.ok) {
    throw new Error(`${respuesta.status}: ${formatearDetalle(datos && datos.detail)}`);
  }
  return datos;
}

/** El detalle de un 422 de FastAPI es una lista de errores; el resto, un texto. */
function formatearDetalle(detalle) {
  if (Array.isArray(detalle)) {
    return detalle.map(e => e.msg.replace(/^Value error, /, "")).join("; ");
  }
  return detalle || "Error desconocido";
}

const api = {
  listarProductos: ()         => peticion("GET", "/productos"),                    // GET /productos
  crearProducto:   (datos)    => peticion("POST", "/productos", datos),            // POST /productos
  eliminarProducto:(id)       => peticion("DELETE", `/productos/${id}`),           // DELETE /productos/{id}
  listarUsuarios:  ()         => peticion("GET", "/usuarios"),                     // GET /usuarios
  crearUsuario:    (datos)    => peticion("POST", "/usuarios", datos),             // POST /usuarios
  crearPedido:     (datos)    => peticion("POST", "/pedidos", datos),              // POST /pedidos
  pedidosUsuario:  (id)       => peticion("GET", `/usuarios/${id}/pedidos`),       // GET /usuarios/{id}/pedidos
};

// ============================================================
// 2. Estado y utilidades de interfaz
// ============================================================

let productos = [];
let usuarios = [];

function mostrarMensaje(texto, tipo = "ok") {
  const caja = document.getElementById("mensaje");
  caja.textContent = texto;
  caja.className = tipo;
  clearTimeout(mostrarMensaje.timer);
  mostrarMensaje.timer = setTimeout(() => (caja.className = ""), 4000);
}

function escapar(texto) {
  return String(texto ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

const euros = (n) => `${Number(n).toFixed(2)} €`;

/** Convierte los campos de un formulario en objeto, omitiendo los vacíos. */
function datosFormulario(form) {
  const datos = {};
  for (const [clave, valor] of new FormData(form)) {
    if (valor !== "") datos[clave] = valor;
  }
  return datos;
}

// ============================================================
// 3. Productos
// ============================================================

async function cargarProductos() {
  productos = await api.listarProductos();
  const filas = productos.map(p => {
    let detalles = "";
    if (p.tipo === "electronico") detalles = `Garantía ${p.meses_garantia} meses`;
    if (p.tipo === "ropa") detalles = `Talla ${escapar(p.talla)}, ${escapar(p.color)}`;
    return `<tr>
      <td>${escapar(p.nombre)}</td><td>${p.tipo}</td><td>${euros(p.precio)}</td>
      <td>${p.stock}</td><td>${detalles}</td>
      <td><button class="peligro" data-eliminar="${p.id}">Eliminar</button></td>
    </tr>`;
  });
  document.getElementById("tabla-productos").innerHTML =
    filas.join("") || `<tr><td colspan="6">No hay productos</td></tr>`;
  refrescarSelectoresProducto();
}

function actualizarCamposProducto() {
  const tipo = document.getElementById("producto-tipo").value;
  document.querySelectorAll(".campo-electronico").forEach(e => e.classList.toggle("oculto", tipo !== "electronico"));
  document.querySelectorAll(".campo-ropa").forEach(e => e.classList.toggle("oculto", tipo !== "ropa"));
}

async function enviarProducto(evento) {
  evento.preventDefault();
  const form = evento.target;
  const datos = datosFormulario(form);

  // Solo se envían los atributos propios del tipo elegido.
  if (datos.tipo !== "electronico") delete datos.meses_garantia;
  if (datos.tipo !== "ropa") { delete datos.talla; delete datos.color; }
  datos.precio = Number(datos.precio);
  datos.stock = Number(datos.stock);
  if (datos.meses_garantia !== undefined) datos.meses_garantia = Number(datos.meses_garantia);

  const creado = await api.crearProducto(datos);
  mostrarMensaje(`Producto "${creado.nombre}" creado`);
  form.reset();
  actualizarCamposProducto();
  await cargarProductos();
}

async function eliminarProducto(id) {
  await api.eliminarProducto(id);
  mostrarMensaje("Producto eliminado");
  await cargarProductos();
}

// ============================================================
// 4. Usuarios
// ============================================================

async function cargarUsuarios() {
  usuarios = await api.listarUsuarios();
  const filas = usuarios.map(u => `<tr>
    <td>${escapar(u.nombre)}</td><td>${escapar(u.email)}</td>
    <td>${u.es_admin ? "Administrador" : "Cliente"}</td><td>${escapar(u.direccion)}</td>
  </tr>`);
  document.getElementById("tabla-usuarios").innerHTML =
    filas.join("") || `<tr><td colspan="4">No hay usuarios</td></tr>`;

  const opciones = (lista) => lista.map(u => `<option value="${u.id}">${escapar(u.nombre)} (${escapar(u.email)})</option>`).join("");
  document.getElementById("pedido-cliente").innerHTML = opciones(usuarios.filter(u => !u.es_admin));
  document.getElementById("consulta-usuario").innerHTML = opciones(usuarios);
}

async function enviarUsuario(evento) {
  evento.preventDefault();
  const form = evento.target;
  const datos = datosFormulario(form);
  if (datos.tipo !== "cliente") delete datos.direccion;

  const creado = await api.crearUsuario(datos);
  mostrarMensaje(`Usuario "${creado.nombre}" creado`);
  form.reset();
  actualizarCampoDireccion();
  await cargarUsuarios();
}

function actualizarCampoDireccion() {
  const tipo = document.getElementById("usuario-tipo").value;
  document.getElementById("campo-direccion").classList.toggle("oculto", tipo !== "cliente");
}

// ============================================================
// 5. Pedidos
// ============================================================

function opcionesProducto() {
  return productos.map(p => `<option value="${p.id}">${escapar(p.nombre)} - ${euros(p.precio)} (stock ${p.stock})</option>`).join("");
}

function anadirLineaPedido() {
  const linea = document.createElement("div");
  linea.className = "linea";
  linea.innerHTML = `
    <select class="linea-producto" style="flex:1">${opcionesProducto()}</select>
    <input class="linea-cantidad" type="number" min="1" value="1" style="width:80px">
    <button type="button" class="secundario">✕</button>`;
  linea.querySelector("button").addEventListener("click", () => linea.remove());
  document.getElementById("lineas-pedido").appendChild(linea);
}

function refrescarSelectoresProducto() {
  document.querySelectorAll(".linea-producto").forEach(select => {
    const seleccionado = select.value;
    select.innerHTML = opcionesProducto();
    select.value = seleccionado;
  });
}

async function enviarPedido(evento) {
  evento.preventDefault();
  const items = [...document.querySelectorAll("#lineas-pedido .linea")].map(linea => ({
    producto_id: linea.querySelector(".linea-producto").value,
    cantidad: Number(linea.querySelector(".linea-cantidad").value),
  }));
  const datos = { cliente_id: document.getElementById("pedido-cliente").value, items };

  const pedido = await api.crearPedido(datos);
  mostrarMensaje(`Pedido creado. Total: ${euros(pedido.total)}`);
  document.getElementById("lineas-pedido").innerHTML = "";
  anadirLineaPedido();
  await cargarProductos();  // el stock ha cambiado
}

async function consultarPedidos(evento) {
  evento.preventDefault();
  const id = document.getElementById("consulta-usuario").value;
  const pedidos = await api.pedidosUsuario(id);

  const contenedor = document.getElementById("resultado-pedidos");
  if (pedidos.length === 0) {
    contenedor.innerHTML = "<p>Este usuario no tiene pedidos.</p>";
    return;
  }
  contenedor.innerHTML = pedidos.map(p => `
    <table>
      <thead><tr><th colspan="4">${new Date(p.fecha).toLocaleString()} — Total ${euros(p.total)}</th></tr>
             <tr><th>Producto</th><th>Precio</th><th>Cantidad</th><th>Subtotal</th></tr></thead>
      <tbody>${p.items.map(i => `<tr><td>${escapar(i.nombre)}</td><td>${euros(i.precio_unitario)}</td>
        <td>${i.cantidad}</td><td>${euros(i.subtotal)}</td></tr>`).join("")}</tbody>
    </table>`).join("");
}

// ============================================================
// 6. Arranque y eventos
// ============================================================

/** Envuelve un manejador para mostrar en pantalla cualquier error de la API. */
const conErrores = (fn) => async (...args) => {
  try { await fn(...args); } catch (e) { mostrarMensaje(e.message, "error"); }
};

const cargarTodo = conErrores(async () => {
  await Promise.all([cargarProductos(), cargarUsuarios()]);
  if (!document.querySelector("#lineas-pedido .linea")) anadirLineaPedido();
});

document.getElementById("producto-tipo").addEventListener("change", actualizarCamposProducto);
document.getElementById("usuario-tipo").addEventListener("change", actualizarCampoDireccion);
document.getElementById("form-producto").addEventListener("submit", conErrores(enviarProducto));
document.getElementById("form-usuario").addEventListener("submit", conErrores(enviarUsuario));
document.getElementById("form-pedido").addEventListener("submit", conErrores(enviarPedido));
document.getElementById("form-consulta-pedidos").addEventListener("submit", conErrores(consultarPedidos));
document.getElementById("btn-add-linea").addEventListener("click", anadirLineaPedido);
document.getElementById("btn-recargar").addEventListener("click", cargarTodo);
document.getElementById("tabla-productos").addEventListener("click", conErrores(async (e) => {
  const id = e.target.dataset.eliminar;
  if (id && confirm("¿Eliminar este producto?")) await eliminarProducto(id);
}));

cargarTodo();
