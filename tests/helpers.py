import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "fixtures"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from qa_tools.common import load_json  # noqa: E402

_VALID_SUITE = load_json(FIXTURES / "valid" / "test-suite.json")
_VALID_ANALYSIS = load_json(FIXTURES / "valid" / "input-analysis.json")


def valid_suite() -> dict:
    return copy.deepcopy(_VALID_SUITE)


def valid_analysis() -> dict:
    return copy.deepcopy(_VALID_ANALYSIS)
