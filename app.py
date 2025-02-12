import eventlet
eventlet.monkey_patch()

from analyseSite import analyseSite
from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Patch eventlet pour assurer la gestion asynchrone des sockets
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

# Fonction de traitement des données et de gestion du fichier
def write_to_file(data):
    with open("urls.txt", "w") as file:
        for item in data:
            file.write(item + "\n")

def formatRes(data):
    result = []
    for prospect in data:
        contacts = prospect.get('enrichment', {}).get('contacts', [])
        url = prospect["url"]
        revenue = "CA " + str(prospect.get('enrichment', {}).get("revenue", "Non précisé")) + "€"
        
        contactListText = "\n".join(
            "NOM: " + contact['lastName'] + ",   PRENOM: " + contact['firstName'] +
            ",   FONCTION: " + contact['jobTitle'] + ",   PERSO: " + contact['phoneNumber'] +
            ",   FIX: " + contact['mobileNumber'] + ",   EMAIL: " + contact['email']
            for contact in contacts
        )
    
        result.append([url, contactListText, revenue])
    return result

# Fonction principale de lancement de l'API
def lunchApi(typePro, arg2, request_id):
    try:
        with app.app_context():  # Ensure the app context is available
            if typePro == 'keyWord':
                analyseSite(request_id, socketio, arg2)
            if typePro == "oneUrl":
                write_to_file([arg2["url"]])
                analyseSite(request_id, socketio)  
            else:
                data = []
                if arg2:
                    if hasattr(arg2, 'read'):
                        file_content = arg2.read()
                        file_content = file_content.decode('utf-8')
                        data = file_content.splitlines()
                        write_to_file(data)
                    analyseSite(request_id, socketio)
    except Exception as e:
        print(f"Error during analysis: {e}")
        socketio.emit('analyse_done', {'message': 'Erreur lors de l\'analyse', 'data': str(e), 'request_id': request_id})

@app.route('/api/analyse', methods=['POST'])
def analyse():
    data = request.get_json()  
    request_id = data.get('request_id', None)  
    
    if not request_id:
        return jsonify({"message": "request_id est nécessaire"}), 400
    
    # Utilisation de eventlet.spawn pour gérer l'appel asynchrone
    eventlet.spawn(lunchApi, "multipleUrl", data, request_id)

    return jsonify({"message": "Analyse en cours, vous serez notifié quand elle sera terminée", "request_id": request_id}), 202

@app.route('/api/analyse/oneUrl', methods=['POST'])
def analyseOneLink():
    data = request.get_json()  
    request_id = data.get('request_id', None)  

    if not request_id:
        return jsonify({"message": "request_id est nécessaire"}), 400

    eventlet.spawn(lunchApi, "oneUrl", data, request_id)

    return jsonify({"message": "Analyse en cours, vous serez notifié quand elle sera terminée", "request_id": request_id}), 202

@app.route('/api/analyse/multipleUrl', methods=['POST'])
def analyseMultipleLink():
    file = request.files.get('file')  
    request_id = request.form.get('request_id')
    
    if not request_id:
        return jsonify({"message": "request_id est nécessaire"}), 400
    
    eventlet.spawn(lunchApi, "multipleUrl", file, request_id)

    return jsonify({"message": "Analyse en cours, vous serez notifié quand elle sera terminée", "request_id": request_id}), 202

@app.route('/api/analyse/keywordSearch', methods=['POST'])
def analyseKeywordSearch():
    data = request.get_json()  
    request_id = data.get('request_id', None)  
    keyWord = data.get('keyWord', None)  
    
    if not request_id:
        return jsonify({"message": "request_id est nécessaire"}), 400
    
    eventlet.spawn(lunchApi, "keyWord", keyWord, request_id)

    return jsonify({"message": "Analyse en cours, vous serez notifié quand elle sera terminée", "request_id": request_id}), 202

@app.route('/api/analyse/exportDataToGoogleSheet', methods=['POST'])
def exportDataToGoogleSheet():
    data = request.get_json()   
    
    # Ensure you are running under app context
    with app.app_context():
        scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('./keyGoogle.json', scope)

        client = gspread.authorize(creds)
        
        spreadsheet = client.open_by_key("1_XKrLQwydkVXSRRxroSUeSY3YJ-asfjcBd2iuhT0U5c")  
        worksheet = spreadsheet.get_worksheet(10)  
        data[0]['url']
        
        result = formatRes(data)
            
        for row in result:
            worksheet.append_row(row)

    return jsonify({"message": "Le fichier a bien été transféré sur votre document Excel. Veuillez le consulter."}), 202

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=80, ssl_context='adhoc')
