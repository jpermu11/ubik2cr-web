# 🔧 Solucionar Bloqueo de Gmail

## Problema
Gmail está bloqueando los emails que envía tu aplicación.

## Soluciones

### Solución 1: Verificar Contraseña de Aplicación (MÁS COMÚN)

1. Ve a: https://myaccount.google.com/apppasswords
2. Verifica que la contraseña de aplicación "Ubik2CR" esté activa
3. Si no la ves o está desactivada:
   - Elimínala
   - Crea una nueva (sigue los pasos anteriores)
   - Actualiza el archivo .env con la nueva contraseña

### Solución 2: Verificar Seguridad de la Cuenta

1. Ve a: https://myaccount.google.com/security
2. Revisa "Actividad reciente de seguridad"
3. Si ves alertas sobre "Acceso desde aplicación":
   - Haz clic en "Sí, fui yo" para confirmar
   - Esto le dice a Google que confíe en tu aplicación

### Solución 3: Permitir Acceso de Aplicaciones Menos Seguras (NO RECOMENDADO)

Google ya no permite esto, pero si tu cuenta es antigua:
1. Ve a: https://myaccount.google.com/lesssecureapps
2. Si la opción existe, actívala temporalmente
3. **Nota:** Esto es menos seguro, mejor usar Solución 1

### Solución 4: Usar OAuth2 (MÁS COMPLEJO)

Para producción, es mejor usar OAuth2, pero es más complejo de configurar.

## Recomendación

**Para desarrollo/pruebas:**
- Usa Solución 1 (verificar contraseña de aplicación)
- Si sigue bloqueando, considera usar SendGrid o Mailgun

**Para producción:**
- Usa SendGrid o Mailgun (más confiable)
- O configura OAuth2 con Gmail

