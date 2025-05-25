from flask import Flask, request, jsonify

app = Flask(__name__)

TEXTO_GLOBAL = ""

@app.route('/get-texto', methods=['GET'])
def holamundo():
    global TEXTO_GLOBAL 
    return jsonify({"texto": TEXTO_GLOBAL}), 200

@app.route('/post-texto',methods=['POST'])
def method_name():
    global TEXTO_GLOBAL
    data = request.get_json()
    if not data or 'texto' not in data:
        return jsonify({"error": "Falta campo 'texto' en el JSON "}), 400
    TEXTO_GLOBAL = data['texto']
    return jsonify({"mensaje": "OK"}), 200
        

if __name__ == '__main__':
    app.run()