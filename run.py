"""Universal server runner for Render and cloud hosting."""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting NexaData AI server on 0.0.0.0:{port}...")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port)
