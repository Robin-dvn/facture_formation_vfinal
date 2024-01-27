import pyodbc
import logging
import textwrap
import azure.functions as func
import json
from datetime import datetime

def connexion(dbName):

    driver = '{ODBC Driver 18 for SQL Server}'
    server_name = "formationserver"
    server=f"{server_name}.database.windows.net,1433"

    Database=dbName
    Uid="formationadmin"
    Pwd='Formationserveroz1!'


    connection_string = textwrap.dedent(f'''
        Driver={driver};
        Server={server};
        Database={Database};
        Uid={Uid};
        Pwd={Pwd};
        Encrypt=yes;
        TrustServerCertificate=no;
        Connection Timeout=30;
        
    ''')
    logging.info(connection_string)

    cnxn : pyodbc.Connection = pyodbc.connect(connection_string)
    

    return cnxn

def insererCommande( cnxn :pyodbc.Connection,numCommande,nom,nomFichier,adressemail,dateCommande,adresse=None,ville=None,pays=None,codePostale=None):
    # Gestion des valeurs par défaut pour les paramètres d'adresse
    adresse = "NULL" if adresse is None else f"'{adresse}'"
    ville = "NULL" if ville is None else f"'{ville}'"
    pays = "NULL" if pays is None else f"'{pays}'"
    codePostale = "NULL" if codePostale is None else f"'{codePostale}'"

    sql_insert_query  = f"INSERT INTO commandes VALUES ({numCommande},'{nom}','{nomFichier}','{adressemail}',{adresse},{ville},{pays},{codePostale},'{dateCommande}')"
    crsr : pyodbc.Cursor = cnxn.cursor()
   
    try:
        crsr.execute(sql_insert_query)
        cnxn.commit()
    except SyntaxError as e:
        
        logging.info("Il y a eu une erreur sur l'insertion")
        raise e

def getNbCommandesMois(cnxn: pyodbc.Connection):
    sql_getquery = '''SELECT * FROM commandes
        WHERE MONTH(date_commande) = MONTH(GETDATE())
        AND YEAR(date_commande) = YEAR(GETDATE());'''
    crsr : pyodbc.Cursor = cnxn.cursor()
    

    crsr.execute(sql_getquery)
    res = list(crsr.fetchall())
    

    return len(res)

def ajouterCommande(nom,adressemail,dateCommande,adresse=None,ville=None,pays=None,codePostale=None):

    cnxn = connexion("profenligneDB")
    [num_commande, nom_fichier] = getNumNomFacture(nom)
    
    

    insererCommande(cnxn,num_commande,nom,nom_fichier,adressemail,dateCommande,adresse,ville,pays,codePostale)

def getNumNomFacture(nom):
    
    nom = nom.replace(" ", "")
    cnxn = connexion("profenligneDB")
    nbFactureMois = getNbCommandesMois(cnxn)
    mois_actuel = datetime.now().month
    an_actuel = datetime.now().year
    num_commande_str = str(an_actuel)+str(mois_actuel)+str(nbFactureMois+1)
    num_commande = int(num_commande_str)
    nom_fichier = "facture-"+num_commande_str+"-"+nom
    return [num_commande,nom_fichier]