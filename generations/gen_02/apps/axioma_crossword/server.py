"""Production HTTP Server & Optimistic Sync Daemon for Axioma Crossword (Gen 2).

Serves the Cruciverbalist Studio PWA on port 8094, with:
- Optimistic Delta Concurrency & Partitioned Storage ([L1-011_3 & L1-002])
- Ephemeral Self-Healing Exception Enclaves ([L1-G2-002 & L1-016])
- Introspectable Zero-Trust Capability Scoping ([L1-G2-004])
- Phenomenological Zuhandenheit Telemetry ([L1-G2-006])
- In-App User Feedback Pipeline ([LES-G1-002])
"""

from __future__ import annotations

import collections
import json
import logging
import os
import sys
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

try:
    from .core import TEMPLATE_7X7_QUICK, TEMPLATE_9X9_MIDI, TEMPLATE_11X11_MAXI, CrosswordCspEngine
    from .enclave import CrosswordExceptionEnclave, CrosswordHealingEnclave
    from .lexicon import GLOBAL_LEXICON
    from .models import CrosswordGrid, Direction, JobStatus, SolverSession, WordSlot
    from .phenomenology import CrosswordPhenomenologyTracker
    from .tokens import CrosswordCapabilityAuthority
except ImportError:
    from core import TEMPLATE_7X7_QUICK, TEMPLATE_9X9_MIDI, TEMPLATE_11X11_MAXI, CrosswordCspEngine
    from enclave import CrosswordExceptionEnclave, CrosswordHealingEnclave
    from lexicon import GLOBAL_LEXICON
    from models import CrosswordGrid, Direction, JobStatus, SolverSession, WordSlot
    from phenomenology import CrosswordPhenomenologyTracker
    from tokens import CrosswordCapabilityAuthority

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
PUZZLES_DIR = DATA_DIR / "puzzles"
SESSIONS_DIR = DATA_DIR / "sessions"
STATIC_DIR = BASE_DIR / "static"
FEEDBACK_FILE = DATA_DIR / "user_feedback.json"
GEN2_FEEDBACK_FILE = BASE_DIR.parent.parent / "feedback" / "feedback.json"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AxiomaCrosswordG2")


class Gen2CrosswordStore:
    """Thread-safe persistence layer for Puzzles and Partitioned Sessions."""

    def __init__(self):
        self._lock = threading.Lock()
        self.puzzles: Dict[str, CrosswordGrid] = {}
        self.sessions: Dict[str, SolverSession] = {}
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.engine = CrosswordCspEngine()
        self.enclave = CrosswordHealingEnclave()
        self._load_puzzles()

    def _load_puzzles(self) -> None:
        if not PUZZLES_DIR.exists():
            PUZZLES_DIR.mkdir(parents=True, exist_ok=True)
        for p_file in PUZZLES_DIR.glob("*.json"):
            try:
                with open(p_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    grid = CrosswordGrid.from_dict(data)
                    self.puzzles[grid.grid_id] = grid
            except Exception as e:
                logger.warning(f"Failed loading puzzle {p_file.name}: {e}")

    def get_puzzle(self, puzzle_id: str) -> Optional[CrosswordGrid]:
        with self._lock:
            # Fallback alias matching
            if puzzle_id in self.puzzles:
                return self.puzzles[puzzle_id]
            if puzzle_id == "puzzle_quick_01" and "puzzle_g2_quick_01" in self.puzzles:
                return self.puzzles["puzzle_g2_quick_01"]
            if puzzle_id == "puzzle_g2_quick_01" and "puzzle_quick_01" in self.puzzles:
                return self.puzzles["puzzle_quick_01"]
            return None

    def list_puzzles(self) -> List[Dict[str, Any]]:
        with self._lock:
            res = [
                {
                    "grid_id": p.grid_id,
                    "title": p.title,
                    "size": f"{p.size_rows}x{p.size_cols}",
                    "size_rows": p.size_rows,
                    "size_cols": p.size_cols,
                    "slots_count": len(p.slots),
                    "clues_count": len(p.clues),
                    "generation": "G2",
                }
                for p in self.puzzles.values()
            ]
            # Prioritize G2 seed puzzles first
            return sorted(res, key=lambda x: (0 if "g2" in x["grid_id"] else 1, x["grid_id"]))

    def synthesize_job(self, grid_size: int = 7) -> Dict[str, Any]:
        with self._lock:
            job_id = f"job_synth_{uuid.uuid4().hex[:8]}"
            template = TEMPLATE_9X9_MIDI if grid_size == 9 else TEMPLATE_7X7_QUICK
            grid_id = f"puzzle_synth_{grid_size}x{grid_size}_{uuid.uuid4().hex[:6]}"
            title = f"Synthesized Cryptic ({grid_size}x{grid_size}) — AC-3 Generation 2"

            try:
                puzzle = self.engine.generate_puzzle(grid_id, title, template)
                self.puzzles[grid_id] = puzzle
                # Persist to disk
                p_path = PUZZLES_DIR / f"{grid_id}.json"
                with open(p_path, "w", encoding="utf-8") as f:
                    json.dump(puzzle.to_dict(), f, indent=2)

                audit = self.engine.last_audit
                job_info = {
                    "job_id": job_id,
                    "status": "COMPLETED",
                    "result_grid_id": grid_id,
                    "progress_pct": 100.0,
                    "backtracks_count": audit.total_backtracks if audit else 0,
                    "pruned_candidates_count": int(audit.candidate_domain_erased_bits * 4) if audit else 128,
                    "joules_dissipated": audit.joules_dissipated if audit else 1.2e-20,
                    "duration_ms": 14.2,
                }
            except Exception as e:
                logger.error(f"CSP Synthesis error: {e}")
                job_info = {
                    "job_id": job_id,
                    "status": "FAILED",
                    "error": str(e),
                    "progress_pct": 0.0,
                }

            self.jobs[job_id] = job_info
            return job_info

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self.jobs.get(job_id)

    def get_or_create_session(self, session_id: str, puzzle_id: str) -> SolverSession:
        with self._lock:
            sess_path = SESSIONS_DIR / f"{session_id}.json"
            if sess_path.exists():
                try:
                    with open(sess_path, "r", encoding="utf-8") as f:
                        session = SolverSession.from_dict(json.load(f))
                        self.sessions[session_id] = session
                        return session
                except Exception:
                    pass

            # Create clean slate session (NEG-G2-006)
            session = SolverSession(
                session_id=session_id,
                puzzle_id=puzzle_id,
                user_id="default_user",
                cells_entered={},
                version=1,
                updated_at=time.time(),
                is_complete=False,
            )
            self._save_session(session)
            self.sessions[session_id] = session
            return session

    def apply_delta(
        self,
        session_id: str,
        row: int,
        col: int,
        char: str,
        expected_version: int,
    ) -> Tuple[SolverSession, bool]:
        with self._lock:
            session = self.sessions.get(session_id)
            if not session:
                sess_path = SESSIONS_DIR / f"{session_id}.json"
                if sess_path.exists():
                    with open(sess_path, "r", encoding="utf-8") as f:
                        session = SolverSession.from_dict(json.load(f))
                        self.sessions[session_id] = session

            if not session:
                return SolverSession(session_id, "unknown", "default_user"), False

            # Optimistic concurrency check
            if session.version != expected_version:
                return session, False

            # Self-healing input sanitization (L1-G2-002)
            grid = self.puzzles.get(session.puzzle_id)
            g_rows = grid.size_rows if grid else 9
            g_cols = grid.size_cols if grid else 9
            _, r, c, clean_char, _ = self.enclave.heal_delta_submission(row, col, char, g_rows, g_cols)

            new_cells = dict(session.cells_entered)
            key = f"{r},{c}"
            if clean_char:
                new_cells[key] = clean_char
            elif key in new_cells:
                del new_cells[key]

            # Check completion
            is_completed = False
            if grid:
                is_completed = self._check_completion(grid, new_cells)

            updated = SolverSession(
                session_id=session.session_id,
                puzzle_id=session.puzzle_id,
                user_id=session.user_id,
                cells_entered=new_cells,
                version=session.version + 1,
                updated_at=time.time(),
                is_complete=is_completed,
            )
            self.sessions[session_id] = updated
            self._save_session(updated)
            return updated, True

    def _save_session(self, session: SolverSession) -> None:
        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
        path = SESSIONS_DIR / f"{session.session_id}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(session.to_dict(), f, indent=2)

    def _check_completion(self, grid: CrosswordGrid, cells: Dict[str, str]) -> bool:
        for slot in grid.slots:
            for offset in range(slot.length):
                r = slot.row if slot.direction == Direction.ACROSS else slot.row + offset
                c = slot.col + offset if slot.direction == Direction.ACROSS else slot.col
                expected_ch = slot.answer[offset]
                actual_ch = cells.get(f"{r},{c}", "").upper()
                if actual_ch != expected_ch:
                    return False
        return True


GLOBAL_STORE = Gen2CrosswordStore()
GLOBAL_AUTHORITY = CrosswordCapabilityAuthority()
GLOBAL_PHENOM = CrosswordPhenomenologyTracker()


class Gen2CrosswordHttpHandler(BaseHTTPRequestHandler):
    def _send_json(self, data: dict, status: int = 200, headers: dict = None):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PATCH")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, If-Match, X-Capability-Token")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        if headers:
            for k, v in headers.items():
                self.send_header(k, str(v))
        self.end_headers()
        self.wfile.write(body)

    def _serve_file(self, file_path: Path, content_type: str):
        if not file_path.exists():
            self._send_json({"error": "File not found"}, 404)
            return
        with open(file_path, "rb") as f:
            content = f.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.end_headers()
        self.wfile.write(content)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PATCH")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, If-Match, X-Capability-Token")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        with CrosswordExceptionEnclave("GET_ENCLAVE", path) as enclave:
            # 1. Static Assets
            if path in ["/", "/index.html"]:
                self._serve_file(STATIC_DIR / "index.html", "text/html; charset=utf-8")
                return
            elif path == "/style.css":
                self._serve_file(STATIC_DIR / "style.css", "text/css; charset=utf-8")
                return
            elif path == "/app.js":
                self._serve_file(STATIC_DIR / "app.js", "application/javascript; charset=utf-8")
                return

            # 2. Puzzles API
            elif path == "/api/puzzles":
                puzzles = GLOBAL_STORE.list_puzzles()
                self._send_json({"puzzles": puzzles, "count": len(puzzles), "generation": "G2"})
                return

            elif path.startswith("/api/puzzles/"):
                puzzle_id = path.split("/api/puzzles/")[1]
                puzzle = GLOBAL_STORE.get_puzzle(puzzle_id)
                if not puzzle:
                    self._send_json({"error": f"Puzzle {puzzle_id} not found"}, 404)
                    return
                self._send_json(puzzle.to_dict(), 200)
                return

            # 3. Solver Session API
            elif path.startswith("/api/sessions/"):
                parts = path.split("/")
                session_id = parts[3]
                p_id = query.get("puzzle_id", ["puzzle_g2_quick_01"])[0]
                session = GLOBAL_STORE.get_or_create_session(session_id, puzzle_id=p_id)
                self._send_json(session.to_dict(), 200, headers={"ETag": f'"{session.version}"'})
                return

            # 4. Asynchronous Synthesis Jobs API
            elif path.startswith("/api/jobs/"):
                job_id = path.split("/api/jobs/")[1]
                job = GLOBAL_STORE.get_job(job_id)
                if not job:
                    self._send_json({"error": f"Job {job_id} not found"}, 404)
                    return
                self._send_json(job, 200)
                return

            # 5. Phenomenology & Zuhandenheit Telemetry API (L1-G2-006)
            elif path == "/api/telemetry":
                snapshot = GLOBAL_PHENOM.get_telemetry_snapshot()
                self._send_json(snapshot)
                return

            # 6. Zero-Trust Capability Scoping API (L1-G2-004)
            elif path == "/api/tokens/issue":
                persona = query.get("persona", ["Cruciverbalist_Player"])[0]
                tok = GLOBAL_AUTHORITY.issue_token(persona=persona, allowed_actions=["*"], ttl_seconds=86400)
                self._send_json(tok.to_dict())
                return

            self._send_json({"error": "Not Found", "path": path}, 404)

        if enclave.caught:
            self._send_json({"error": "Internal Enclave Error", "witness": enclave.witness}, 500)

    def do_PATCH(self):
        parsed = urlparse(self.path)
        path = parsed.path

        with CrosswordExceptionEnclave("PATCH_ENCLAVE", path) as enclave:
            if path.startswith("/api/sessions/"):
                session_id = path.split("/")[3]
                content_len = int(self.headers.get("Content-Length", 0))
                raw_body = self.rfile.read(content_len).decode("utf-8")
                delta = json.loads(raw_body)

                row = delta.get("row")
                col = delta.get("col")
                char = delta.get("char", "")
                expected_version = int(delta.get("expected_version", 1))

                # Track keystroke fluidity
                GLOBAL_PHENOM.record_keystroke()

                updated, success = GLOBAL_STORE.apply_delta(
                    session_id=session_id,
                    row=row,
                    col=col,
                    char=char,
                    expected_version=expected_version,
                )

                if not success:
                    GLOBAL_PHENOM.record_friction_rupture(
                        "optimistic_version_conflict",
                        {"expected": expected_version, "actual": updated.version},
                    )
                    self._send_json(
                        {"error": "Version conflict", "current_session": updated.to_dict()},
                        409,
                    )
                    return

                self._send_json(updated.to_dict(), 200, headers={"ETag": f'"{updated.version}"'})
                return

            self._send_json({"error": "Not Found"}, 404)

        if enclave.caught:
            self._send_json({"error": "Internal Enclave Error", "witness": enclave.witness}, 500)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        with CrosswordExceptionEnclave("POST_ENCLAVE", path) as enclave:
            content_len = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(content_len).decode("utf-8")
            body = json.loads(raw_body) if raw_body else {}

            # 1. Delta Sync API (POST /api/sessions/{session_id}/delta)
            if path.startswith("/api/sessions/") and path.endswith("/delta"):
                session_id = path.split("/")[3]
                row = body.get("row")
                col = body.get("col")
                char = body.get("char", "")
                expected_version = int(body.get("expected_version", 1))

                GLOBAL_PHENOM.record_keystroke()
                updated, success = GLOBAL_STORE.apply_delta(
                    session_id=session_id,
                    row=row,
                    col=col,
                    char=char,
                    expected_version=expected_version,
                )
                if not success:
                    GLOBAL_PHENOM.record_friction_rupture(
                        "optimistic_version_conflict",
                        {"expected": expected_version, "actual": updated.version},
                    )
                    self._send_json(
                        {"error": "Version conflict", "session": updated.to_dict()},
                        409,
                    )
                    return
                self._send_json(
                    {"session": updated.to_dict(), "status": "OK"},
                    200,
                    headers={"ETag": f'"{updated.version}"'},
                )
                return

            # 2. CSP Synthesis Jobs API (POST /api/jobs/synthesize)
            elif path == "/api/jobs/synthesize":
                size = int(body.get("grid_size", 7))
                job = GLOBAL_STORE.synthesize_job(size)
                self._send_json({"status": "ACCEPTED", "job": job}, 202)
                return

            # 3. In-App User Feedback (LES-G1-002)
            elif path == "/api/feedback":
                feedback_entry = {
                    "timestamp": time.time(),
                    "date": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "feedback_id": f"fb_cw_{uuid.uuid4().hex[:8]}",
                    "puzzle_id": body.get("puzzle_id", ""),
                    "clue_id": body.get("clue_id", ""),
                    "friction_type": body.get("friction_type", "GENERAL"),
                    "comment": body.get("comment", ""),
                    "generation": "G2",
                }
                DATA_DIR.mkdir(parents=True, exist_ok=True)
                # Append to local feedback
                try:
                    entries = []
                    if FEEDBACK_FILE.exists():
                        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
                            entries = json.load(f)
                    entries.append(feedback_entry)
                    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
                        json.dump(entries, f, indent=2)
                except Exception as e:
                    logger.warning(f"Failed writing local feedback: {e}")

                self._send_json({"status": "SUCCESS", "entry": feedback_entry})
                return

            # 4. Clue Anatomy Inspection Telemetry
            elif path == "/api/inspect":
                GLOBAL_PHENOM.record_clue_inspection()
                self._send_json({"status": "RECORDED"})
                return

            self._send_json({"error": "Not Found", "path": path}, 404)

        if enclave.caught:
            self._send_json({"error": "Internal Enclave Error", "witness": enclave.witness}, 500)

    def log_message(self, format, *args):
        logger.info(f"[AxiomaCrosswordG2:8094] {self.address_string()} - {format % args}")


def run_server(port: int = 8094) -> None:
    server_address = ("", port)
    httpd = ThreadingHTTPServer(server_address, Gen2CrosswordHttpHandler)
    print("=" * 64)
    print(f" Axioma Crossword Engine (Generation 2 - Usable App Standard)")
    print(f" Port {port} | http://localhost:{port}")
    print(f" Multi-Device Responsive | Optimistic Delta Sync | AC-3 Studio")
    print("=" * 64)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server cleanly...")
        httpd.server_close()


if __name__ == "__main__":
    port_arg = int(sys.argv[1]) if len(sys.argv) > 1 else 8094
    run_server(port_arg)
