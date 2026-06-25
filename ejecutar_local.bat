@echo off
cd /d "%~dp0"

if not exist venv (
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install -q -r requirements.txt

if not exist .env if exist .env.example (
    copy .env.example .env
    echo Creado .env desde .env.example — edita GROQ_API_KEY antes de usar el asistente.
)

streamlit run app.py
