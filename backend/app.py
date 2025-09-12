from google import genai
from google.genai import types

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_JUSTIFY
from flask import send_file, request
import io


from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
import psycopg2
import os

DATABASE_URL = os.getenv("DATABASE_URL")
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

app = Flask(__name__)
CORS(app)

# --- Conexión a PostgreSQL ---
DATABASE_URL = os.environ.get("DATABASE_URL")

'''def get_conn():
    return psycopg2.connect(DATABASE_URL)'''

'''def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS interacciones (
            id SERIAL PRIMARY KEY,
            user_id TEXT,
            personaje TEXT,
            tema TEXT,
            tono TEXT,
            cuento TEXT,
            fecha_hora TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()'''

@app.route("/")
def home():
    return app.send_static_file("index.html")

# --- Endpoint para generar cuento ---
@app.route("/generate", methods=["POST"])
def generate_story():
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
@app.route("/save_iteration", methods=["POST"])
def save_iteration():
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
    

@app.route("/download_pdf", methods=["POST"])
def download_pdf():
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
        leading=15  # altura de línea
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
