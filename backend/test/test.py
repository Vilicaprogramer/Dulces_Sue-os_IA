import requests

# Test para el endpoint /generate.
# Envía una petición POST que incluye un personaje, un tema y un tono.
# Verifica que la respuesta tenga código 200, que el JSON contenga la clave "cuento"
# y que el cuento generado no esté vacío. .
def test_generate_endpoint():
    url = 'http://localhost:5000/generate'
    payload = {
        "personaje": "Tito el dragón",
        "tema": "Una aventura en la luna",
        "tono": "aventurero"
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "cuento" in data
    assert len(data["cuento"]) > 0

# Test para el endpoint /save_iteration.
# Envía una petición POST que incluye personaje, tema, tono y el cuento completo.
# Verifica que la respuesta tenga código 200 y que el JSON devuelto contenga
# la clave "status" con el valor "ok", confirmando que la iteración se guardó correctamente.
def test_save_iteration_endpoint():
    url = 'http://localhost:5000/save_iteration'
    payload = {
        "personaje": "Luna la conejita",
        "tema": "El bosque mágico",
        "tono": "dulce",
        "cuento": "Había una vez una conejita muy curiosa..."
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

# Test para el endpoint /download_pdf.
# Envía una petición POST con los datos de tema, personaje, tono e historia completos.
# Verifica que la respuesta tenga código 200, que el encabezado "Content-Type" sea "application/pdf"
# y que el contenido devuelto tenga un tamaño mayor a 100 bytes, asegurando que se generó un PDF válido.
def test_download_pdf_endpoint():
    url = 'http://localhost:5000/download_pdf'
    payload = {
        "theme": "El dragón y la luna",
        "character": "Tito el dragón",
        "tone": "aventurero",
        "story": "Había una vez un dragón que quería volar hasta la luna..."
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/pdf"
    assert len(response.content) > 100  # Comprobamos que hay contenido en el PDF
