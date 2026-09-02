from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-sharc-bootstrap.lst"


def listing():
    result = {}
    for line in LISTING.read_text(encoding="utf-8").splitlines():
        if ":" in line:
            slot, body = line.split(":", 1)
            if len(slot) == 3 and all(c in "0123456789abcdef" for c in slot):
                result[slot] = body
    return result


def require(lines, checks, label):
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"{label} slot {slot} missing {fragment}")
