"""Modelos de usuario para la tienda online."""

import uuid


class Usuario:
    """Persona que interactúa con la tienda."""

    def __init__(self, nombre: str, email: str) -> None:
        """Crea un usuario asignándole un identificador único automático."""
        self.id: str = str(uuid.uuid4())
        self.nombre: str = nombre
        self.email: str = email

    def is_admin(self) -> bool:
        """Indica si el usuario tiene privilegios de administrador."""
        return False

    def __str__(self) -> str:
        """Devuelve las características principales del usuario."""
        return f"[{self.id}] {self.nombre} ({self.email})"


class Cliente(Usuario):
    """Usuario que puede realizar pedidos en la tienda."""

    def __init__(self, nombre: str, email: str, direccion: str) -> None:
        """Crea un cliente añadiendo su dirección postal."""
        super().__init__(nombre, email)
        self.direccion: str = direccion

    def __str__(self) -> str:
        """Devuelve las características del cliente incluyendo la dirección."""
        return f"{super().__str__()} - Dirección: {self.direccion}"


class Administrador(Usuario):
    """Usuario gestor de la tienda."""

    def is_admin(self) -> bool:
        """Los administradores siempre tienen privilegios de administrador."""
        return True
