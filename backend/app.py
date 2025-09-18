from flask import send_file, request
import io


from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from datetime import datetime
import os

# Configuración inicial de la aplicación Flask.
# - Se obtienen las variables de entorno necesarias:
#   DATABASE_URL: conexión a la base de datos PostgreSQL.
#   GEMINI_API_KEY: clave de acceso a la API de Gemini.
DATABASE_URL = os.getenv("DATABASE_URL")
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# - Se crea la aplicación Flask indicando:
#   static_folder: ruta donde se encuentran los archivos estáticos (CSS, JS, imágenes).
#   static_url_path: define cómo se accederá a esos archivos desde la URL raíz.
app = Flask(
    __name__,
    static_folder="../static",   
    static_url_path=""           
)

# Ruta principal de la aplicación ("/").
# - Cuando un usuario accede a la raíz de la web, Flask devuelve el archivo
#   "index.html" que está dentro de la carpeta definida como estática.
# - En este caso, la carpeta estática es "../static", por lo que servirá
#   el archivo ubicado en /Dulces_Sue-os_IA/static/index.html.
@app.route("/")
def home():
    # sirve /project-root/static/index.html
    return send_from_directory(app.static_folder, "index.html")

# --- Endpoint para generar cuento ---
# Este endpoint recibe una solicitud POST en "/generate" con un JSON que debe incluir:
#   - "personaje": protagonista del cuento
#   - "tema": tema central o ambientación
#   - "tono": estilo narrativo
#
# Funcionamiento:
# 1. Extrae los datos del JSON enviado por el cliente.
# 2. Inicializa el cliente de la API de Gemini usando la clave guardada en las variables de entorno.
# 3. Construye un mensaje de contexto detallado con instrucciones estrictas para el modelo:
# 4. Envía este mensaje al modelo "gemini-2.5-flash".
# 5. Devuelve la respuesta en formato JSON con la clave "cuento".
@app.route("/generate", methods=["POST"])
def generate_story():
    from google import genai
    from google.genai import types
    data = request.json
    personaje = data.get("personaje")
    tema = data.get("tema")
    tono = data.get("tono")

    # Inicializa el cliente
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # Mensaje de contexto para el modelo
    context_message = f"""
    Eres un generador de cuentos completamente seguro y apropiado para niños en castellano, usando un lenguaje sencillo y educativo. Tu misión es crear historias únicas, enriquecedoras y entretenidas para niños de 4 a 10 años, que también sean agradables y educativas para los padres que las leen o escuchan. 

    - Bajo ninguna circunstancia incluyas violencia, sexualidad, drogas, lenguaje ofensivo, miedos extremos, acoso, discriminación, o cualquier tema inapropiado para menores.
    - Si se solicita algo fuera de lo permitido, responde estrictamente: "Este no es un tema apropiado para niños, por favor elige otro."
    - Tu historia debe **ceñirse estrictamente** a los parámetros dados:
    * Protagonista: {personaje}
    * Tipo de cuento / tema central: {tema}
    * Tono / estilo: {tono}
    - Cada cuento debe ser **original, creativo y variado**, asegurando que ninguna historia se repita exactamente y que proporcione una experiencia enriquecedora y memorable.
    - Mantén la narrativa clara y comprensible, con estructuras adecuadas a la edad del niño, fomentando valores positivos como amistad, curiosidad, empatía, imaginación y aprendizaje.
    - La duración de la historia debe ser suficiente para leerla en **aproximadamente 4 a 5 minutos**.

    Cumple estas normas al pie de la letra y no te desvíes del propósito de la aplicación.
    """


    # Llamada al modelo
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=context_message,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        ),
    )


    return jsonify({"cuento": response.text})

# --- Endpoint para guardar interacción ---
# Este endpoint recibe una solicitud POST en "/save_iteration" con un JSON que debe incluir:
# - "personaje": protagonista del cuento
# - "tema": tema central o ambientación
# - "tono": estilo narrativo
# - "cuento": el texto completo generado por la app
# Funcionamiento:
# 1. Extrae los datos del JSON enviado por el cliente.
# 2. Obtiene la fecha y hora actual en formato "YYYY-MM-DD HH:MM:SS" para registrar cuándo se guardó 
# la interacción.
# 3. Se conecta a la base de datos PostgreSQL usando la variable de entorno DATABASE_URL.
# 4. Crea la tabla dulces_suenos_IA si no existe
# 5. Inserta los datos recibidos en la tabla.
# 6. Cierra la conexión a la base de datos.
# 7. Devuelve un JSON con {"status": "ok"} si la operación fue exitosa.
# 8. En caso de error en cualquier paso de la conexión o inserción, captura la excepción, imprime el error 
# en consola y devuelve un JSON con {"status": "error", "message": <mensaje del error>} con código HTTP 500.
@app.route("/save_iteration", methods=["POST"])
def save_iteration():
    import psycopg2
    data = request.json
    personaje = data.get("personaje")
    tema = data.get("tema")
    tono = data.get("tono")
    cuento = data.get("cuento")
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS dulces_suenos_IA (
            id SERIAL PRIMARY KEY,
            fecha_hora TEXT NOT NULL,
            personaje TEXT NOT NULL,
            tema TEXT NOT NULL,
            tono TEXT NOT NULL,
            cuento TEXT NOT NULL 
        )
        """)
        conn.commit()
        cur.execute(f"""
            INSERT INTO dulces_suenos_IA (fecha_hora, personaje, tema, tono, cuento)
            VALUES ('{fecha_hora}', '{personaje}', '{tema}', '{tono}', '{cuento}')
        """)
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "ok"})
    except Exception as e:
        print("Error guardando en DB:", e)
        return jsonify({"status": "error", "message": str(e)}), 500
    

# --- Endpoint para descargar cuento en PDF ---
# Este endpoint recibe una solicitud POST en "/download_pdf" con un JSON que debe incluir:
# - "theme": tema del cuento (opcional, por defecto "Sin tema")
# - "character": personaje principal (opcional, por defecto "Sin personaje")
# - "tone": tono o estilo narrativo (opcional, por defecto "Normal")
# - "story": texto completo del cuento
# Funcionamiento:
# 1. Extrae los datos del JSON enviado por el cliente y asigna valores por defecto si algún campo no existe.
# 2. Crea un buffer en memoria (io.BytesIO) que servirá para almacenar el PDF antes de enviarlo al cliente.
# 3. Inicializa un documento A4 (SimpleDocTemplate) con márgenes definidos para todo el contenido.
# 4. Obtiene los estilos de texto estándar (getSampleStyleSheet) y crea un estilo justificado (ParagraphStyle) 
# con altura de línea adecuada para lectura cómoda.
# 5. Construye la lista story_elements que contendrá los elementos del PDF
# 6. Genera el PDF en el buffer usando doc.build(story_elements).
# 7. Reposiciona el buffer al inicio (buffer.seek(0)) para que pueda ser leído desde el principio.
# 8. Devuelve el archivo PDF al cliente mediante send_file
# Resultado: el usuario recibe un PDF listo para descargar con el cuento formateado y los metadatos visibles 
# (tema, personaje, tono).
@app.route("/download_pdf", methods=["POST"])
def download_pdf():
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.enums import TA_JUSTIFY
    data = request.get_json()
    theme = data.get("theme", "Sin tema")
    character = data.get("character", "Sin personaje")
    tone = data.get("tone", "Normal")
    story = data.get("story", "")

    buffer = io.BytesIO()
    
    # Documento A4 con márgenes
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    justify_style = ParagraphStyle(
        'Justify',
        parent=styles['Normal'],
        alignment=TA_JUSTIFY,
        leading=15 
    )

    story_elements = []
    story_elements.append(Paragraph(f"<b>Tema:</b> {theme}", styles["Heading3"]))
    story_elements.append(Paragraph(f"<b>Personaje:</b> {character}", styles["Normal"]))
    story_elements.append(Paragraph(f"<b>Tono:</b> {tone}", styles["Normal"]))
    story_elements.append(Spacer(1, 12))

    # Convertir saltos de línea en <br/> para que respeten el formato
    story_html = story.replace("\n", "<br/>")
    story_elements.append(Paragraph("<b>Cuento:</b>", styles["Heading3"]))
    story_elements.append(Paragraph(story_html, justify_style))

    doc.build(story_elements)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"cuento_{theme.replace(' ', '_')}.pdf",
        mimetype="application/pdf"
    )

# --- Bloque principal para ejecutar la aplicación Flask ---
# Este bloque se ejecuta solo si el script se ejecuta directamente (python app.py) y no si se importa como módulo 
# en otro script.
# 1. Obtiene el puerto en el que correrá la app:
# - Primero intenta leer la variable de entorno PORT (útil si se despliega en plataformas como Render, Heroku, etc.)
# - Si no existe, usa el puerto 5000 por defecto.
# 2. Llama a app.run() para iniciar el servidor Flask:
# - host="0.0.0.0" permite que el servidor sea accesible desde cualquier IP, no solo localhost.
# - port=port define el puerto donde escuchará la app.
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

