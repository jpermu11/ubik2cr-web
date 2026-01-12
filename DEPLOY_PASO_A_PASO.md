# 🚀 Deploy en Render.com - Paso a Paso

## Paso 1: Crear Web Service en Render

1. En Render, haz clic en "New +" (arriba a la derecha)
2. Selecciona "Web Service"
3. Si no está conectado GitHub:
   - Haz clic en "Connect account" o "Connect GitHub"
   - Autoriza Render para acceder a tus repositorios
4. Selecciona tu repositorio: `jpermu11/ubik2cr-web`
5. Haz clic en "Connect"

## Paso 2: Configurar el Web Service

Completa estos campos:

**Información Básica:**
- **Name:** `ubik2cr` (o el nombre que prefieras)
- **Region:** Oregon (la misma región que tu base de datos)
- **Branch:** `main` (o la rama que uses)
- **Root Directory:** (déjalo vacío - si tu código está en la raíz)

**Build & Deploy:**
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn main:app`

## Paso 3: Configurar Variables de Entorno

Haz clic en "Advanced" y luego en "Add Environment Variable"

Agrega estas variables UNA POR UNA:

1. **DATABASE_URL**
   - Key: `DATABASE_URL`
   - Value: `postgresql://ubik2cr_db_oregon_user:p8XoPKIdBFbDc6PBVEkBoSTpTHG07ikB@dpg-d5cnsna4d50c7388o440-a/ubik2cr_db_oregon`
   - (Usa la Internal Database URL - sin el dominio completo)

2. **SESSION_SECRET**
   - Key: `SESSION_SECRET`
   - Value: (genera una clave fuerte, ejemplo: `sk_live_abc123xyz789_secret_key_2025`)
   - **IMPORTANTE:** Cambia esto por una clave única y segura

3. **ADMIN_USER**
   - Key: `ADMIN_USER`
   - Value: `info@ubik2cr.com`

4. **ADMIN_PASS**
   - Key: `ADMIN_PASS`
   - Value: `UjifamKJ252319@`

5. **SMTP_HOST**
   - Key: `SMTP_HOST`
   - Value: `smtp.gmail.com`

6. **SMTP_PORT**
   - Key: `SMTP_PORT`
   - Value: `587`

7. **SMTP_USER**
   - Key: `SMTP_USER`
   - Value: `jpermu@gmail.com`

8. **SMTP_PASS**
   - Key: `SMTP_PASS`
   - Value: `gxhr btfm rxfa wvbg`

9. **SMTP_FROM**
   - Key: `SMTP_FROM`
   - Value: `Ubik2CR <jpermu@gmail.com>`

10. **PORT** (opcional)
    - Key: `PORT`
    - Value: `10000` (Render usa este puerto automáticamente, pero puedes dejarlo)

## Paso 4: Crear el Web Service

1. Revisa que todas las variables estén agregadas
2. Haz clic en "Create Web Service"
3. Espera 5-10 minutos a que se despliegue
4. Verás el progreso en tiempo real

## Paso 5: Ejecutar Migraciones

Una vez que el deploy termine:

1. En tu Web Service, ve a la pestaña "Shell"
2. Se abrirá una terminal
3. Ejecuta: `flask db upgrade`
4. Esto creará las tablas en PostgreSQL

## Paso 6: Conectar Tu Dominio

1. En tu Web Service, ve a "Settings"
2. Busca la sección "Custom Domains"
3. Haz clic en "Add Custom Domain"
4. Ingresa tu dominio: `ubik2cr.com` (o el que tengas)
5. Haz clic en "Save"
6. Render te mostrará instrucciones de DNS

## Paso 7: Configurar DNS en Hostinger

Render te dará algo como:

**Opción A: CNAME (Recomendado)**
- Tipo: CNAME
- Nombre: `@` o `www`
- Valor: `ubik2cr.onrender.com` (o la URL que Render te dé)

**Opción B: A Record**
- Tipo: A
- Nombre: `@`
- Valor: (una IP que Render te dará)

**Pasos en Hostinger:**
1. Inicia sesión en Hostinger
2. Ve a "Dominios" → "Administrar"
3. Busca tu dominio y haz clic en "Administrar"
4. Ve a "Zona DNS" o "DNS Management"
5. Agrega el registro que Render te indicó
6. Guarda los cambios
7. Espera 5-60 minutos a que se propague

## Paso 8: Verificar que Funciona

1. Visita tu dominio (puede tardar unos minutos)
2. O visita la URL de Render mientras se propaga el DNS
3. Verifica que la aplicación carga
4. Prueba crear una cuenta
5. Prueba iniciar sesión como admin

## ✅ Checklist Final

- [ ] Web Service creado
- [ ] Variables de entorno configuradas
- [ ] Deploy completado
- [ ] Migraciones ejecutadas
- [ ] Dominio agregado en Render
- [ ] DNS configurado en Hostinger
- [ ] Aplicación funcionando en tu dominio

