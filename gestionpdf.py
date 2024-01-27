
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
import json
import datetime
from gestionmail import envoieFacture
from gestiondonnees import getNumNomFacture

async def generatePdf(data,email):

    url = "https://api.pdfendpoint.com/v1/convert"

    with open("template_facture.html",'r',encoding="utf-8") as file:
        htmlcontent = file.read()

    with open('style_facture.css', 'r', encoding='utf-8') as file:
        css_content = file.read()

    data_facture = json.dumps(data,ensure_ascii=False)
    
    payload = {
    "html": htmlcontent,
    "css" : css_content,
    "parse_liquid":True,
    "liquid_data": data_facture,
    "sandbox":True
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer pdfe_live_2ef353924d6347579e130888bc7b5f9982ac"
        
    }

    try:
        r_creation = requests.post(url, headers=headers, json=payload)
        # Check if the request was successful
        if r_creation.status_code == 200:
            data_crea = r_creation.json()
            # Process the received data as needed
            dowload_url = data_crea["data"]["url"]
            await downloadPdf(dowload_url,email,data['data']['name'])
            
        else:
            print(f"Request failed with status code: {r_creation.status_code}")
    except requests.RequestException as e:
        print(f"Request failed: {e}")

async def downloadPdf(dowload_url,email,nom):

    r_dowload = requests.get(dowload_url,stream=True)
    content = r_dowload.content
    nom_facture = getNumNomFacture(nom)[1]

    #stockage dans le cloud
    connection_string = 'DefaultEndpointsProtocol=https;AccountName=facture;AccountKey=YMALpipX0Y8H+IEmQg8X/sKKyJQTGXpf1445q+lY2TaZ/KxSV9KwmpxWBV01ZwgAIDYdaGXvLobJ+ASt58SqKA==;EndpointSuffix=core.windows.net'
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    async with blob_service_client:
        container_client = blob_service_client.get_container_client('factures')
                
        # Get a new BlobClient
        blob_client = container_client.get_blob_client(nom_facture)
        await blob_client.upload_blob(content, blob_type="BlockBlob",content_settings=ContentSettings( content_type='application/pdf'))
    envoieFacture(email,nom_facture,content)

        



