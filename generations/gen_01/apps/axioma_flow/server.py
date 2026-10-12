"""Facade re-exporting from src.server for Axioma Flow."""
import sys
from pathlib import Path
app_root = Path(__file__).parent
if str(app_root) not in sys.path:
    sys.path.insert(0, str(app_root))
from src.server import run_server, AppStateEngine, ExceptionEnclave, LANDAUER_LIMIT, AppHttpHandler, state_engine
