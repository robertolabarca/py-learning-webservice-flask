from flask import Flask, request, jsonify

from entities.course import Course
from entities.student import Student

app = Flask(__name__)

TEXTO_GLOBAL = ""
COURSE_GLOBAL=None
STUDENT_GLOBAL=None

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
    return jsonify(COURSE_GLOBAL.to_entity()),200

@app.route('/set-course',methods=['POST'])
def set_course():
    global COURSE_GLOBAL
    data=request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'El campo "name" es obligatorio'}), 400
    
    if COURSE_GLOBAL is None:
        COURSE_GLOBAL= Course(course_id=data["id"],name=data["name"],description=data["description"])
    return jsonify(COURSE_GLOBAL.to_entity()),200

@app.route('/set-student',methods=['POST'])
def set_student():
    global STUDENT_GLOBAL
    data=request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'El campo "name" es obligatorio'}), 400
    
    if STUDENT_GLOBAL is None:
        STUDENT_GLOBAL=Student(id=data["id"],name=data["name"],age=21)
    
    return jsonify(STUDENT_GLOBAL),200



if __name__ == '__main__':
    app.run()