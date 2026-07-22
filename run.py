# Arquivo pra subir o servidor Flask na máquina.
# Uso: python run.py
# Depois abre no navegador: http://127.0.0.1:5000

from app import create_app

app = create_app()

if __name__ == "__main__":
    # debug=True recarrega sozinho quando a gente muda o código.
    app.run(host="0.0.0.0", port=5000, debug=True)
