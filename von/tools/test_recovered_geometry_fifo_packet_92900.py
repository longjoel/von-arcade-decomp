#!/usr/bin/env python3
import ctypes, pathlib, subprocess, tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_fifo_packet_92900.c"

class Plan(ctypes.Structure):
    _fields_ = [("input_word", ctypes.c_uint32 * 3),
                ("projected_word", ctypes.c_uint32),
                ("fifo_word", ctypes.c_uint32 * 12),
                ("fifo_count", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "packet.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    dll = ctypes.CDLL(str(library))
    fn = dll.recovered_geometry_fifo_packet_92900
    fn.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32,
                   ctypes.POINTER(Plan)]
    callers = [
        (0xc089999a, 0x421c6666, 0x40466666, 0x00000000), # 0x96948
        (0x4019999a, 0x4213999a, 0xc059999a, 0xffff8000), # 0x96e04
        (0x40326e98, 0x41e66666, 0x3fcb020c, 0x00007500), # 0x97254
        (0x400947ae, 0x42040000, 0x405374bc, 0xffffae00), # 0x977a4
        (0x40733333, 0x421e6666, 0xbf666666, 0x00007d00), # 0x98ab8
        (0xc059999a, 0x4224cccd, 0x3fe66666, 0x00000d00), # 0x99274
    ]
    plan = Plan()
    for g0, g1, g2, g3 in callers:
        inputs = (ctypes.c_uint32 * 3)(g0, g1, g2)
        fn(inputs, g3, ctypes.byref(plan))
        assert list(plan.fifo_word) == [5, 18, g0, g1, g2, 21,
                                        g3 & 0xffff, 19,
                                        0x3e4ccccd, 0x3e4ccccd,
                                        0x3e4ccccd, 6], hex(g0)
        assert plan.projected_word == g3 & 0xffff
        assert plan.fifo_count == 12
    fn2 = dll.recovered_geometry_fifo_packet_92db0
    fn2.argtypes = fn.argtypes
    fn2(inputs, 0x12345678, ctypes.byref(plan))
    assert plan.projected_word == 0x5678
    class Prefix(ctypes.Structure):
        _fields_ = [("divisor_word", ctypes.c_uint32),
                    ("quotient_source", ctypes.c_uint32),
                    ("quotient_word", ctypes.c_uint32),
                    ("fifo_word", ctypes.c_uint32 * 11),
                    ("fifo_count", ctypes.c_uint32)]
    prefix_fn = dll.recovered_geometry_fifo_packet_92da0_prefix
    prefix_fn.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32,
                          ctypes.c_uint32, ctypes.c_uint32,
                          ctypes.POINTER(Prefix)]
    prefix = Prefix()
    prefix_fn(inputs, 0xffff8500, 37, 1234, ctypes.byref(prefix))
    assert prefix.quotient_word == 33
    assert list(prefix.fifo_word) == [5, 18, *inputs, 21, 0x8500, 19,
                                      0x3e4ccccd, 0x3e4ccccd, 0x3e4ccccd]
    assert prefix.fifo_count == 11
    for g0, g1, g2, g3 in [
        (0x4151999a, 0x420b3333, 0xbfe66666, 0xffff8500), # 0x96ef4
        (0x412b3333, 0x42053333, 0xbe4ccccd, 0xffff8500), # 0x98d4c
        (0x3dcccccd, 0x42040000, 0x4101999a, 0xffffc000), # 0x9966c
    ]:
        caller_inputs = (ctypes.c_uint32 * 3)(g0, g1, g2)
        prefix_fn(caller_inputs, g3, 1, 0, ctypes.byref(prefix))
        assert list(prefix.fifo_word) == [5, 18, g0, g1, g2, 21, g3 & 0xffff,
                                          19, 0x3e4ccccd, 0x3e4ccccd,
                                          0x3e4ccccd]
    class Gate(ctypes.Structure):
        _fields_ = [("divisor_word", ctypes.c_uint32),
                    ("quotient_source", ctypes.c_uint32),
                    ("alternate_source", ctypes.c_uint32),
                    ("remainder", ctypes.c_uint32),
                    ("helper_argument", ctypes.c_uint32),
                    ("helper_target", ctypes.c_uint32),
                    ("table_base", ctypes.c_uint32),
                    ("flag_address", ctypes.c_uint32),
                    ("flag_value", ctypes.c_uint32)]
    gate_fn = dll.recovered_geometry_fifo_helper_gate_929a0
    gate_fn.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(Gate)]
    gate = Gate(); gate_fn(10, 37, 41, 0x5624d0, ctypes.byref(gate))
    assert (gate.remainder, gate.helper_argument, gate.table_base,
            gate.flag_address, gate.flag_value) == (1, 7, 0x2be2a14,
                                                     0x5624d0, 1)
    gate_fn(11, 37, 41, 0x5624d0, ctypes.byref(gate))
    assert (gate.remainder, gate.helper_argument, gate.table_base,
            gate.flag_value) == (2, 8, 0x2be296c, 0)
    twin_fn = dll.recovered_geometry_fifo_helper_gate_92e28
    twin_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                        ctypes.POINTER(Gate)]
    twin_fn(10, 37, 41, ctypes.byref(gate))
    assert (gate.remainder, gate.helper_argument, gate.table_base,
            gate.flag_address, gate.flag_value) == (1, 7, 0x2be2a14,
                                                     0x5624e4, 1)
    twin_fn(11, 37, 41, ctypes.byref(gate))
    assert (gate.remainder, gate.helper_argument, gate.table_base,
            gate.flag_address, gate.flag_value) == (2, 8, 0x2be296c,
                                                     0x5624e4, 0)
    twin_fn(0, 37, 41, ctypes.byref(gate))
    assert (gate.remainder, gate.helper_argument, gate.table_base,
            gate.flag_address, gate.flag_value) == (0, 0, 0x2be2a14,
                                                     0x5624e4, 1)
print("recovered geometry FIFO 0x92900/0x92db0 packet: six fixed callers ok")
