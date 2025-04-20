#!/usr/bin/env python3
"""
NEXDB: Main application entry point
"""
import os
from app import create_app
from app.cli import register_cli_commands

app = create_app()
register_cli_commands(app)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=app.config.get("DEBUG", False)) 