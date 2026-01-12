# 📸 Configurar Cloudinary para Imágenes (Gratis)

## ¿Por qué Cloudinary?

En Render, el sistema de archivos es efímero (las imágenes se pierden al reiniciar). Cloudinary permite almacenar imágenes permanentemente y es **gratis** hasta 25 GB.

---

## PASO 1: Crear cuenta en Cloudinary

1. Ve a: https://cloudinary.com
2. Haz clic en "Sign Up for Free"
3. Completa el formulario:
   - Email
   - Nombre
   - Contraseña
4. Confirma tu email
5. ¡Listo! Ya tienes cuenta gratis

---

## PASO 2: Obtener credenciales

1. Una vez dentro de Cloudinary, verás un "Dashboard"
2. Busca "Account Details" o "Settings"
3. Verás información como:
   - **Cloud name**: (ejemplo: `dabc123`)
   - **API Key**: (ejemplo: `123456789012345`)
   - **API Secret**: (ejemplo: `abcdefghijklmnop`)

**⚠️ IMPORTANTE:** Guarda estas 3 cosas, las necesitarás.

---

## PASO 3: Agregar variables en Render

1. Ve a Render.com
2. Entra a tu servicio `ubik2cr-web`
3. Ve a "Settings" → "Environment Variables"
4. Agrega estas 3 variables:

   - **CLOUDINARY_CLOUD_NAME**
     - Value: (tu Cloud name de Cloudinary)

   - **CLOUDINARY_API_KEY**
     - Value: (tu API Key de Cloudinary)

   - **CLOUDINARY_API_SECRET**
     - Value: (tu API Secret de Cloudinary)

5. Guarda los cambios

---

## PASO 4: Instalar Cloudinary en la app

Ya lo haré yo en el código. Solo necesitas las credenciales de arriba.

---

## ✅ Cuando esté configurado

- Las imágenes se subirán automáticamente a Cloudinary
- Se guardarán permanentemente
- No se perderán aunque Render se reinicie
- Funcionarán perfectamente en producción

---

## 🎯 Siguiente paso

1. Crea tu cuenta en Cloudinary
2. Obtén las 3 credenciales
3. Agrégalas en Render como variables de entorno
4. Dime "listo" y actualizo el código para usar Cloudinary

