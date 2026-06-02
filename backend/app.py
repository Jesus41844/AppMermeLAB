"""Compat wrapper para Gunicorn.

La implementación real vive en ``mermelab.create_app``.
"""

import os
from mermelab import create_app

app = create_app()

if __name__ == "__main__":
    # Permite que la app corra al ejecutar: python app.py
    port = int(os.getenv("FLASK_PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=app.config.get("DEBUG", False))
