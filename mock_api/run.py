# Sobe só a API mock na porta 5001.
# Uso (na pasta mock_api):
#   pip install -r requirements.txt
#   python run.py


import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    porta = int(os.getenv("PORT", "5001"))
    # debug=True só pra desenvolvimento
    app.run(host="0.0.0.0", port=porta, debug=True)
