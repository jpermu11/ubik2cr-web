# 🚀 Guía: Deploy en Render.com

## Configuración Actual

✅ Base de datos PostgreSQL creada en Render: `ubik2cr-db-oregon`
✅ Internal Database URL lista para usar en producción

## Paso 1: Crear Web Service en Render

1. En Render, haz clic en "New +"
2. Selecciona "Web Service"
3. Conecta tu repositorio de GitHub: `jpermu11/ubik2cr-web`
4. Completa la configuración:

**Configuración Básica:**
- **Name:** `ubik2cr` (o el que prefieras)
- **Region:** Oregon (la misma que tu BD)
- **Branch:** `main`
- **Root Directory:** (déjalo vacío)
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn main:app`

**Variables de Entorno (Environment Variables):**
Agrega estas variables en "Advanced" → "Environment Variables":

```
DATABASE_URL=postgresql://ubik2cr_db_oregon_user:p8XoPKIdBFbDc6PBVEkBoSTpTHG07ikB@dpg-d5cnsna4d50c7388o440-a/ubik2cr_db_oregon
SESSION_SECRET=clave-super-segura-aleatoria-cambiar-aqui
ADMIN_USER=info@ubik2cr.com
ADMIN_PASS=UjifamKJ252319@
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=jpermu@gmail.com
SMTP_PASS=gxhr btfm rxfa wvbg
SMTP_FROM=Ubik2CR <jpermu@gmail.com>
```

**IMPORTANTE:** 
- Usa la **Internal Database URL** (sin el dominio completo, solo el hostname corto)
- Cambia `SESSION_SECRET` por una clave fuerte y única

5. Haz clic en "Create Web Service"
6. Espera 5-10 minutos a que se despliegue

## Paso 2: Ejecutar Migraciones

Una vez desplegado, las migraciones se ejecutarán automáticamente si configuraste el build command correctamente.

O puedes ejecutarlas manualmente desde el shell de Render:
1. En tu Web Service, ve a "Shell"
2. Ejecuta: `flask db upgrade`

## Paso 3: Conectar Tu Dominio

1. En tu Web Service, ve a "Settings"
2. Busca "Custom Domains"
3. Agrega tu dominio: `ubik2cr.com` (o el que tengas)
4. Render te dará instrucciones para configurar DNS en Hostinger
5. Configura los registros DNS según las instrucciones
6. Espera a que se verifique (puede tardar hasta 24 horas, pero usualmente es rápido)

## Paso 4: Verificar que Todo Funciona

1. Visita tu dominio o la URL de Render (algo como `ubik2cr.onrender.com`)
2. Verifica que la aplicación carga
3. Prueba crear una cuenta
4. Prueba iniciar sesión como admin

## Notas Importantes

- El plan gratuito de Render "duerme" después de 15 min de inactividad
- Para producción real, considera el plan de pago ($7/mes)
- La base de datos PostgreSQL gratis tiene 90 días, luego necesitas plan de pago
- Para producción, considera Supabase (más espacio gratis) o plan de pago de Render

## Checklist de Deployment

- [ ] Web Service creado en Render
- [ ] Variables de entorno configuradas
- [ ] Migraciones ejecutadas
- [ ] Dominio conectado (opcional)
- [ ] Aplicación funcionando
- [ ] Probar todas las funcionalidades

