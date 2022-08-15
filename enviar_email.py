import os
import smtplib
from email.message import EmailMessage
from ssl import ALERT_DESCRIPTION_RECORD_OVERFLOW

e_mail = 'contato@videogoat.co'
senha = 'p6rDJhkhjLBQ'
def enviar(alvo, tema, conteudo):
    msg = EmailMessage()
    msg['Subject'] = tema
    msg['From'] = e_mail
    msg['To'] = alvo
    msg.set_content(conteudo)

    with smtplib.SMTP_SSL('smtp.zoho.com', 465) as smtp:
        smtp.login(e_mail, senha)
        smtp.send_message(msg)
        print('e-mail enviado para {}'.format(alvo))