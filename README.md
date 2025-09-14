# 🌙 Dulces Sueños IA

Aplicación web desarrollada en **Flask** que permite interactuar con una API de IA para generar historias.
La aplicación se ha desplegado en Render y cuenta con integración con una base de datos PostgreSQL.

---

## 📂 Estructura del proyecto

```
backend/                 # Código backend de la aplicación
│   ├── app.py           # Aplicación principal en Flask
│   └── test/            # Tests de pytest
│       └── test.py      
│
static/                  # Archivos estáticos
│   ├── css/
│   │   └── style.css    # Estilos de la página
│   ├── img/
│   │   └── Dulces_suenos_IA.png   # Imagen utilizada en la app
│   ├── js/
│   │   └── script.js    # Lógica en JavaScript
│   └── index.html       # Página principal
│
.gitignore
dockerfile               # Configuración del contenedor Docker
requirements.txt         # Dependencias de Python
```

---

## 🚀 Ejecución en local

1. Clonar el repositorio:

   ```bash
   git clone https://github.com/Vilicaprogramer/Dulces_Sue-os_IA
   cd Dulces_Sue-os_IA
   ```

2. Crear un entorno virtual:

   ```bash
   python -m venv venv
   source venv/bin/activate   # En Linux/Mac
   venv\Scripts\activate      # En Windows
   ```

3. Instalar dependencias:

   ```bash
   pip install -r requirements.txt
   ```

4. Ejecutar la aplicación:

   ```bash
   python backend/app.py
   ```

5. Abrir en navegador:

   ```
   http://127.0.0.1:5000
   ```

---

## 🐳 Ejecución con Docker

La aplicación también está disponible como imagen en **Docker Hub**.

```bash
docker run -p 5000:5000 vilica/app-cuentos:latest
```

---

## 🌐 Uso desde Render

La aplicación está desplegada en Render y puede utilizarse directamente desde cualquier navegador en la siguiente URL:

👉 **[https://dulces-suenos-ia.onrender.com](https://dulces-suenos-ia.onrender.com)**

---

## 📌 Notas

* El proyecto utiliza **Flask** como backend.
* Los estilos y scripts están organizados en la carpeta `static`.
* Render está configurado con una base de datos **PostgreSQL** gratuita.
* Se puede ampliar fácilmente para añadir nuevas funcionalidades como generación de voz (TTS) o imágenes con la API de Gemini.

---

## ✨ Autor

Proyecto creado por [Tu Nombre](https://github.com/tu_usuario).
