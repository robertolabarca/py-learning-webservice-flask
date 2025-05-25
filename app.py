from flask import Flask, request, jsonify

from entities.course import Course

app = Flask(__name__)

TEXTO_GLOBAL = ""
COURSE_GLOBAL=None

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

@app.route('/get-course',methods=['GET'])
def get_course():
    global COURSE_GLOBAL
    if COURSE_GLOBAL is None:
        return jsonify({"error":"error"}),404
    return jsonify(COURSE_GLOBAL.to_entitie()),200

@app.route('/set-course',methods=['POST'])
def set_course():
    global COURSE_GLOBAL
    data=request.get_json()
    if COURSE_GLOBAL is None:
        COURSE_GLOBAL= Course(course_id=data["id"],name=data["name"],description=data["description"])
    return jsonify(COURSE_GLOBAL.to_entitie()),200

if __name__ == '__main__':
    app.run()