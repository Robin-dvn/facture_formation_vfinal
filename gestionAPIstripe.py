import stripe
import datetime
from gestiondonnees import getNumNomFacture


def getCustomerInfo(customerID):
    stripe.api_key = "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"
    customer_data = stripe.Customer.retrieve(customerID)

    date_actuelle = datetime.datetime.now().strftime("%Y-%m-%d")
    num_facture = getNumNomFacture(customer_data["name"])[0]

    data = {
        "data":{
            "pays":customer_data["address"]["country"],
            "name": customer_data["name"],
            "codePostale": "",
            "ville": "",
            "adresse": "",
            "date": date_actuelle,
            "num_fact" : num_facture,
            "adresse_mail" : customer_data["email"]
        }
        
    }

    return data

