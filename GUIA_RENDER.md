# 🚀 Guía Completa: Deploy en Render.com

## Paso 1: Crear Cuenta en Render

1. Ve a: https://render.com/
2. Haz clic en "Get Started for Free"
3. Elige "Sign up with GitHub" (recomendado) o con email
4. Si eliges GitHub, autoriza Render para acceder a tus repositorios
5. Completa el registro

## Paso 2: Crear Base de Datos PostgreSQL

1. En el dashboard de Render, haz clic en "New +"
2. Selecciona "PostgreSQL"
3. Completa:
   - **Name:** `ubik2cr-db` (o el nombre que prefieras)
   - **Database:** `ubik2cr` (o déjalo por defecto)
   - **User:** `ubik2cr_user` (o déjalo por defecto)
   - **Region:** Elige la más cercana (US East, etc.)
   - **PostgreSQL Version:** Deja la más reciente
   - **Plan:** Selecciona "Free" (gratis)
4. Haz clic en "Create Database"
5. Espera 2-3 minutos a que se cree

## Paso 3: Obtener la URL de Conexión

1. Una vez creada la base de datos, haz clic en ella
2. En la sección "Connections", verás "Internal Database URL"
3. **Copia esa URL completa** - se ve así:
   ```
   postgresql://ubik2cr_user:password@dpg-xxxxx-a.oregon-postgres.render.com/ubik2cr
   ```
4. **IMPORTANTE:** Esta URL es la que usarás en tu `.env`

## Paso 4: Crear Web Service (Deploy de la App)

1. En el dashboard, haz clic en "New +"
2. Selecciona "Web Service"
3. Conecta tu repositorio de GitHub:
   - Si no está conectado, haz clic en "Connect account"
   - Selecciona tu repositorio: `jpermu11/ubik2cr-web`
4. Completa la configuración:
   - **Name:** `ubik2cr` (o el que prefieras)
   - **Region:** La misma que elegiste para la BD
   - **Branch:** `main` (o la rama que uses)
   - **Root Directory:** Déjalo vacío (o `.` si está en subcarpeta)
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn main:app`
5. Haz clic en "Advanced"
6. Agrega las variables de entorno (Environment Variables):
   - `DATABASE_URL` = (la URL que copiaste en el Paso 3)
   - `SESSION_SECRET` = (una clave secreta fuerte)
   - `ADMIN_USER` = `info@ubik2cr.com`
   - `ADMIN_PASS` = `UjifamKJ252319@`
   - `SMTP_HOST` = `smtp.gmail.com`
   - `SMTP_PORT` = `587`
   - `SMTP_USER` = `jpermu@gmail.com`
   - `SMTP_PASS` = `gxhr btfm rxfa wvbg`
   - `SMTP_FROM` = `Ubik2CR <jpermu@gmail.com>`
7. Haz clic en "Create Web Service"
8. Espera 5-10 minutos a que se despliegue

## Paso 5: Conectar Dominio (Opcional)

1. En tu Web Service, ve a "Settings"
2. Busca "Custom Domains"
3. Agrega tu dominio: `ubik2cr.com` (o el que tengas)
4. Render te dará instrucciones para configurar DNS en Hostinger
5. Configura los registros DNS en Hostinger según las instrucciones
6. Espera a que se verifique (puede tardar hasta 24 horas, pero usualmente es rápido)

## Paso 6: Migrar Base de Datos

Una vez que todo esté desplegado:
1. Render ejecutará automáticamente las migraciones si configuraste el build command correctamente
2. O puedes conectarte manualmente y ejecutar:
   ```bash
   flask db upgrade
   ```

## Notas Importantes

- El plan gratuito de Render tiene limitaciones (se "duerme" después de 15 min de inactividad)
- Para producción real, considera el plan de pago ($7/mes)
- La base de datos PostgreSQL gratis tiene 90 días de prueba, luego necesitas plan de pago
- Para producción, considera Supabase (más espacio gratis) o plan de pago de Render

