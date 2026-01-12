# 📧 Guía: Configurar Mailgun con Hostinger

## Paso 1: Crear cuenta en Mailgun

1. Ve a: https://www.mailgun.com/
2. Haz clic en "Sign Up" (arriba a la derecha)
3. Completa el formulario:
   - Email: tu email (puede ser info@ubik2cr.com)
   - Password: crea una contraseña segura
   - Company: Ubik2CR (o el nombre que quieras)
4. Haz clic en "Get Started"
5. Verifica tu email (revisa tu bandeja de entrada)

## Paso 2: Agregar y verificar tu dominio

1. Una vez dentro de Mailgun, verás el dashboard
2. Ve a "Sending" → "Domains" (en el menú izquierdo)
3. Haz clic en "Add New Domain"
4. Ingresa tu dominio: `ubik2cr.com` (o el que tengas)
5. Selecciona región: "US" o "EU" (elige la más cercana)
6. Haz clic en "Add Domain"

## Paso 3: Obtener los registros DNS

Mailgun te mostrará una tabla con registros DNS que debes agregar.
Necesitarás estos registros (Mailgun te los dará exactos):

- Tipo: TXT
- Nombre: (varía según Mailgun)
- Valor: (un texto largo que Mailgun te da)

- Tipo: CNAME
- Nombre: (algo como email.ubik2cr.com)
- Valor: (algo como mxa.mailgun.org)

**IMPORTANTE:** Copia TODOS los registros que Mailgun te muestre.

## Paso 4: Agregar registros DNS en Hostinger

1. Inicia sesión en Hostinger: https://www.hostinger.com/
2. Ve a "Dominios" → "Administrar"
3. Busca tu dominio y haz clic en "Administrar"
4. Busca "Zona DNS" o "DNS Zone" o "DNS Management"
5. Haz clic en "Agregar registro" o "Add Record"

Para cada registro que Mailgun te dio:

**Para registros TXT:**
- Tipo: TXT
- Nombre: (el que Mailgun te dio, puede ser @ o mailgun)
- Valor: (el texto largo que Mailgun te dio)
- TTL: 3600 (o déjalo por defecto)

**Para registros CNAME:**
- Tipo: CNAME
- Nombre: (el que Mailgun te dio, ejemplo: email)
- Valor: (el que Mailgun te dio, ejemplo: mxa.mailgun.org)
- TTL: 3600

6. Guarda cada registro

## Paso 5: Verificar en Mailgun

1. Vuelve a Mailgun
2. En la página de tu dominio, haz clic en "Verify DNS Settings"
3. Mailgun verificará automáticamente (puede tardar unos minutos)
4. Cuando todos los registros estén verificados, verás checkmarks verdes ✅

## Paso 6: Obtener credenciales SMTP

Una vez verificado:

1. En Mailgun, ve a "Sending" → "Domain Settings"
2. Busca la sección "SMTP credentials"
3. Verás:
   - **SMTP Hostname:** smtp.mailgun.org
   - **Port:** 587 (o 465 para SSL)
   - **Username:** (algo como postmaster@ubik2cr.com)
   - **Password:** (haz clic en "Reset password" para verla)

**Copia estos valores, los necesitarás.**

## Paso 7: Configurar en tu aplicación

Una vez tengas las credenciales, las configuramos en tu `.env`

