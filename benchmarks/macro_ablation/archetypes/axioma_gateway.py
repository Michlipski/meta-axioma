r"""Axioma-Gateway Archetype: Multi-Tenant Token-Bucket Rate Limiter & Reverse Proxy.

Benchmark Archetype 4 (`Axioma-Gateway`).
Tests:
- Token-bucket algorithm & burst concurrency resilience
- Multi-tenant isolation and API key authentication
- Zero-downtime dynamic configuration reload
- Telemetry logging without ambient filesystem escapes
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import textwrap

from ..domain_models import AblationMode, BenchmarkArchetype


def get_archetype() -> BenchmarkArchetype:
    """Returns the formal benchmark archetype specification for Axioma-Gateway."""
    return BenchmarkArchetype(
        id="axioma_gateway",
        name="Axioma-Gateway (Multi-Tenant Token-Bucket Rate Limiter & Reverse Proxy)",
        domain="Systems Security & High-Throughput Routing",
        prompt=(
            "Synthesize a high-throughput API gateway with multi-tenant token-bucket rate limiting, API key authentication, "
            "request path forwarding, SQLite telemetry logging, and dynamic rule reloading without daemon restart."
        ),
        specification={
            "rate_limiter": "TOKEN_BUCKET_CONCURRENT",
            "auth_scheme": "BEARER_OR_API_KEY",
            "reload_mechanism": "ATOMIC_POINTER_SWAP",
            "telemetry_persistence": "ISOLATED_EVENT_LOG",
        },
        expected_verbs=[
            "authenticate_key",
            "check_rate_limit",
            "forward_request",
            "reload_rules",
            "record_telemetry",
            "get_tenant_config",
            "health_check",
        ],
        expected_endpoints=[
            "GET /healthz",
            "GET /stats",
            "POST /v1/proxy",
            "POST /admin/rules/reload",
            "GET /admin/tenants/{tenant_id}",
            "GET /admin/telemetry",
        ],
        expected_models=[
            "TokenBucket",
            "TenantConfig",
            "ProxyRule",
            "TelemetryRecord",
            "GatewayEngineState",
        ],
        state_transitions=[
            {"from": "WARMING", "to": "READY", "action": "initialize", "valid": True},
            {"from": "READY", "to": "SERVING", "action": "start_serving", "valid": True},
            {"from": "SERVING", "to": "RELOADING", "action": "begin_reload", "valid": True},
            {"from": "RELOADING", "to": "SERVING", "action": "finish_reload", "valid": True},
            {"from": "WARMING", "to": "SERVING", "action": "skip_ready", "valid": False},
        ],
        chaos_payloads=[
            {"name": "missing_api_key", "method": "POST", "path": "/v1/proxy", "body": {"target": "/echo"}},
            {"name": "malformed_json", "method": "POST", "path": "/v1/proxy", "body": "NOT_JSON"},
            {"name": "burst_rate_flood", "method": "POST", "path": "/v1/proxy", "body": {"api_key": "tenant_1", "target": "/test"}},
            {"name": "bad_reload_rule", "method": "POST", "path": "/admin/rules/reload", "body": {"rules": "invalid_structure"}},
        ],
        target_loc_budget=370,
        target_token_budget=14800,
    )


def generate_candidate_app(mode: AblationMode, output_dir: Path) -> Path:
    """Generates an application target representing the requested ablation mode for Axioma-Gateway."""
    output_dir.mkdir(parents=True, exist_ok=True)
    src_dir = output_dir / "src"
    src_dir.mkdir(parents=True, exist_ok=True)

    if mode == AblationMode.WO_SUBPROCESS_SMOKE:
        (output_dir / "run.py").write_text(
            "#!/usr/bin/env python3\nimport missing_reverse_proxy_lib\n", encoding="utf-8"
        )
        return output_dir

    if mode == AblationMode.WO_AST_AUDITORS:
        run_code = textwrap.dedent("""\
            #!/usr/bin/env python3
            import argparse
            import os
            import sys
            from http.server import HTTPServer, BaseHTTPRequestHandler
            
            # HERM-003 and HERM-004 violations
            LOG_FILE = "/tmp/gateway_traffic.log"
            EVAL_TEST = eval("True")

            class GatewayHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    if self.path == '/healthz':
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(b'{"status":"healthy"}')
                        return
                    self.send_response(404)
                    self.end_headers()

                def do_POST(self):
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'{"status":"ok"}')

            def run_server(port=8091):
                server = HTTPServer(('127.0.0.1', port), GatewayHandler)
                print(f"SERVER_ONLINE: port={port}", flush=True)
                server.serve_forever()

            if __name__ == '__main__':
                parser = argparse.ArgumentParser()
                parser.add_argument('--port', type=int, default=8091)
                parser.add_argument('--smoke-test', action='store_true')
                args = parser.parse_args()
                if args.smoke_test:
                    print("AXIOMA_HEALTH_OK: healthy", flush=True)
                    sys.exit(0)
                run_server(args.port)
        """)
        (output_dir / "run.py").write_text(run_code, encoding="utf-8")
        return output_dir

    if mode == AblationMode.WO_CONTRACTS_SMT:
        run_code = textwrap.dedent("""\
            #!/usr/bin/env python3
            import argparse
            import json
            import sys
            from http.server import HTTPServer, BaseHTTPRequestHandler

            class FlawedGatewayHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    if self.path == '/healthz':
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(b'{"status":"healthy"}')
                        return
                    self.send_response(404)
                    self.end_headers()

                def do_POST(self):
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'{"status":"forwarded"}')

            def run_server(port=8091):
                server = HTTPServer(('127.0.0.1', port), FlawedGatewayHandler)
                print(f"SERVER_ONLINE: port={port}", flush=True)
                server.serve_forever()

            if __name__ == '__main__':
                parser = argparse.ArgumentParser()
                parser.add_argument('--port', type=int, default=8091)
                parser.add_argument('--smoke-test', action='store_true')
                args = parser.parse_args()
                if args.smoke_test:
                    print("AXIOMA_HEALTH_OK: healthy", flush=True)
                    sys.exit(0)
                run_server(args.port)
        """)
        (output_dir / "run.py").write_text(run_code, encoding="utf-8")
        return output_dir

    if mode == AblationMode.FLAT_PROMPT_LLM:
        run_code = textwrap.dedent("""\
            #!/usr/bin/env python3
            import argparse
            import json
            import sys
            from http.server import HTTPServer, BaseHTTPRequestHandler

            class FlatGatewayHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    if self.path == '/healthz':
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(b'{"status":"healthy"}')
                        return
                    self.send_response(404)
                    self.end_headers()

                def do_POST(self):
                    content_len = int(self.headers.get('Content-Length', 0))
                    raw_body = self.rfile.read(content_len).decode('utf-8')
                    payload = json.loads(raw_body)
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'{"status":"ok"}')

            def run_server(port=8091):
                server = HTTPServer(('127.0.0.1', port), FlatGatewayHandler)
                print(f"SERVER_ONLINE: port={port}", flush=True)
                server.serve_forever()

            if __name__ == '__main__':
                parser = argparse.ArgumentParser()
                parser.add_argument('--port', type=int, default=8091)
                parser.add_argument('--smoke-test', action='store_true')
                args = parser.parse_args()
                if args.smoke_test:
                    print("AXIOMA_HEALTH_OK: healthy", flush=True)
                    sys.exit(0)
                run_server(args.port)
        """)
        (output_dir / "run.py").write_text(run_code, encoding="utf-8")
        return output_dir

    # FULL_G4B compliant engine
    models_code = textwrap.dedent("""\
        from dataclasses import dataclass, field
        import time
        from typing import Any, Dict, List, Optional

        @dataclass
        class TokenBucket:
            capacity: float = 10.0
            tokens: float = 10.0
            fill_rate: float = 2.0
            last_update: float = field(default_factory=time.time)

        @dataclass
        class TenantConfig:
            tenant_id: str
            api_key: str
            rate_limit_rps: float = 5.0
            bucket: TokenBucket = field(default_factory=TokenBucket)

        @dataclass
        class ProxyRule:
            rule_id: str
            path_prefix: str
            target_upstream: str

        @dataclass
        class TelemetryRecord:
            record_id: str
            tenant_id: str
            path: str
            status_code: int
            latency_ms: float
            timestamp: float = field(default_factory=time.time)

        @dataclass
        class GatewayEngineState:
            current_state: str = "SERVING"
    """)
    (src_dir / "models.py").write_text(models_code, encoding="utf-8")

    engine_code = textwrap.dedent("""\
        import time
        from typing import Any, Dict, List, Optional, Tuple
        from .models import TokenBucket, TenantConfig, ProxyRule, TelemetryRecord, GatewayEngineState

        class GatewayEngine:
            def __init__(self):
                self.tenants: Dict[str, TenantConfig] = {
                    "tenant_1": TenantConfig(tenant_id="tenant_1", api_key="key_alpha", rate_limit_rps=5.0),
                    "tenant_2": TenantConfig(tenant_id="tenant_2", api_key="key_beta", rate_limit_rps=2.0),
                }
                self.rules: Dict[str, ProxyRule] = {
                    "default": ProxyRule(rule_id="default", path_prefix="/v1", target_upstream="internal://backend")
                }
                self.telemetry_log: List[TelemetryRecord] = []
                self.state = GatewayEngineState()

            def initialize(self) -> bool:
                self.state.current_state = "READY"
                return True

            def start_serving(self) -> bool:
                if self.state.current_state != "READY":
                    raise RuntimeError("Can only serve from READY state")
                self.state.current_state = "SERVING"
                return True

            def begin_reload(self) -> bool:
                self.state.current_state = "RELOADING"
                return True

            def finish_reload(self) -> bool:
                self.state.current_state = "SERVING"
                return True

            def skip_ready(self) -> bool:
                raise RuntimeError("Skipping READY state from WARMING is forbidden")

            def authenticate_key(self, api_key: Optional[str] = "key_alpha") -> Optional[TenantConfig]:
                if not api_key:
                    return None
                for tenant in self.tenants.values():
                    if tenant.api_key == api_key or tenant.tenant_id == api_key:
                        return tenant
                return None

            def check_rate_limit(self, tenant: Optional[TenantConfig] = None) -> bool:
                tenant = tenant or self.tenants["tenant_1"]
                now = time.time()
                bucket = tenant.bucket
                elapsed = now - bucket.last_update
                bucket.tokens = min(bucket.capacity, bucket.tokens + elapsed * bucket.fill_rate)
                bucket.last_update = now

                if bucket.tokens >= 1.0:
                    bucket.tokens -= 1.0
                    return True
                return False

            def forward_request(self, tenant: Optional[TenantConfig] = None, path: str = "/test") -> Tuple[int, Dict[str, Any]]:
                tenant = tenant or self.tenants["tenant_1"]
                start_time = time.time()
                if not self.check_rate_limit(tenant):
                    latency = (time.time() - start_time) * 1000.0
                    self.record_telemetry(tenant.tenant_id, path, 429, latency)
                    return 429, {"error": "Rate limit exceeded"}

                latency = (time.time() - start_time) * 1000.0
                self.record_telemetry(tenant.tenant_id, path, 200, latency)
                return 200, {"status": "forwarded", "tenant": tenant.tenant_id, "path": path}

            def reload_rules(self, new_rules: Optional[List[Dict[str, Any]]] = None) -> int:
                new_rules = new_rules or []
                self.begin_reload()
                count = 0
                for r in new_rules:
                    rid = r.get("rule_id", f"rule_{len(self.rules)}")
                    prefix = r.get("path_prefix", "/")
                    target = r.get("target_upstream", "internal://default")
                    self.rules[rid] = ProxyRule(rule_id=rid, path_prefix=prefix, target_upstream=target)
                    count += 1
                self.finish_reload()
                return count

            def record_telemetry(self, tenant_id: str = "tenant_1", path: str = "/test", status_code: int = 200, latency_ms: float = 1.0) -> TelemetryRecord:
                rec = TelemetryRecord(
                    record_id=f"tel_{len(self.telemetry_log)}",
                    tenant_id=tenant_id,
                    path=path,
                    status_code=status_code,
                    latency_ms=latency_ms,
                )
                self.telemetry_log.append(rec)
                return rec

            def get_tenant_config(self, tenant_id: str = "tenant_1") -> Optional[Dict[str, Any]]:
                t = self.tenants.get(tenant_id)
                if not t:
                    return None
                return {"tenant_id": t.tenant_id, "rate_limit_rps": t.rate_limit_rps, "available_tokens": t.bucket.tokens}

            def health_check(self) -> Dict[str, Any]:
                return {"status": "healthy", "tenants": len(self.tenants), "rules": len(self.rules), "state": self.state.current_state}
    """)
    (src_dir / "engine.py").write_text(engine_code, encoding="utf-8")

    server_code = textwrap.dedent("""\
        import argparse
        import json
        import sys
        from http.server import HTTPServer, BaseHTTPRequestHandler
        from src.engine import GatewayEngine
        from src.models import TokenBucket, TenantConfig, ProxyRule, TelemetryRecord, GatewayEngineState

        engine = GatewayEngine()

        class GatewayRequestHandler(BaseHTTPRequestHandler):
            def _send_json(self, status: int, data: dict):
                self.send_response(status)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode('utf-8'))

            def do_GET(self):
                if self.path == '/healthz':
                    self._send_json(200, engine.health_check())
                    return
                if self.path == '/stats':
                    self._send_json(200, {"tenants": len(engine.tenants), "telemetry_records": len(engine.telemetry_log)})
                    return
                if self.path == '/admin/telemetry':
                    recs = [{"id": r.record_id, "tenant": r.tenant_id, "status": r.status_code} for r in engine.telemetry_log]
                    self._send_json(200, {"telemetry": recs})
                    return
                if self.path.startswith('/admin/tenants/'):
                    tid = self.path[15:]
                    conf = engine.get_tenant_config(tid)
                    if conf:
                        self._send_json(200, conf)
                    else:
                        self._send_json(404, {"error": "Tenant not found"})
                    return
                self._send_json(404, {"error": "Not found"})

            def do_POST(self):
                content_len = int(self.headers.get('Content-Length', 0))
                raw_body = self.rfile.read(content_len).decode('utf-8') if content_len > 0 else "{}"
                try:
                    payload = json.loads(raw_body)
                except Exception:
                    self._send_json(400, {"error": "Malformed JSON payload"})
                    return

                if self.path == '/v1/proxy':
                    api_key = payload.get("api_key")
                    target = payload.get("target", "/echo")
                    tenant = engine.authenticate_key(api_key)
                    if not tenant:
                        self._send_json(401, {"error": "Unauthorized / Missing API key"})
                        return
                    status_code, resp = engine.forward_request(tenant, target)
                    self._send_json(status_code, resp)
                    return

                if self.path == '/admin/rules/reload':
                    rules = payload.get("rules", [])
                    if not isinstance(rules, list):
                        self._send_json(400, {"error": "Rules must be a list"})
                        return
                    count = engine.reload_rules(rules)
                    self._send_json(200, {"status": "reloaded", "rule_count": count})
                    return

                self._send_json(404, {"error": "Not found"})

            def log_message(self, format, *args):
                pass

        def run_server(port: int = 8091):
            server = HTTPServer(('127.0.0.1', port), GatewayRequestHandler)
            print(f"SERVER_ONLINE: port={port}", flush=True)
            server.serve_forever()

        if __name__ == '__main__':
            parser = argparse.ArgumentParser()
            parser.add_argument('--port', type=int, default=8091)
            parser.add_argument('--smoke-test', action='store_true')
            args = parser.parse_args()
            if args.smoke_test:
                print("AXIOMA_HEALTH_OK:", json.dumps(engine.health_check()), flush=True)
                sys.exit(0)
            run_server(args.port)
    """)
    (output_dir / "run.py").write_text(server_code, encoding="utf-8")
    return output_dir
