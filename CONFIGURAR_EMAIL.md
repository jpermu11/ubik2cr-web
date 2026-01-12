# 📧 Guía: Configurar Email para Recuperación de Contraseñas

## Opción 1: Gmail (Más Fácil - Gratis)

### Paso 1: Crear App Password en Gmail

1. Ve a tu cuenta de Google: https://myaccount.google.com/
2. Ve a "Seguridad"
3. Activa "Verificación en 2 pasos" (si no la tienes)
4. Busca "Contraseñas de aplicaciones"
5. Selecciona "Correo" y "Otro (nombre personalizado)"
6. Escribe: "Ubik2CR"
7. Haz clic en "Generar"
8. **Copia la contraseña de 16 caracteres** (la necesitarás)

### Paso 2: Configurar en tu aplicación

Edita el archivo `.env` y agrega:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASS=la-contraseña-de-16-caracteres-que-copiaste
SMTP_FROM=Ubik2CR <tu-email@gmail.com>
```

### Paso 3: Probar

Reinicia la aplicación y prueba recuperar una contraseña.

---

## Opción 2: SendGrid (Recomendado para Producción)

### Paso 1: Crear cuenta

1. Ve a: https://sendgrid.com/
2. Crea cuenta gratuita (100 emails/día gratis)
3. Verifica tu email

### Paso 2: Crear API Key

1. En el dashboard, ve a "Settings" → "API Keys"
2. Crea un nuevo API Key
3. **Copia la API key** (solo se muestra una vez)

### Paso 3: Configurar en tu aplicación

En `.env`:

```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASS=tu-api-key-de-sendgrid
SMTP_FROM=Ubik2CR <noreply@ubik2cr.com>
```

---

## Opción 3: Mailgun (Muy bueno, 5,000 emails/mes gratis)

1. Crea cuenta en: https://www.mailgun.com/
2. Verifica tu dominio
3. Obtén credenciales SMTP
4. Configura en `.env`:

```env
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=postmaster@tu-dominio.com
SMTP_PASS=tu-password-de-mailgun
SMTP_FROM=Ubik2CR <noreply@tu-dominio.com>
```

---

## Probar que funciona

Después de configurar, reinicia la aplicación y:

1. Ve a: `localhost:5000/recuperar`
2. Ingresa un email de prueba
3. Revisa tu bandeja de entrada (y spam)

---

## Nota Importante

Para producción, usa SendGrid o Mailgun. Gmail tiene límites y puede bloquear tu cuenta si envías muchos emails.

