# 🌐 Conectar tu Dominio a Render - Guía Paso a Paso

## ✅ PASO 1: Configurar el dominio en Render

1. Ve a Render.com e inicia sesión
2. Entra a tu servicio `ubik2cr-web`
3. Ve a la pestaña **"Settings"** (⚙️ Settings)
4. Baja hasta la sección **"Custom Domains"**
5. Haz clic en **"Add Custom Domain"**
6. Escribe tu dominio (ejemplo: `ubik2cr.com` o `www.ubik2cr.com`)
7. Haz clic en **"Add"**
8. Render te dará instrucciones de DNS que necesitas configurar

---

## ✅ PASO 2: Obtener los registros DNS de Render

Después de agregar el dominio, Render te mostrará algo como:

**Para el dominio principal (ejemplo: ubik2cr.com):**
- **Tipo:** `CNAME`
- **Nombre:** `@` o `ubik2cr.com`
- **Valor:** `ubik2cr-web.onrender.com` (o algo similar)

**Para www (ejemplo: www.ubik2cr.com):**
- **Tipo:** `CNAME`
- **Nombre:** `www`
- **Valor:** `ubik2cr-web.onrender.com`

**O si Render te da un registro A:**
- **Tipo:** `A`
- **Nombre:** `@` o `ubik2cr.com`
- **Valor:** Una dirección IP (ejemplo: `76.76.21.21`)

---

## ✅ PASO 3: Configurar DNS en Hostinger

1. Inicia sesión en tu cuenta de Hostinger
2. Ve a **"Dominios"** o **"DNS"**
3. Busca tu dominio y haz clic en **"Administrar"**
4. Ve a la sección **"Zona DNS"** o **"DNS Zone"**
5. Agrega los registros que Render te dio:

### Si Render te dio CNAME:
- **Tipo:** CNAME
- **Nombre:** `@` (o deja vacío, o `ubik2cr.com`)
- **Valor:** `ubik2cr-web.onrender.com`
- **TTL:** 3600 (o el que Render recomiende)

- **Tipo:** CNAME
- **Nombre:** `www`
- **Valor:** `ubik2cr-web.onrender.com`
- **TTL:** 3600

### Si Render te dio registro A:
- **Tipo:** A
- **Nombre:** `@` (o deja vacío)
- **Valor:** (La IP que Render te dio)
- **TTL:** 3600

6. Guarda los cambios

---

## ✅ PASO 4: Esperar la propagación DNS

1. Los cambios DNS pueden tardar **15 minutos a 48 horas** en propagarse
2. Normalmente toma **1-2 horas**
3. Render verificará automáticamente cuando esté listo
4. Verás un checkmark verde cuando el dominio esté conectado

---

## ✅ PASO 5: Verificar que funciona

1. Espera a que Render muestre el checkmark verde
2. Abre tu navegador
3. Ve a tu dominio (ejemplo: `https://ubik2cr.com`)
4. Deberías ver tu aplicación funcionando

---

## ⚠️ IMPORTANTE: SSL/HTTPS

- Render configura automáticamente el certificado SSL (HTTPS)
- No necesitas hacer nada adicional
- El certificado se activa automáticamente cuando el DNS está configurado

---

## 🆘 Si algo no funciona

1. Verifica que los registros DNS estén correctos en Hostinger
2. Espera más tiempo (puede tardar hasta 48 horas)
3. Verifica en Render que el dominio esté "Verified" (con checkmark verde)
4. Usa herramientas como `whatsmydns.net` para verificar la propagación DNS

---

## 📝 Notas

- Si tienes problemas, Render mostrará mensajes de error específicos
- Puedes tener tanto `ubik2cr.com` como `www.ubik2cr.com` funcionando
- Render redirige automáticamente HTTP a HTTPS

