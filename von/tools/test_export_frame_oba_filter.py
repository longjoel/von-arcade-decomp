"""--oba filtering keeps model parts by address and fails on absence."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_geometry_frame_textured_gltf import filter_obas


def main():
    objects = [(0x10, "a", {}), (0x20, "b", {}), (0x30, "c", {})]
    slots = [4, 5, 6]
    kept, kept_slots = filter_obas(objects, slots, ["20", "0x10"])
    assert [item[0] for item in kept] == [0x10, 0x20]
    assert list(kept_slots) == [4, 5]
    for raw, fragment in ((["20", "ff"], "missing model obas"),
                          (["zz"], "not hex"), (["ff"], "no model obas")):
        try:
            filter_obas(objects, slots, raw)
        except SystemExit as error:
            assert fragment in str(error), (raw, error)
        else:
            raise AssertionError(f"no failure for {raw}")
    print("PASS: oba filtering")


if __name__ == "__main__":
    main()
