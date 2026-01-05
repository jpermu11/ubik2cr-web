# 🚀 Desplegar en Render - Guía Súper Simple

## ✅ PASO 1: Crear cuenta en Render (si no la tienes)

1. Abre tu navegador
2. Ve a: **https://render.com**
3. Haz clic en **"Get Started for Free"** (arriba a la derecha)
4. Elige **"Sign up with GitHub"** (más fácil)
5. Autoriza Render para acceder a tu GitHub
6. ¡Listo! Ya estás dentro de Render

---

## ✅ PASO 2: Crear la Base de Datos PostgreSQL

1. En Render, haz clic en **"New +"** (arriba a la derecha)
2. Selecciona **"PostgreSQL"**
3. Completa:
   - **Name**: `ubik2cr-db-oregon`
   - **Database**: `ubik2cr_db_oregon`
   - **User**: `ubik2cr_db_oregon_user`
   - **Region**: **Oregon** (más cerca de Costa Rica)
   - **Plan**: **Free** (para empezar)
4. Haz clic en **"Create Database"**
5. **ESPERA** 2-3 minutos a que se cree
6. Cuando esté listo, haz clic en la base de datos
7. Ve a la pestaña **"Connections"**
8. Copia la **"Internal Database URL"** (la que dice `postgresql://...`)
   - **GUARDA ESTA URL**, la necesitarás después

---

## ✅ PASO 3: Crear el Web Service (tu aplicación)

1. En Render, haz clic en **"New +"** otra vez
2. Selecciona **"Web Service"**
3. Conecta tu repositorio:
   - Si no aparece tu repositorio, haz clic en **"Configure account"** y autoriza
   - Busca: **`jpermu11/ubik2cr-web`**
   - Haz clic en **"Connect"**
4. Completa la información:
   - **Name**: `ubik2cr-web`
   - **Region**: **Oregon**
   - **Branch**: `main`
   - **Root Directory**: (déjalo vacío)
   - **Runtime**: `Python 3`
   - **Build Command**: 
     ```
     pip install -r requirements.txt && flask db upgrade
     ```
   - **Start Command**: 
     ```
     gunicorn main:app
     ```
   - **Plan**: **Free** (para empezar)

---

## ✅ PASO 4: Configurar Variables de Entorno

En la misma página del Web Service, baja hasta **"Environment Variables"** y agrega estas variables:

### Variables que debes agregar:

1. **DATABASE_URL**
   - Value: Pega la URL de la base de datos que copiaste antes (la Internal Database URL)

2. **SESSION_SECRET**
   - Value: `tu-secret-key-super-segura-123456789` (puedes inventar cualquier texto largo)

3. **ADMIN_USER**
   - Value: `info@ubik2cr.com`

4. **ADMIN_PASS**
   - Value: `UjifamKJ252319@`

5. **SMTP_HOST**
   - Value: `smtp.gmail.com`

6. **SMTP_PORT**
   - Value: `587`

7. **SMTP_USER**
   - Value: `jpermu@gmail.com`

8. **SMTP_PASS**
   - Value: `gxhr btfm rxfa wvbg`

9. **SMTP_FROM**
   - Value: `Ubik2CR <jpermu@gmail.com>`

---

## ✅ PASO 5: Crear el Servicio

1. Haz clic en **"Create Web Service"** (abajo)
2. **ESPERA** 5-10 minutos mientras Render:
   - Instala las dependencias
   - Crea la base de datos
   - Inicia tu aplicación
3. Verás un log en tiempo real de lo que está pasando
4. Cuando termine, verás: **"Your service is live"** 🎉

---

## ✅ PASO 6: Ver tu aplicación

1. Render te dará una URL como: `https://ubik2cr-web.onrender.com`
2. Haz clic en esa URL
3. ¡Tu aplicación debería estar funcionando! 🚀

---

## ⚠️ IMPORTANTE:

- La versión **Free** de Render "duerme" después de 15 minutos sin uso
- La primera vez que la abres después de dormir, puede tardar 30-60 segundos en despertar
- Si quieres que esté siempre activa, necesitas el plan **Starter** ($7/mes)

---

## 🆘 Si algo falla:

1. Ve a la pestaña **"Logs"** en Render
2. Revisa los errores
3. Los errores más comunes:
   - Variables de entorno mal escritas
   - DATABASE_URL incorrecta
   - Falta alguna dependencia en requirements.txt

---

## ✅ ¡Listo!

Tu aplicación estará en línea y accesible desde cualquier lugar del mundo.

