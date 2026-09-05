from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from extract_coprocessor_sources import (  # noqa: E402
    GEOMETRY_OFFSET,
    GEOMETRY_WORDS,
    SHARC_OFFSET,
    SHARC_WORDS,
    extract,
)


ROOT = Path(__file__).parents[1]


def test_upload_windows_match_documented_bounds():
    result = extract(ROOT / "artifacts", ROOT / "build/disasm/vonj-maincpu.bin")
    assert result["sharc"]["offset"] == SHARC_OFFSET
    assert result["sharc"]["words"] == SHARC_WORDS
    assert result["sharc"]["bytes"] == SHARC_WORDS * 2
    assert result["geometry"]["offset"] == GEOMETRY_OFFSET
    assert result["geometry"]["words"] == GEOMETRY_WORDS
    assert result["geometry"]["bytes"] == GEOMETRY_WORDS * 2


def test_upload_windows_are_not_empty():
    result = extract(ROOT / "artifacts", ROOT / "build/disasm/vonj-maincpu.bin")
    assert any(result["payloads"]["sharc"])
    assert any(result["payloads"]["geometry"])

