import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from email.mime.base import MIMEBase
from email import encoders

def envoieFacture(email,nom_facture,pdf_content):

    
    with open("template_mail_facture.html","r",encoding="utf-8") as file:
        html_content = file.read()
    html_part = MIMEText(html_content, 'html')
    
    
    msg = MIMEMultipart()
    msg['From'] = 'communication@prof-en-ligne.com'
    msg['To'] = email
    msg['Subject'] = 'Facture de votre achat à Prof en ligne'

    html_part = MIMEText(html_content,'html')
    msg.attach(html_part)
    

    pdf_part = MIMEBase('application', 'octet-stream')
    pdf_part.set_payload(pdf_content)
    encoders.encode_base64(pdf_part)
    pdf_part.add_header('Content-Disposition', f'attachment; filename={nom_facture}.pdf')
    msg.attach(pdf_part)
    with smtplib.SMTP('smtp.hostinger.com', 587) as smtp_server:
        smtp_server.starttls()
        smtp_server.login('communication@prof-en-ligne.com', 'Profenligneoz1!')
        smtp_server.sendmail('communication@prof-en-ligne.com',email,msg.as_string())