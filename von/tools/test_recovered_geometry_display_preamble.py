import ctypes
from pathlib import Path
import subprocess
import tempfile


ROOT = Path(__file__).parents[2]


def test_display_preamble_matches_parser_trace():
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "geometry-commands.so"
        subprocess.run([
            "cc", "-shared", "-fPIC", "-O2", "-o", str(library),
            str(ROOT / "von/i960/recovered_geometry_commands.c"),
        ], check=True)
        lib = ctypes.CDLL(str(library))
        function = lib.recovered_geometry_display_preamble
        function.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
        function.restype = ctypes.c_uint32
        output = (ctypes.c_uint32 * 28)()
        assert function(output) == 28
        assert list(output[:9]) == [
            0x0B001616, 0x47800000, 0x03800707, 3,
            0x04000808, 0x41004000, 0x01800303, 0x00000080,
            0x01F40204,
        ]
        assert output[16] == 0x04800909
        assert output[23] == 0x02000404
        assert output[26] == 0x08001010

