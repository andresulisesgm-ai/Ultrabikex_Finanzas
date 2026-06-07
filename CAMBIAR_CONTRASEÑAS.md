# Cómo cambiar las contraseñas de usuario

## Credenciales por defecto

- **Admin**: usuario `admin` / contraseña `admin2026`
- **Viewer**: usuario `viewer` / contraseña `viewer2026`

## ⚡ Método Rápido (Recomendado)

### Windows:
1. **Doble clic** en el archivo `cambiar_clave.bat`
2. Sigue las instrucciones en pantalla
3. Reinicia la aplicación ULTRAX

### Linux/Mac:
```bash
python cambiar_clave.py
```

El script te pedirá:
- Nueva contraseña para **admin**
- Confirmación de la contraseña
- Nueva contraseña para **viewer**
- Confirmación de la contraseña
- Confirmación final (escribe "SI" para aplicar)

✅ ¡Listo! Las contraseñas se actualizarán automáticamente.

---

## 🔧 Método Manual (Avanzado)

Solo si prefieres editar el código directamente:

1. Abre el archivo `auth.py`
2. Genera el hash SHA-256 de tu nueva contraseña usando Python:

```python
import hashlib
nueva_contraseña = "tu_contraseña_aqui"
hash_generado = hashlib.sha256(nueva_contraseña.encode()).hexdigest()
print(hash_generado)
```

3. Reemplaza el hash en el diccionario `USERS` del archivo `auth.py`:

```python
USERS = {
    'admin': {
        'password_hash': 'AQUI_VA_EL_NUEVO_HASH',
        'role': 'admin'
    },
    'viewer': {
        'password_hash': 'AQUI_VA_EL_NUEVO_HASH',
        'role': 'viewer'
    }
}
```

4. Guarda el archivo y reinicia la aplicación.

## Diferencias entre roles

### Admin (Administrador)
- **Permisos completos**: Puede hacer TODO
- Cargar archivos de Odoo (ERR y ESF)
- Modificar mappings de cuentas
- Configurar tasas de cambio
- Gestionar presupuestos
- Importar/exportar datos
- Hacer backup y restore
- Apagar el servidor

### Viewer (Visor)
- **Solo lectura**: Puede VER TODO pero NO modificar nada
- Ver dashboards y reportes
- Consultar datos financieros
- Ver comparativas
- Ver estados de resultados
- Ver estados de situación financiera
- Descargar reportes (Excel, PDF)

**Importante**: Los usuarios viewer recibirán mensajes de "Acceso denegado" si intentan realizar operaciones de escritura.
