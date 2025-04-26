from flask import Flask, request, render_template, jsonify
from flask_socketio import SocketIO
import eventlet

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')

# Herätys säilötään tähän sanakirjaan
heratys = {}

@app.route('/')
def index():
    return render_template('index.html', heratys=heratys)

@app.route('/lisaa_heratys', methods=['POST'])
def lisaa_heratys():
    global heratys  # Tämä tarvitaan, jotta voidaan muokata globaalia muuttujaa
    aika = request.form.get('aika')
    teksti = request.form.get('teksti')

    if not aika or not teksti:
        return "Virheellinen syöte", 400

    heratys['aika'] = aika
    heratys['teksti'] = teksti
    print("Herätys lisätty:", heratys)
    socketio.emit('heratys_paivittynyt', heratys)
    return render_template('index.html', heratys=heratys)

@app.route('/hae_heratys', methods=['GET'])
def hae_heratys():
    try:
        if not heratys or 'aika' not in heratys or 'teksti' not in heratys:
            return jsonify({"aika": "", "teksti": ""})
        return jsonify(heratys)
    except Exception as e:
        print("Virhe haettaessa herätystä:", e)
        return jsonify({"aika": "", "teksti": "", "virhe": str(e)}), 500

if __name__ == '__main__':
    socketio.run(app)