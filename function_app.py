import azure.functions as func
from azure.storage.blob import ContentSettings
from azure.storage.blob.aio import BlobServiceClient
import logging
from fpdf import FPDF
from jinja2 import Template
import smtplib
from email.message import EmailMessage
import stripe
import requests
import time
import asyncio
import datetime
from gestionpdf import generatePdf, downloadPdf
from gestiondonnees import ajouterCommande, getNumNomFacture
from gestionAPIstripe import getCustomerInfo

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


#clé test 
#stripe.api_key = "sk_test_51O4PhpJSHtxcKMiQvGcmDNu73QiuRryguCiDRmzrcDeDK2tjgDawrppUmVVi4LwiXGYxftWiq03QfkcoB5asWhFC00um57Sh0X"
#clé réelle
stripe.api_key = "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"
#endpoint_secret = 'whsec_5928c08f9f8c02130ec7e69cc3a3bbf2c81002807886112b0e8977ec9b162964' # clé LOCAL d'écoute
#endpoint_secret = "whsec_0DXIEBlf3jY3i6MflJdliaEqgkTzbRTE" #AZURE clé d'écoute sur test. 
endpoint_secret = "whsec_MaaultGkkS8rejDPnHEDDvWAVEP33a4Z" #AZURE clé d'écoute
#C'est une sécurité pour être sur que c'est bien stripe qui m'envoie une demande




    


@app.route(route="http_trigger_factures")
async def http_trigger_factures(req: func.HttpRequest) -> func.HttpResponse:
    # logging.info('Python HTTP trigger function processed a request.')
    # logging.info(str(req.headers))

    #récupération des headers
    headers_dict = dict(req.headers)

    # logging.info('Headers:')
    # for key, value in headers_dict.items():
    #     logging.info(f'{key}: {value}')

    #récupération des données de la requète post (payload)
    event = None
    payload = req.get_body()
    #récupération de la clé de signature stripe
    sig_header = headers_dict.get('stripe-signature')
    

    #Test de l'event stripe
    try:
        #on crée un evenement avec la clé de signature, la clé d'écoute et le contenu du post
        # si un de ces éléments n'est pas bon on stop
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise e

    # on vérifie qu'il y a bien eu un event de type charge.succeeded
    if event['type'] == 'payment_intent.succeeded':
      
      
      
      # Gestion des données d'un payement par carte
      payement = event['data']['object']
      
      customer_id = payement["customer"]

      data_payement = getCustomerInfo(customer_id)

      #génération d'un pdf avec pdf_endpoint
      await generatePdf(data_payement,data_payement["data"]["adresse_mail"])

      #ajout de la commande dans la base de donnée
      date_actuelle = datetime.datetime.now().strftime("%Y-%m-%d")
      ajouterCommande(data_payement["data"]["name"],data_payement["data"]["adresse_mail"],date_actuelle)




      


      
    # ... handle other event types
    else:
      print('Unhandled event type {}'.format(event['type']))

    return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
        

