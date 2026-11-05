#!/usr/bin/env bash
# ==============================================================================
# Meta-Axioma: macOS Loopback Subnet Teardown Script
# Removes IP aliases for the 192.168.40.0/24 subnet from the loopback interface (lo0).
# ==============================================================================

set -euo pipefail

echo "======================================================================"
echo "META-AXIOMA: REMOVING MACOS 192.168.40.0/24 SUBNET ALIASES"
echo "======================================================================"

IPS=(
  "192.168.40.10"
  "192.168.40.20"
  "192.168.40.30"
  "192.168.40.40"
  "192.168.40.50"
)

for ip in "${IPS[@]}"; do
  if ifconfig lo0 | grep -q "$ip"; then
    echo "  [REMOVING] sudo ifconfig lo0 -alias $ip"
    sudo ifconfig lo0 -alias "$ip" 2>/dev/null || true
  else
    echo "  [SKIPPED] $ip not present on lo0"
  fi
done

echo ""
echo "Remaining aliases on lo0 (if any):"
ifconfig lo0 | grep "192.168.40" || echo "  [CLEAN] No 192.168.40.X aliases remaining."
echo "======================================================================"
