from main import app, send_email

with app.app_context():
    try:
        send_email(
            'jpermu@gmail.com',
            'Prueba Ubik2CR - Email Funcionando',
            'Este es un email de prueba. Si recibes esto, el email esta funcionando correctamente.',
            '<h1>Prueba Ubik2CR</h1><p>Este es un email de prueba. Si recibes esto, el email esta funcionando correctamente.</p>'
        )
        print('OK: Email enviado correctamente a jpermu@gmail.com')
        print('Revisa tu bandeja de entrada (y spam)')
    except Exception as e:
        print(f'ERROR: Error al enviar email: {e}')

