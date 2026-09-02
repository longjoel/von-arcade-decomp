#!/usr/bin/env python3
import ctypes
import pathlib
import struct
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_projection.c"


class Record(ctypes.Structure):
    _fields_ = [("unused_0", ctypes.c_uint16), ("unused_1", ctypes.c_uint16)] + [
        (name, ctypes.c_uint32) for name in ("packet_1", "packet_2", "packet_3", "packet_4")
    ]


SENTINEL = 0x47C34F80


def bits(value):
    return struct.unpack("<I", struct.pack("<f", value))[0]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "projection.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
        dll = ctypes.CDLL(str(library))
        build = dll.recovered_geometry_projection_packet
        build.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
            ctypes.POINTER(Record), ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
        ]
        build.restype = ctypes.c_int
        validate = dll.recovered_geometry_projection_validate
        validate.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        validate.restype = ctypes.c_int
        output_mask = dll.recovered_geometry_projection_output_mask
        output_mask.argtypes = [ctypes.c_uint16, ctypes.c_uint32]
        output_mask.restype = ctypes.c_uint16
        result_route = dll.recovered_geometry_projection_result_route
        result_route.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint16,
            ctypes.c_uint16, ctypes.POINTER(ctypes.c_uint32),
        ]
        result_route.restype = ctypes.c_int
        callback_quadrant = dll.recovered_geometry_projection_callback_quadrant
        callback_quadrant.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
        callback_quadrant.restype = ctypes.c_int
        mask_source = dll.recovered_geometry_projection_mask_source
        mask_source.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        mask_source.restype = ctypes.c_uint32
        grid_index = dll.recovered_geometry_projection_grid_index
        grid_index.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_uint32),
        ]
        grid_index.restype = ctypes.c_int
        mask_field = dll.recovered_geometry_projection_mask_field
        mask_field.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        mask_field.restype = ctypes.c_uint32
        mask_field_scaled = dll.recovered_geometry_projection_mask_field_scaled
        mask_field_scaled.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        mask_field_scaled.restype = ctypes.c_uint32
        mask_threshold = dll.recovered_geometry_projection_mask_threshold
        mask_threshold.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
        mask_threshold.restype = ctypes.c_uint32
        mask_threshold_passes = dll.recovered_geometry_projection_mask_threshold_passes
        mask_threshold_passes.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
        mask_threshold_passes.restype = ctypes.c_int

        table = (Record * 3)()
        table[2] = Record(0, 0, 0x11111111, 0x81234567, 0x33333333, 0x44444444)
        request = ctypes.c_uint32()
        packet = (ctypes.c_uint32 * 8)()
        xq = ctypes.c_uint32()
        yq = ctypes.c_uint32()
        x, y = bits(513.75), bits(1023.9)
        assert build(x, y, 2, table, ctypes.byref(request), packet, ctypes.byref(xq), ctypes.byref(yq)) == 1
        assert request.value == (511 << 9) + 256
        assert list(packet) == [53, 0x11111111, x, 0x33333333, y, 0x44444444, 0x44444444, 0x01234567]
        assert (xq.value, yq.value) == (12, 25)

        assert build(bits(-1.0), bits(1.0), 2, table, ctypes.byref(request), packet, ctypes.byref(xq), ctypes.byref(yq)) == 0
        assert build(bits(1024.0), bits(1.0), 2, table, ctypes.byref(request), packet, ctypes.byref(xq), ctypes.byref(yq)) == 0

        result = ctypes.c_uint32()
        threshold = bits(4.0)
        assert validate(bits(10.0), bits(10.0), 0, threshold, ctypes.byref(result)) == 1
        assert validate(bits(10.0), bits(10.1), 0, threshold, ctypes.byref(result)) == 0
        assert result.value == SENTINEL
        assert validate(bits(10.0), bits(-10.0), 1, threshold, ctypes.byref(result)) == 1
        assert validate(bits(10.0), bits(-10.1), 1, threshold, ctypes.byref(result)) == 0
        assert validate(bits(1.0), bits(0.0), 4, threshold, ctypes.byref(result)) == 0
        assert mask_source(0x503AD0, 0) == 0x562C80
        assert mask_source(0x503AD0, 1) == 0x562C80
        assert mask_source(0x1000, 0) == 0
        assert mask_source(0x1000, 1) == 0x562C84
        first_q = ctypes.c_int()
        second_q = ctypes.c_int()
        grid = ctypes.c_uint32()
        assert grid_index(bits(-480.0), bits(-480.0), 9,
                          ctypes.byref(first_q), ctypes.byref(second_q),
                          ctypes.byref(grid)) == 1
        assert (first_q.value, second_q.value, grid.value) == (0, 0, 0)
        assert grid_index(bits(0.0), bits(40.0), 9,
                          ctypes.byref(first_q), ctypes.byref(second_q),
                          ctypes.byref(grid)) == 1
        assert (first_q.value, second_q.value, grid.value) == (12, 13, 49)
        assert grid_index(bits(480.0), bits(80.0), 9,
                          ctypes.byref(first_q), ctypes.byref(second_q),
                          ctypes.byref(grid)) == 1
        assert (first_q.value, second_q.value, grid.value) == (24, 14, 86)
        mask_word = 0xE4A1C39B
        for slot in range(16):
            expected = (mask_word >> (slot * 2)) & 3
            assert mask_field(mask_word, slot) == expected
            assert mask_field_scaled(mask_word, slot) == expected << 14
        assert mask_field(mask_word, 16) == 0
        assert mask_field_scaled(mask_word, 16) == 0
        for slot in range(16):
            field = (mask_word >> (slot * 2)) & 3
            for sample in (0, 0x47ff, 0x4800, 0x8000, 0xffff):
                signed_sample = sample if sample < 0x8000 else sample - 0x10000
                expected = (0x4800 + (field << 14) - signed_sample) & 0xffff
                assert mask_threshold(mask_word, slot, sample) == expected
                assert mask_threshold_passes(mask_word, slot, sample) == (expected <= 0x8fff)
        assert output_mask(0xC000, 15) == 0xC000
        assert output_mask(0x4000, 15) == 0x4000
        assert output_mask(0x8000, 15) == 0x8000
        assert output_mask(0x0001, 1) == 0

        routed = ctypes.c_uint32(0xdeadbeef)
        # The floating result is only the branch condition on this path.
        assert result_route(bits(0.25), 12, 15, 0x1000, 0,
                            0xc000, 0x4000, ctypes.byref(routed)) == 0
        assert routed.value == (12 << 8)
        # The -0.1 helper sentinel selects the special object's mask path.
        assert result_route(0xbdcccccd, 12, 15, 0x503ad0, 0,
                            0xc000, 0x4000, ctypes.byref(routed)) == 1
        assert routed.value == 0xc000
        # With no general mask state, a negative result publishes zero.
        assert result_route(0xbdcccccd, 12, 15, 0x1000, 0,
                            0xc000, 0x4000, ctypes.byref(routed)) == 1
        assert routed.value == 0

        quadrant = ctypes.c_uint32(99)
        for map_byte in range(256):
            eligible = bool(map_byte != 0xff and (map_byte & 0x20))
            assert callback_quadrant(map_byte, ctypes.byref(quadrant)) == eligible
            if eligible:
                assert quadrant.value == (map_byte - 0x20) >> 6

        assert callback_quadrant(0x20, ctypes.byref(quadrant)) == 1
        assert quadrant.value == 0
        assert callback_quadrant(0xe0, ctypes.byref(quadrant)) == 1
        assert quadrant.value == 3

    print("recovered geometry projection packet vectors: ok")


if __name__ == "__main__":
    main()
