#!/usr/bin/env python3
"""Sovereign Service Mesh Network Verifier (`verify_mesh_network.py`).

Probes all 5 Generation 4b Sovereign Services over real HTTP sockets,
measures round-trip latency, confirms status, and prints a verified audit table.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request

# ANSI Colors
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def probe_endpoint(name: str, host: str, port: int, path: str = "/health", timeout: float = 1.5) -> dict:
    url = f"http://{host}:{port}{path}"
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "MetaAxiomaVerifier/1.0"})
        # Bypass any ambient HTTP proxies
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(req, timeout=timeout) as resp:
            latency_ms = (time.time() - t0) * 1000.0
            data = resp.read()
            status_code = resp.status
            try:
                parsed = json.loads(data.decode("utf-8"))
            except Exception:
                parsed = {}
            return {
                "name": name,
                "url": url,
                "host": host,
                "port": port,
                "status": "ONLINE",
                "http_code": status_code,
                "latency_ms": latency_ms,
                "payload": parsed,
                "error": None,
            }
    except Exception as e:
        latency_ms = (time.time() - t0) * 1000.0
        return {
            "name": name,
            "url": url,
            "host": host,
            "port": port,
            "status": "OFFLINE",
            "http_code": 0,
            "latency_ms": latency_ms,
            "payload": {},
            "error": str(e),
        }


def main():
    parser = argparse.ArgumentParser(description="Verify Meta-Axioma Generation 4b Sovereign Mesh Network")
    parser.add_argument("--mode", choices=["auto", "native", "local"], default="auto")
    args = parser.parse_args()

    # Determine probe targets
    # Native targets
    native_endpoints = [
        ("Sovereign Research", "192.168.40.10", 8440, "/health"),
        ("Sovereign Builder", "192.168.40.20", 8442, "/health"),
        ("Sovereign Audit", "192.168.40.30", 8444, "/health"),
        ("Sovereign Telemetry (Ingest)", "192.168.40.40", 8446, "/api/v1/telemetry/health"),
        ("Sovereign Telemetry (Cockpit)", "192.168.40.40", 8447, "/healthz"),
        ("Sovereign Governance", "192.168.40.50", 8448, "/health"),
    ]

    # Local fallback targets
    local_endpoints = [
        ("Sovereign Research", "127.0.0.1", 8440, "/health"),
        ("Sovereign Builder", "127.0.0.1", 8442, "/health"),
        ("Sovereign Audit", "127.0.0.1", 8444, "/health"),
        ("Sovereign Telemetry (Ingest)", "127.0.0.1", 8446, "/api/v1/telemetry/health"),
        ("Sovereign Telemetry (Cockpit)", "127.0.0.1", 8447, "/healthz"),
        ("Sovereign Governance", "127.0.0.1", 8448, "/health"),
    ]

    endpoints_to_test = native_endpoints
    if args.mode == "local":
        endpoints_to_test = local_endpoints
    elif args.mode == "auto":
        # Test first native endpoint to see if native subnet is active
        quick_test = probe_endpoint("Probe", "192.168.40.40", 8447, "/healthz", timeout=0.3)
        if quick_test["status"] != "ONLINE":
            # If native isn't up, test local
            quick_local = probe_endpoint("ProbeLocal", "127.0.0.1", 8447, "/healthz", timeout=0.3)
            if quick_local["status"] == "ONLINE":
                endpoints_to_test = local_endpoints

    print("\n" + "=" * 90)
    print(f"{BOLD}META-AXIOMA GENERATION 4b: LIVE SOVEREIGN MESH NETWORK VERIFIER{RESET}")
    print("=" * 90)
    print(f"{'SERVICE NAME':<30} | {'INTERFACE':<22} | {'STATUS':<10} | {'LATENCY':<10} | {'HTTP'}")
    print("-" * 90)

    online_count = 0
    total_count = len(endpoints_to_test)

    for name, host, port, path in endpoints_to_test:
        res = probe_endpoint(name, host, port, path)
        if res["status"] == "ONLINE":
            online_count += 1
            status_str = f"{GREEN}{BOLD}ONLINE{RESET}"
            lat_str = f"{res['latency_ms']:.2f}ms"
            http_str = f"{GREEN}{res['http_code']}{RESET}"
        else:
            status_str = f"{RED}{BOLD}OFFLINE{RESET}"
            lat_str = "--"
            http_str = f"{RED}ERR{RESET}"

        iface_str = f"{host}:{port}"
        print(f"{name:<30} | {iface_str:<22} | {status_str:<19} | {lat_str:<10} | {http_str}")

    print("=" * 90)
    if online_count == total_count:
        print(f"{GREEN}{BOLD}[PASS] 100% Sovereign Enclaves Operational ({online_count}/{total_count} Nodes Verified){RESET}\n")
        sys.exit(0)
    elif online_count > 0:
        print(f"{YELLOW}{BOLD}[PARTIAL] {online_count}/{total_count} Nodes Reachable.{RESET}")
        print("Note: To launch the full mesh, run:")
        print("  python3 scripts/run_sovereign_mesh.py\n")
        sys.exit(0)
    else:
        print(f"{RED}{BOLD}[OFFLINE] No active mesh detected.{RESET}")
        print("To start the sovereign cluster, run in a separate terminal:")
        print("  python3 scripts/run_sovereign_mesh.py\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
