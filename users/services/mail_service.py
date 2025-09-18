from django.core.mail import EmailMessage
from django.conf import settings

def send_email_changed_password(assunto: str, nome: str, email_destino: str, mensagem: str):
    corpo_html = f"""
        <h2>Olá {nome},</h2>
        <p>{mensagem}</p>
    """
    email = EmailMessage(
        subject=assunto,
        body=corpo_html,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email_destino]
    )
    email.content_subtype = "html"  # habilita HTML
    email.send()

def send_email_code_confirmation(assunto: str, nome: str, email_destino: str, mensagem: str, code: str):
    corpo_html = f"""
        <h2>Olá {nome},</h2>
        <p>{mensagem}</p>
        <p>Código de verificação: {code}</p>
    """
    email = EmailMessage(
        subject=assunto,
        body=corpo_html,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email_destino]
    )
    email.content_subtype = "html"  # habilita HTML
    email.send()
