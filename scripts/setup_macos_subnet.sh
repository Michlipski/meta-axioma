#!/usr/bin/env bash
# ==============================================================================
# Meta-Axioma: macOS Loopback Subnet Configuration Script
# Configures IP aliases for the 192.168.40.0/24 subnet on the loopback interface (lo0).
# This enables real TCP/UDP socket binding and communication on discrete IPs:
#   - 192.168.40.10: Sovereign Research Service
#   - 192.168.40.20: Sovereign Builder Enclave
#   - 192.168.40.30: Sovereign Audit & Formal Verification Service
#   - 192.168.40.40: Sovereign Telemetry & Evaluation Service
#   - 192.168.40.50: Sovereign Governance & Safety Service
# ==============================================================================

set -euo pipefail

echo "======================================================================"
echo "META-AXIOMA: CONFIGURING MACOS 192.168.40.0/24 SUBNET ALIASES"
echo "======================================================================"

if [[ "$OSTYPE" != "darwin"* ]]; then
  echo "Error: This script is intended for macOS (Darwin). On Linux, use docker-compose or 'ip addr add'." >&2
  exit 1
fi

IPS=(
  "192.168.40.10" # Research
  "192.168.40.20" # Builder
  "192.168.40.30" # Audit
  "192.168.40.40" # Telemetry
  "192.168.40.50" # Governance
)

echo "Adding IP aliases to lo0 (requires sudo)..."
for ip in "${IPS[@]}"; do
  if ifconfig lo0 | grep -q "$ip"; then
    echo "  [EXISTS] $ip already aliased on lo0"
  else
    echo "  [ADDING] sudo ifconfig lo0 alias $ip 255.255.255.0"
    sudo ifconfig lo0 alias "$ip" 255.255.255.0
  fi
done

echo ""
echo "Active 192.168.40.X aliases on lo0:"
ifconfig lo0 | grep "192.168.40" || true

echo ""
echo "Testing loopback ping on 192.168.40.10 and 192.168.40.40..."
ping -c 1 192.168.40.10 >/dev/null && echo "  [OK] 192.168.40.10 reachable!"
ping -c 1 192.168.40.40 >/dev/null && echo "  [OK] 192.168.40.40 reachable!"

echo "======================================================================"
echo "SUCCESS: 192.168.40.0/24 subnet is now physically active on macOS."
echo "You can now boot the sovereign mesh with:"
echo "  python3 scripts/run_sovereign_mesh.py"
echo "To tear down when finished, run:"
echo "  ./scripts/teardown_macos_subnet.sh"
echo "======================================================================"
