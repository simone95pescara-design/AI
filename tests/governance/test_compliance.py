import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def test_compliance_validator_passes_on_repository():
    result = subprocess.run(
        [sys.executable, str(REPO / "compliance" / "validate.py")],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "COMPLIANCE: PASS" in result.stdout
