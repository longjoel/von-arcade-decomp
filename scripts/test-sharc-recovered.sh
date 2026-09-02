#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require_command python3

cd "$ROOT_DIR"

mapfile -t TESTS < <(
    find von/tools -maxdepth 1 -type f -name 'test_recovered_sharc_*.py' -print | sort
)

TESTS+=(
    von/tools/test_sharc_service_contract.py
    von/tools/test_sharc_precision_fixtures.py
    von/tools/test_sharc_40bit_reference.py
)

for test_file in "${TESTS[@]}"; do
    python3 "$test_file"
done

printf 'SHARC recovered-model checkpoint passed: %d tests.\n' "${#TESTS[@]}"
