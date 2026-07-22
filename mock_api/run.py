# Sobe só a API mock na porta 5001.
# Uso (na pasta mock_api):
#   pip install -r requirements.txt
#   python run.py
#
# Depois teste no navegador:
#   http://127.0.0.1:5001/agendamentos

import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    porta = int(os.getenv("PORT", "5001"))
    # No Docker: FLASK_DEBUG=0. Local: pode deixar 1.
    debug = os.getenv("FLASK_DEBUG", "1") == "1"
    app.run(host="0.0.0.0", port=porta, debug=debug)
