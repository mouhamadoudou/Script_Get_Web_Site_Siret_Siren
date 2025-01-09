from analyseSite import analyseSite
import threading
from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*")



def write_to_file(data):
    print("dattta  == ", data)
    with open("urls.txt", "w") as file:
        for item in data:
            file.write(item + "\n")

def lunchApi(typePro, data):
    try:
        if typePro == "oneUrl":
            write_to_file([data["url"]])
            result = analyseSite()
        else:
            result = analyseSite(data)

        print("Analyse terminée")

        
        socketio.emit('analyse_done', {'message': 'Analyse terminée', 'data': result})

    except Exception as e:
        print(f"Error during analysis: {e}")
        socketio.emit('analyse_done', {'message': 'Erreur lors de l\'analyse', 'data': str(e)})


@app.route('/api/analyse', methods=['POST'])
def analyse():
    data = request.get_json()  
    
    thread = threading.Thread(target=lunchApi, args=("multipleUrl", data))
    thread.start()

    return jsonify({"message": "Analyse en cours, vous serez notifié quand elle sera terminée"}), 202


@app.route('/api/analyse/oneUrl', methods=['POST'])
def analyseOneLink():
    print("elaaaaaaaaaa")
    data = request.get_json()  
    print(data)
    
    thread = threading.Thread(target=lunchApi, args=("oneUrl", data))
    thread.start()

    return jsonify({"message": "Analyse en cours, vous serez notifié quand elle sera terminée"}), 202


if __name__ == '__main__':
    socketio.run(app, debug=True)
