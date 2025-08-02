#!/usr/bin/env python3
"""
Script de prueba para testear la autenticación de la API
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración
BASE_URL = "http://localhost:8000"

def test_register():
    """Probar registro de usuario"""
    print("=== TESTING REGISTER ===")
    
    email = input("Ingresa email para registro: ")
    password = input("Ingresa contraseña: ")
    
    data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_login():
    """Probar login de usuario"""
    print("\n=== TESTING LOGIN ===")
    
    email = input("Ingresa email: ")
    password = input("Ingresa contraseña: ")
    
    data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            return token
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_protected_route(token):
    """Probar ruta protegida"""
    print("\n=== TESTING PROTECTED ROUTE ===")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/user/profile", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_invalid_token():
    """Probar con token inválido"""
    print("\n=== TESTING INVALID TOKEN ===")
    
    headers = {
        "Authorization": "Bearer invalid_token_here"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/user/profile", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 401
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🧪 TESTING AUTHENTICATION API")
    print("=" * 50)
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print("❌ Error: El servidor no está corriendo en http://localhost:8000")
            print("Ejecuta: uvicorn main:app --reload")
            return
        print("✅ Servidor corriendo correctamente")
    except:
        print("❌ Error: No se puede conectar al servidor")
        print("Asegúrate de que esté corriendo en http://localhost:8000")
        return
    
    # Menú de opciones
    while True:
        print("\n" + "=" * 50)
        print("OPCIONES DE PRUEBA:")
        print("1. Registrar usuario")
        print("2. Login usuario")
        print("3. Probar ruta protegida")
        print("4. Probar token inválido")
        print("5. Ejecutar todas las pruebas")
        print("6. Salir")
        
        choice = input("\nSelecciona una opción (1-6): ")
        
        if choice == "1":
            test_register()
        elif choice == "2":
            token = test_login()
            if token:
                print(f"✅ Token obtenido: {token[:50]}...")
        elif choice == "3":
            token = input("Ingresa el token JWT: ")
            test_protected_route(token)
        elif choice == "4":
            test_invalid_token()
        elif choice == "5":
            print("\n🚀 EJECUTANDO TODAS LAS PRUEBAS")
            print("=" * 50)
            
            # Registrar
            if test_register():
                print("✅ Registro exitoso")
            else:
                print("❌ Registro falló")
            
            # Login
            token = test_login()
            if token:
                print("✅ Login exitoso")
                
                # Probar ruta protegida
                if test_protected_route(token):
                    print("✅ Ruta protegida accesible")
                else:
                    print("❌ Ruta protegida falló")
                
                # Probar token inválido
                if test_invalid_token():
                    print("✅ Token inválido rechazado correctamente")
                else:
                    print("❌ Token inválido no fue rechazado")
            else:
                print("❌ Login falló")
        elif choice == "6":
            print("👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción inválida")

if __name__ == "__main__":
    main() 