from analyseSite import analyseSite
import threading
from flask import Flask, request, jsonify
from flask_socketio import SocketIO

# Création de l'application Flask
app = Flask(__name__)

# Initialiser l'instance de SocketIO
socketio = SocketIO(app)

def lunchApi():
    # Exécuter l'algorithme dans un thread séparé
    result = analyseSite()
    print("Analyse terminée")

    # Émettre l'événement de notification via SocketIO
    socketio.emit('analyse_done', {'message': 'Analyse terminée', 'data': result})

@app.route('/api/analyse', methods=['POST'])
def analyse():
    # Lancer l'analyse dans un thread séparé pour éviter le timeout
    thread = threading.Thread(target=lunchApi)
    thread.start()

    # Répondre immédiatement avec un message de statut
    return jsonify({"message": "Analyse en cours, vous serez notifié quand elle sera terminée"}), 202

if __name__ == '__main__':
    # Lancer l'application avec SocketIO
    socketio.run(app, debug=True)
