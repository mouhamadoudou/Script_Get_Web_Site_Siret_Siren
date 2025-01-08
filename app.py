from analyseSite import analyseSite
import threading
from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*")  

def lunchApi():
    try:
        result = analyseSite() 
        print("Analyse terminée")
        
        socketio.emit('analyse_done', {'message': 'Analyse terminée', 'data': result})
    except Exception as e:
        print(f"Error during analysis: {e}")
        socketio.emit('analyse_done', {'message': 'Erreur lors de l\'analyse', 'data': str(e)})

@app.route('/api/analyse', methods=['POST'])
def analyse():
    thread = threading.Thread(target=lunchApi)
    thread.start()

    return jsonify({"message": "Analyse en cours, vous serez notifié quand elle sera terminée"}), 202

if __name__ == '__main__':
    socketio.run(app, debug=True)
