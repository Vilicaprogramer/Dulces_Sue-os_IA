import requests

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
    print("Cuento generado (preview):", data["cuento"][:50], "...")

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
