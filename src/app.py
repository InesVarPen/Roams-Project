import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from transformers import AutoTokenizer, AutoModelForCausalLM
import sqlite3
import re

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
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

import sqlite3

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
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if USER_CREDENTIALS.get(username) == password:
        session['authenticated'] = True
        session['username'] = username  # Guardar nombre de usuario en la sesión
        return jsonify({"message": "Autenticación exitosa"}), 200
    else:
        return render_template('login.html', error='Usuario o contraseña incorrectos'), 401

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('authenticated', None)
    session.pop('username', None)
    return render_template('login.html'), 401

@app.route('/')
def form():
    if not session.get('authenticated'):
        return render_template('login.html')
    return render_template('form.html', models=MODELS.keys())

@app.route('/logs', methods=['GET'])
def view_logs():
    if not session.get('authenticated') or 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    model_filter = request.args.get('model', 'all')  # Obtener el filtro de modelo

    conn = sqlite3.connect("logs.db")
    cursor = conn.cursor()

    if model_filter == "all":
        cursor.execute("SELECT model, prompt, max_length, temperature, top_p, generated_text, timestamp FROM logs WHERE username = ? ORDER BY timestamp DESC", (username,))
    else:
        cursor.execute("SELECT model, prompt, max_length, temperature, top_p, generated_text, timestamp FROM logs WHERE username = ? AND model = ? ORDER BY timestamp DESC", (username, model_filter))

    logs = cursor.fetchall()
    conn.close()

    return render_template('logs.html', logs=logs, model_filter=model_filter)


@app.route('/submit', methods=['POST'])
def submit_form():
    if not session.get('authenticated') or 'username' not in session:
        return jsonify({"error": "No autorizado"}), 403
    
    username = session['username']  # Obtener el usuario autenticado
    model_choice = request.form.get('model', 'gpt2-spanish')  # Modelo seleccionado
    prompt = request.form.get('prompt', '').strip()
    max_length = request.form.get('max_length', 100, type=int)
    temperature = request.form.get('temperature', 0.7, type=float)
    top_p = request.form.get('top_p', 0.9, type=float)

    # Validaciones
    if not prompt:
        return jsonify({"error": "El prompt no debe estar vacío"}), 400
    if len(prompt) > 500:
        return jsonify({"error": "El prompt debe tener como mucho 500 caracteres"}), 400
    if '@' in prompt or '/' in prompt:
        return jsonify({"error": "Los caracteres '@' o '/' están prohibidos"}), 400
    if not re.search(r'[a-zA-Z]', prompt):
        return jsonify({"error": "El prompt debe tener al menos una letra"}), 400
    if re.search(r'\b(?:delete|drop|insert|update)\b', prompt, re.IGNORECASE):
        return jsonify({"error": "El prompt contiene palabras prohibidas por SQL"}), 400

    try:
        # Cargar el modelo correspondiente
        model_name = MODELS.get(model_choice, "gpt2-spanish")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)
        
        # Tokeniza el prompt y lo envía al modelo
        input_ids = tokenizer.encode(prompt, return_tensors="pt")
        output = model.generate(
            input_ids,
            max_length=max_length,
            temperature=temperature,
            top_p=top_p,
            do_sample=True,
        )
        generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
        
        # Guardar en la base de datos con el nombre de usuario autenticado y el modelo seleccionado
        conn = sqlite3.connect("logs.db")
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO logs (username, model, prompt, max_length, temperature, top_p, generated_text)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (username, model_choice, prompt, max_length, temperature, top_p, generated_text))
        conn.commit()
        conn.close()
        
        return render_template(
            "form.html",
            prompt=prompt,
            max_length=max_length,
            temperature=temperature,
            top_p=top_p,
            generated_text=generated_text,
            models=MODELS.keys()
        )
    except Exception as e:
        return render_template("form.html", error=f"Error al procesar el texto: {str(e)}", models=MODELS.keys())

if __name__ == '__main__':
    app.run(debug=DEBUG)
