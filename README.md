# 🚀 API de Generación de Texto con Flask y Transformers

Esta API permite la autenticación de usuarios y la generación de texto con modelos de `Hugging Face Transformers`. Los logs de las solicitudes se almacenan en una base de datos SQLite.  

Incluye documentación interactiva con **Swagger** y permite activarlo o desactivarlo con una variable de entorno.

---

## 📂 **Estructura del Proyecto**
```
📁 tu_proyecto  
 ├── 📄 app.py               # Código principal de la API  
 ├── 📄 app_swagger.py       # Versión con Swagger   
 ├── 📂 templates/           # Plantillas HTML  
 ├── 📄 requirements.txt     # Lista de paquetes necesarios  
 ├── 📄 .env.example         # Variables de entorno de ejemplo  
 ├── 📄 README.md            # Documentación del proyecto  
 ├── 📄 .gitignore           # Para evitar subir archivos innecesarios  
 ├── 📂 database/            # Base de datos local (SQLite)  
 │   ├── logs.db             
```

---

## ⚙️ **Instalación y Configuración**
### **1️⃣ Clonar el repositorio**
```bash
git clone https://github.com/InesVarPen/Roams-Project.git
cd Roams-Project
```

### **2️⃣ Crear un entorno virtual **
```bash
python -m venv env
source env/bin/activate  # En macOS/Linux
env\Scripts\activate     # En Windows
```

### **3️⃣ Instalar dependencias**
Ejecuta este comando para instalar todas las librerías necesarias:
```bash
pip install -r requirements.txt
```

### **4️⃣ Configurar las variables de entorno**
Antes de ejecutar la API, necesitas configurar las variables de entorno.

1️⃣ Copia el archivo `env_example` y renómbralo como `.env`:
```bash
cp env_example.txt .env
```
2️⃣ Abre `.env` y edita los valores según sea necesario:
```ini
SECRET_KEY=supersecretkey
DEBUG=True
DATABASE_NAME=/database/logs.db
```
---

## ▶️ **Ejecutar la API**
Una vez configurado el entorno, inicia la aplicación con:
```bash
python app.py
```
La API estará disponible en **http://127.0.0.1:5000/**.

📌 **Ejecutar Swagger**
```bash
python app_swagger.py
```
**Para acceder a la documentación:**  

🔗 **http://127.0.0.1:5000/apidocs**

---

## 🔐 **Autenticación**
La API usa un sistema de autenticación de usuarios basado en sesiones.  
Con credenciales predefinidas:

    "username": "root",
    "password": "toor"

     "username": "ines",
    "password": "12345"

Puedes añadir más usuarios en el diccionario de credenciales en app.py
Al ser una demo, se usan estas credenciales tan débiles. Se aconseja ponerlas seguras o emplear otros métodos 2FA.

Si el login es exitoso, la sesión se almacenará y podrás acceder al formulario de generación de texto.

---

## 🛠 **Endpoints Disponibles**
| Método | Ruta          | Descripción |
|--------|--------------|-------------|
| `POST` | `/login`     | Inicia sesión con usuario y contraseña |
| `GET`  | `/logout`    | Cierra sesión del usuario |
| `GET`  | `/logs`      | Muestra los logs del usuario autenticado |
| `POST` | `/submit`    | Genera texto con el modelo seleccionado |
| `GET`  | `/`          | Página de bienvenida de la API |

📌 **Puedes probar estos endpoints directamente en `http://127.0.0.1:5000/apidocs`.**


## 📝 **Tecnologías utilizadas**
- Python 3.x
- Flask
- Hugging Face Transformers
- SQLite
- Flasgger (Swagger para Flask)
- Jinja2 (si usas plantillas HTML)

---

## 🚀 **Contribuir**
Si quieres mejorar este proyecto:
1. Haz un fork 🍴
2. Crea una nueva rama `git checkout -b mi-feature`
3. Haz cambios y commitea `git commit -m "Mi nueva funcionalidad"`
4. Haz push a la rama `git push origin mi-feature`
5. Abre un Pull Request en GitHub 🚀

---

## 📩 **Contacto**
Si tienes dudas o sugerencias, puedes escribirme a:  
📧 [ines.var@icloud.com](mailto:ines.var@icloud.com)  



