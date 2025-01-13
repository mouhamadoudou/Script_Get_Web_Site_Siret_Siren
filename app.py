from analyseSite import analyseSite
import threading
from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

def write_to_file(data):
    # Ecrit dans le fichier urls.txt
    with open("urls.txt", "w") as file:
        for item in data:
            file.write(item + "\n")

def lunchApi(typePro, arg2, request_id):
    try:
        # Effectue l'analyse en fonction du type d'URL
        if typePro == "oneUrl":
            write_to_file([arg2["url"]])
            result = analyseSite()  # Simuler le résultat de l'analyse
        else:
            data = []
            if arg2:
                if hasattr(arg2, 'read'):
                    file_content = arg2.read()
                    file_content = file_content.decode('utf-8')
                    data = file_content.splitlines()
                    write_to_file(data)
                    print("Contenu du fichier texte :", data)
                result = analyseSite()  # Simuler l'analyse pour le fichier

        # Envoi du résultat avec le request_id
        socketio.emit('analyse_done', {'message': 'Analyse terminée', 'data': result, 'request_id': request_id})

    except Exception as e:
        # En cas d'erreur, envoi du message d'erreur avec le request_id
        print(f"Error during analysis: {e}")
        socketio.emit('analyse_done', {'message': 'Erreur lors de l\'analyse', 'data': str(e), 'request_id': request_id})


@app.route('/api/analyse', methods=['POST'])
def analyse():
    data = request.get_json()  # Récupérer les données envoyées en JSON
    request_id = data.get('request_id', None)  # Récupérer le request_id envoyé par le client
    
    if not request_id:
        return jsonify({"message": "request_id est nécessaire"}), 400

    # Démarrer un nouveau thread pour l'analyse, en passant le request_id
    thread = threading.Thread(target=lunchApi, args=("multipleUrl", data, request_id))
    thread.start()  # Démarre le thread d'analyse

    return jsonify({"message": "Analyse en cours, vous serez notifié quand elle sera terminée", "request_id": request_id}), 202


@app.route('/api/analyse/oneUrl', methods=['POST'])
def analyseOneLink():
    data = request.get_json()  # Récupérer les données pour une URL
    request_id = data.get('request_id', None)  # Récupérer le request_id envoyé par le client

    if not request_id:
        return jsonify({"message": "request_id est nécessaire"}), 400

    # Démarrer un nouveau thread pour l'analyse de l'URL, en passant le request_id
    thread = threading.Thread(target=lunchApi, args=("oneUrl", data, request_id))
    thread.start()

    return jsonify({"message": "Analyse en cours, vous serez notifié quand elle sera terminée", "request_id": request_id}), 202


@app.route('/api/analyse/multipleUrl', methods=['POST'])
def analyseMultipleLink():
    file = request.files.get('file')  # Récupérer le fichier envoyé par l'utilisateur
    request_id = request.headers.get('request_id')  # Récupérer le request_id dans l'en-tête
    
    if not request_id:
        return jsonify({"message": "request_id est nécessaire"}), 400

    # Démarrer un nouveau thread pour l'analyse du fichier, en passant le request_id
    thread = threading.Thread(target=lunchApi, args=("multipleUrl", file, request_id))
    thread.start()  # Démarre le thread

    return jsonify({"message": "Analyse en cours, vous serez notifié quand elle sera terminée", "request_id": request_id}), 202


if __name__ == '__main__':
    socketio.run(app, debug=True)
