#!/bin/bash
#
# Runs inside the SHARED environment image (environment/Dockerfile) — canonical TB2 has no
# separate verifier image. pytest is baked into environment/Dockerfile, so do NOT install or
# download anything here — verify-time setup is rejected by the static checks.
#
# Harbor overlays tests/ at /tests only at verify time, so keep ground truth / expected
# outputs in tests/ (never in environment/, where the agent could read them).
# --ctrf writes a standard JSON report; write 1/0 to /logs/verifier/reward.txt.
# This script must always exit 0 — Harbor reads reward.txt for the score.
set -u

mkdir -p /logs/verifier

pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
PYTEST_EXIT=$?

if [ $PYTEST_EXIT -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

exit 0
