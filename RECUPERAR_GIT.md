# 🔄 Recuperar Conexión Git - Guía Rápida

## ✅ Tu Trabajo Está Guardado

Los archivos están bien guardados en:
`C:\Users\jperm\.cursor\flask-app`

## 🔧 Pasos para Reconectar con GitHub

### Opción 1: Reconectar Este Directorio (RECOMENDADO)

1. **Abre PowerShell o CMD en este directorio**

2. **Inicializa Git:**
   ```bash
   git init
   ```

3. **Conecta al repositorio de GitHub:**
   ```bash
   git remote add origin https://github.com/jpermu11/ubik2cr-web.git
   ```

4. **Agrega todos los archivos:**
   ```bash
   git add .
   ```

5. **Haz commit:**
   ```bash
   git commit -m "Recuperar trabajo después de cierre de Cursor"
   ```

6. **Conecta a la rama main:**
   ```bash
   git branch -M main
   ```

7. **Haz push (puede requerir autenticación):**
   ```bash
   git push -u origin main
   ```

### Opción 2: Usar GitHub Desktop (MÁS FÁCIL)

1. Abre GitHub Desktop
2. File → Add Local Repository
3. Selecciona: `C:\Users\jperm\.cursor\flask-app`
4. Si no detecta el repo, haz clic en "Create Repository"
5. Haz commit de los cambios
6. Haz push

## 🛡️ Prevenir Esto en el Futuro

### 1. Habilitar Auto-Save en Cursor
- File → Preferences → Settings
- Busca "Auto Save"
- Activa "afterDelay" (guarda cada X segundos)

### 2. Hacer Commits Frecuentes
```bash
# Cada vez que hagas cambios importantes:
git add .
git commit -m "Descripción del cambio"
git push
```

### 3. Usar GitHub Desktop para Simplicidad
- Más fácil que comandos
- Visual de cambios
- Auto-push con un clic

### 4. Activar Notificaciones de Cambios No Guardados
- Cursor te avisará si hay cambios sin guardar
- No cierres sin guardar explícitamente

## ✅ Verificar que Funciona

Después de reconectar:

1. Haz un cambio pequeño en `main.py`
2. Guarda el archivo (Ctrl+S)
3. Haz commit y push
4. Ve a Render.com → Logs
5. Deberías ver que Render detecta el cambio automáticamente

## 📝 Nota Importante

**Los archivos NUNCA se pierden si están en Git + GitHub:**
- Local: tus archivos en la computadora
- GitHub: copia en la nube (backup automático)
- Render: despliegue automático desde GitHub

¡Múltiples copias = más seguridad!
