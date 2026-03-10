#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import motor_inteligente
import getpass

# Usuario y contraseña de administrador (puedes cambiarlos)
ADMIN_USER = "admin"
ADMIN_PASS = "tu_contraseña_segura"

def login():
    print("=== LOGIN DE ADMINISTRADOR ===")
    usuario = input("Usuario: ").strip()
    clave = getpass.getpass("Contraseña
