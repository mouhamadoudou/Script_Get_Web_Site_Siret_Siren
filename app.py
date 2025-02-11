from analyseSite import analyseSite
import threading
from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import eventlet
eventlet.monkey_patch()

app = Flask(__name__)
# CORS(app)
# socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

# socketio = SocketIO(app, cors_allowed_origins="*")

def write_to_file(data):
    
    with open("urls.txt", "w") as file:
        for item in data:
            file.write(item + "\n")

def formatRes(data):
    result = []
    for propsect in data:
        contacts = propsect.get('enrichment', {}).get('contacts', [])
        
        propsect.get('enrichment', {})
        url = propsect["url"]
        revenue = "CA " + str(propsect.get('enrichment', {})["revenue"]) + "€"
    
        contactListText = "\n".join(
            "NOM: " + contact['lastName'] + ",   PRENOM: " + contact['firstName'] +
            ",   FONCTION: " + contact['jobTitle'] + ",   PERSO: " + contact['phoneNumber'] +
            ",   FIX: " + contact['mobileNumber'] + ",   EMAIL: " + contact['email']
            for contact in contacts
        )
    
        result.append([url, contactListText, revenue])
    return result

def lunchApi(typePro, arg2, request_id):
    try:
        if typePro == 'keyWord':
            analyseSite(request_id, socketio, arg2)
        if typePro == "oneUrl":
            write_to_file([arg2["url"]])
            result, nbSiteFound = analyseSite(request_id, socketio)  
        else:
            data = []
            if arg2:
                if hasattr(arg2, 'read'):
                    file_content = arg2.read()
                    file_content = file_content.decode('utf-8')
                    data = file_content.splitlines()
                    write_to_file(data)
                    print("Contenu du fichier texte --------------------------")
                analyseSite(request_id, socketio)
                # result, nbSiteFound = analyseSite()  
        # socketio.emit('analyse_done', {'message': 'Analyse terminée', 'data': result, 'nb_site_found' : nbSiteFound, 'request_id': request_id})
    except Exception as e:
        
        print(f"Error during analysis: {e}")
        socketio.emit('analyse_done', {'message': 'Erreur lors de l\'analyse', 'data': str(e), 'request_id': request_id})

@app.route('/api/analyse', methods=['POST'])
def analyse():
    data = request.get_json()  
    request_id = data.get('request_id', None)  
    
    if not request_id:
        return jsonify({"message": "request_id est nécessaire"}), 400
    
    thread = threading.Thread(target=lunchApi, args=("multipleUrl", data, request_id))
    thread.start()  

    return jsonify({"message": "Analyse en cours, vous serez notifié quand elle sera terminée", "request_id": request_id}), 202

@app.route('/api/analyse/oneUrl', methods=['POST'])
def analyseOneLink():
    data = request.get_json()  
    request_id = data.get('request_id', None)  

    if not request_id:
        return jsonify({"message": "request_id est nécessaire"}), 400
    thread = threading.Thread(target=lunchApi, args=("oneUrl", data, request_id))
    thread.start()

    return jsonify({"message": "Analyse en cours, vous serez notifié quand elle sera terminée", "request_id": request_id}), 202


@app.route('/api/analyse/multipleUrl', methods=['POST'])
def analyseMultipleLink():
    file = request.files.get('file')  
    request_id = request.form.get('request_id')
    
    if not request_id:
        return jsonify({"message": "request_id est nécessaire"}), 400
    
    thread = threading.Thread(target=lunchApi, args=("multipleUrl", file, request_id))
    thread.start()  

    return jsonify({"message": "Analyse en cours, vous serez notifié quand elle sera terminée", "request_id": request_id}), 202


@app.route('/api/analyse/keywordSearch', methods=['POST'])
def analyseKeywordSearch():
    data = request.get_json()  
    request_id = data.get('request_id', None)  
    keyWord = data.get('keyWord', None)  
    
    print("keywwordd === ", keyWord)
    if not request_id:
        return jsonify({"message": "request_id est nécessaire"}), 400
    
    thread = threading.Thread(target=lunchApi, args=("keyWord", keyWord, request_id))
    thread.start()  
    return jsonify({"message": "Analyse en 0cours, vous serez notifié quand elle sera terminée", "request_id": request_id}), 202

@app.route('/api/analyse/exportDataToGoogleSheet', methods=['POST'])
def exportDataToGoogleSheet():
    data = request.get_json()   
    
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('./keyGoogle.json', scope)

    client = gspread.authorize(creds)
    
    spreadsheet = client.open_by_key("1_XKrLQwydkVXSRRxroSUeSY3YJ-asfjcBd2iuhT0U5c")  # Remplace par ton ID de feuille
    worksheet = spreadsheet.get_worksheet(10)  # Choisir la première feuille
    data[0]['url']

    
    result = formatRes(data)
        
    for row in result:
        worksheet.append_row(row)

    return jsonify({"message": "Le fichier a bien été transféré sur votre document Excel. Veuillez le consulter."}), 202

if __name__ == '__main__':
    # socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
    # socketio.run(app, host="0.0.0.0", port=500, debug=True, allow_unsafe_werkzeug=True)
    # app.run(host='0.0.0.0', port=80)
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
    