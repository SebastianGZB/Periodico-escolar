# 📰 Periódico Escolar

Proyecto en **Django 5** que implementa un periódico escolar con autenticación de usuarios, roles (lector, redactor, editor, administrador) y gestión de noticias (crear, editar, eliminar, reaccionar y comentar).

## ⚙️ Requisitos

- Python 3.10+ (recomendado 3.12 o 3.13)
- Django 5.1+
- Virtualenv (opcional, pero recomendado)

## 🚀 Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/SebastianGZB/Periodico-escolar
   cd periodico_escolar

2. python -m venv env
source env/bin/activate   # Linux / Mac
.\env\Scripts\activate    # Windows

3. pip install -r requirements.txt

4. python manage.py migrate

5. python manage.py createsuperuser

6. python manage.py runserver

## 📂 Estructura

periodico_escolar/
│── manage.py
│── periodico_escolar/       # Configuración del proyecto
│── noticias/                # App principal
│── static/                  # Archivos estáticos (CSS, JS, imágenes)
│── templates/               # Plantillas HTML


👤 Roles

Lector: puede leer noticias, reaccionar y comentar.

Redactor: puede crear y editar sus propias noticias.

Editor: puede editar y eliminar cualquier noticia.

Administrador: superusuario con permisos completos.

🧪 Tests

python manage.py test

📜 Licencia

Este proyecto es de uso académico y libre para modificaciones.