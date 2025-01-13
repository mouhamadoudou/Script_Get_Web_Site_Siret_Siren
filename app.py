from analyseSite import analyseSite
import threading
from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

def write_to_file(data):
    
    with open("urls.txt", "w") as file:
        for item in data:
            file.write(item + "\n")

def lunchApi(typePro, arg2, request_id):
    try:
        
        if typePro == "oneUrl":
            write_to_file([arg2["url"]])
            result, nbSiteFound = analyseSite()  
        else:
            data = []
            if arg2:
                if hasattr(arg2, 'read'):
                    file_content = arg2.read()
                    file_content = file_content.decode('utf-8')
                    data = file_content.splitlines()
                    write_to_file(data)
                    # print("Contenu du fichier texte :", data)
                result, nbSiteFound = analyseSite()  
        
        socketio.emit('analyse_done', {'message': 'Analyse terminée', 'data': result, 'nb_site_found' : nbSiteFound, 'request_id': request_id})

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

if __name__ == '__main__':
    socketio.run(app, debug=True)
