import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from transformers import AutoTokenizer, AutoModelForCausalLM
import sqlite3
import re
from flasgger import Swagger  

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configuración de Swagger
# Configuración de Swagger
app.config["SWAGGER"] = {
    "title": "API de Generación de Texto",
    "description": """
    **API de Generación de Texto**  
    Esta API permite la autenticación de usuarios y la generación de texto con modelos de lenguaje de Hugging Face.  

    **Endpoints disponibles:**  
    - **Autenticación:** `/login`, `/logout`  
    - **Generación de Texto:** `/submit`  
    - **Logs de actividad:** `/logs`  

    **Swagger UI:** [http://127.0.0.1:5000/apidocs](http://127.0.0.1:5000/apidocs)
    """,
    "version": "1.0.0"
}
swagger = Swagger(app)

# Leer variables de entorno
app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")
DEBUG = os.getenv("DEBUG", "True") == "True"
DATABASE_NAME = os.getenv("DATABASE_NAME", "database/logs.db")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt2-spanish")

database_folder = os.path.dirname(DATABASE_NAME)
if database_folder and not os.path.exists(database_folder):
    os.makedirs(database_folder)


# Diccionario de modelos disponibles
MODELS = {
    "gpt2-spanish": "DeepESP/gpt2-spanish",
    "gpt2-english": "gpt2"
}

# Función para inicializar la base de datos
def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            model TEXT,
            prompt TEXT,
            max_length INTEGER,
            temperature REAL,
            top_p REAL,
            generated_text TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Diccionario de usuarios y contraseñas (simulado)
USER_CREDENTIALS = {
    "root": "toor",
    "ines": "12345"
}

@app.route('/login', methods=['POST'])
def login():
    """
    Inicia sesión con usuario y contraseña
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              example: "root"
            password:
              type: string
              example: "toor"
    responses:
      200:
        description: Autenticación exitosa
      401:
        description: Usuario o contraseña incorrectos
    """
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if USER_CREDENTIALS.get(username) == password:
        session['authenticated'] = True
        session['username'] = username  
        return jsonify({"message": "Autenticación exitosa"}), 200
    else:
        return jsonify({"error": "Usuario o contraseña incorrectos"}), 401

@app.route('/logout', methods=['GET'])
def logout():
    """
    Cierra la sesión del usuario autenticado
    ---
    responses:
      200:
        description: Sesión cerrada
    """
    session.pop('authenticated', None)
    session.pop('username', None)
    return jsonify({"message": "Sesión cerrada"}), 200

@app.route('/logs', methods=['GET'])
def view_logs():
    """
    Muestra los logs del usuario autenticado
    ---
    parameters:
      - name: model
        in: query
        type: string
        required: false
        description: Filtrar logs por modelo
    responses:
      200:
        description: Lista de logs del usuario
    """
    if not session.get('authenticated') or 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    model_filter = request.args.get('model', 'all')

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    if model_filter == "all":
        cursor.execute("SELECT model, prompt, max_length, temperature, top_p, generated_text, timestamp FROM logs WHERE username = ? ORDER BY timestamp DESC", (username,))
    else:
        cursor.execute("SELECT model, prompt, max_length, temperature, top_p, generated_text, timestamp FROM logs WHERE username = ? AND model = ? ORDER BY timestamp DESC", (username, model_filter))

    logs = cursor.fetchall()
    conn.close()

    return jsonify({"logs": logs})

@app.route('/submit', methods=['POST'])
def submit_form():
    """
    Envía un prompt y genera texto con el modelo seleccionado
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            model:
              type: string
              example: "gpt2-spanish"
            prompt:
              type: string
              example: "Había una vez un dragón que..."
            max_length:
              type: integer
              example: 100
            temperature:
              type: number
              format: float
              example: 0.7
            top_p:
              type: number
              format: float
              example: 0.9
    responses:
      200:
        description: Texto generado exitosamente
        schema:
          type: object
          properties:
            generated_text:
              type: string
              example: "Había una vez un dragón que protegía una aldea secreta..."
      400:
        description: Error en la entrada del prompt
        schema:
          type: object
          properties:
            error:
              type: string
              example: "El prompt no debe estar vacío"
      403:
        description: No autorizado (falta autenticación)
        schema:
          type: object
          properties:
            error:
              type: string
              example: "No autorizado"
    """
    if not session.get('authenticated') or 'username' not in session:
        return jsonify({"error": "No autorizado"}), 403

    username = session['username']
    data = request.json
    model_choice = data.get('model', 'gpt2-spanish')
    prompt = data.get('prompt', '').strip()
    max_length = data.get('max_length', 100)
    temperature = data.get('temperature', 0.7)
    top_p = data.get('top_p', 0.9)

    if not prompt:
        return jsonify({"error": "El prompt no debe estar vacío"}), 400
    if len(prompt) > 500:
        return jsonify({"error": "El prompt debe tener como máximo 500 caracteres"}), 400
    if not re.search(r'[a-zA-Z]', prompt):
        return jsonify({"error": "El prompt debe tener al menos una letra"}), 400

    try:
        model_name = MODELS.get(model_choice, "gpt2-spanish")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)

        input_ids = tokenizer.encode(prompt, return_tensors="pt")
        output = model.generate(input_ids, max_length=max_length, temperature=temperature, top_p=top_p, do_sample=True)
        generated_text = tokenizer.decode(output[0], skip_special_tokens=True)

        return jsonify({"generated_text": generated_text}), 200

    except Exception as e:
        return jsonify({"error": f"Error al generar texto: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=DEBUG)
