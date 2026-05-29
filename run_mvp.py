"""One-click Launcher for the Rescue Robot System Web Dashboard MVP.

Binds the static HTML/CSS/JS frontend to the FastAPI server on port 8000,
launches the uvicorn process, and opens the dashboard in the operator's browser.
"""
from __future__ import annotations

import os
import sys
import threading
import time
import webbrowser

# Target Server address
HOST = "127.0.0.1"
PORT = 8000
URL = f"http://{HOST}:{PORT}"


def install_dependencies() -> None:
    """Pre-verification check for mandatory packages."""
    try:
      import fastapi
      import uvicorn
      print("[Launcher] Pre-req check: fastapi and uvicorn are already installed.")
    except ImportError:
      print("[Launcher] Dependencies missing. Running automated pip install setup...")
      import subprocess
      subprocess.check_call([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn"])
      print("[Launcher] Setup complete.")


def open_browser() -> None:
    """Opens the local browser tab targeted at the Dashboard single port server."""
    print(f"\n[Launcher] Dashboard single port server ready.")
    print(f"[Launcher] Opening operator browser at: {URL}\n")
    webbrowser.open(URL)


def main() -> None:
    # 1. Setup dev profile env variable
    os.environ["RUNTIME_PROFILE"] = "dev-windows-local"

    # Add 'src' directory to Python search path dynamically
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

    # 2. Verify dependencies
    install_dependencies()

    # 3. Schedule automated browser open in 1.2 seconds (after server starts listening)
    threading.Timer(1.2, open_browser).start()

    # 4. Start Uvicorn ASGI Server
    import uvicorn
    
    print(f"[Launcher] Starting FastAPI ASGI Server on {HOST}:{PORT}...")
    try:
      uvicorn.run(
          "api.server:app",
          host=HOST,
          port=PORT,
          log_level="info",
          reload=False, # Disable reload for stable manual simulations
      )
    except KeyboardInterrupt:
      print("\n[Launcher] Shutdown signal received. Closing Rescue Robot Panel.")
    except Exception as e:
      print(f"\n[Launcher] Critical Server Error: {e}")


if __name__ == "__main__":
    main()
