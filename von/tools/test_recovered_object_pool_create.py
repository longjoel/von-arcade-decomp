#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_object_pool_create.c"

class Slot(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_uint8), ("input_byte_01", ctypes.c_uint8),
        ("input_byte_02", ctypes.c_uint8), ("reserved_03", ctypes.c_uint8),
        ("lookup_halfword", ctypes.c_int16), ("sequence", ctypes.c_int16),
        ("auxiliary_halfword", ctypes.c_int16),
        ("input_halfword_06", ctypes.c_int16),
        ("input_halfword_08", ctypes.c_int16),
        ("source_handle", ctypes.c_uint16),
        ("value_10", ctypes.c_uint32), ("value_14", ctypes.c_uint32),
        ("value_18", ctypes.c_uint32), ("work_1c", ctypes.c_uint32),
        ("work_20", ctypes.c_uint32), ("work_24", ctypes.c_uint32),
        ("derived_value", ctypes.c_uint32),
    ]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "object-pool.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(source)], check=True)
    lib = ctypes.CDLL(str(library))
    function = lib.recovered_object_pool_create
    function.argtypes = [
        ctypes.POINTER(Slot), ctypes.POINTER(Slot), ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint8),
        ctypes.POINTER(ctypes.c_int16), ctypes.POINTER(ctypes.c_uint16),
        ctypes.c_int16,
    ]
    pool = (Slot * 37)()
    for slot in pool:
        slot.lookup_halfword = 1
    pool[4].lookup_halfword = 0
    input_slot = Slot(type=3, input_byte_01=0x22, input_halfword_06=0x1234,
                      input_halfword_08=0x5678, value_10=1, value_14=2, value_18=3)
    mode_table = (ctypes.c_uint32 * (256 * 8))()
    mode_table[3 * 8 + 6] = 0xfeedface
    class_table = (ctypes.c_uint8 * (256 * 8))()
    class_table[3 * 8 + 6] = 0x07
    halfwords = (ctypes.c_int16 * 256)()
    halfwords[3] = 0x2468
    counter = ctypes.c_uint16(9)
    index = function(pool, ctypes.byref(input_slot), 6, mode_table, class_table,
                     halfwords, ctypes.byref(counter), -12)
    assert index == 4
    assert pool[4].type == 7
    assert pool[4].input_byte_01 == 3
    assert pool[4].input_byte_02 == 0x22
    assert (pool[4].value_10, pool[4].value_14, pool[4].value_18) == (1, 2, 3)
    assert pool[4].derived_value == 0xfeedface
    assert pool[4].lookup_halfword == 0x2468
    assert pool[4].auxiliary_halfword == -12
    assert (pool[4].input_halfword_06, pool[4].input_halfword_08) == (0x1234, 0x5678)
    assert pool[4].sequence == 9 and counter.value == 10
    assert (pool[4].work_1c, pool[4].work_20, pool[4].work_24) == (0, 0, 0)

    assert function(pool, ctypes.byref(input_slot), 6, mode_table, class_table,
                    halfwords, ctypes.byref(counter), 0) == -1

    variant = lib.recovered_object_pool_create_constant
    variant.argtypes = [
        ctypes.POINTER(Slot), ctypes.POINTER(Slot), ctypes.c_uint32,
        ctypes.c_uint32, ctypes.POINTER(ctypes.c_int16),
        ctypes.POINTER(ctypes.c_uint16),
    ]
    pool[2].lookup_halfword = 0
    old_byte = pool[2].input_byte_01
    counter.value = 20
    assert variant(pool, ctypes.byref(input_slot), 0x107, 0x3f4ccccd,
                   halfwords, ctypes.byref(counter)) == 2
    assert pool[2].type == 7
    assert pool[2].derived_value == 0x3f4ccccd
    assert pool[2].lookup_halfword == halfwords[0x07]
    assert pool[2].input_halfword_08 == 0x5678
    assert pool[2].input_byte_01 == old_byte
    assert pool[2].sequence == 20 and counter.value == 21

    rebased = lib.recovered_object_pool_create_rebased
    rebased.argtypes = [
        ctypes.POINTER(Slot), ctypes.POINTER(Slot), ctypes.c_uint32,
        ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(ctypes.c_int16),
        ctypes.POINTER(ctypes.c_uint16), ctypes.c_int16,
    ]
    pool[1].lookup_halfword = 0
    input_slot.work_1c = 0x12345678
    mode_table[5 * 8 + 1] = 0xaabbccdd
    class_table[1 * 8 + 5] = 9
    halfwords[9] = 0x1357
    counter.value = 30
    assert rebased(pool, ctypes.byref(input_slot), 5, 1, mode_table, class_table,
                   halfwords, ctypes.byref(counter), 0x4321) == 1
    assert (pool[1].value_10, pool[1].value_14, pool[1].value_18) == (2, 3, 0x12345678)
    assert pool[1].derived_value == 0xaabbccdd
    assert pool[1].type == 9 and pool[1].lookup_halfword == 0x1357
    assert pool[1].source_handle == 0x5678
    assert pool[1].sequence == 30 and counter.value == 31

    Handler = ctypes.CFUNCTYPE(None, ctypes.POINTER(Slot))
    seen = []
    callbacks = {}
    for type_code in (2, 7):
        def record(slot, type_code=type_code):
            seen.append((type_code, slot.contents.sequence))
        callbacks[type_code] = Handler(record)
    handlers = (Handler * 256)()
    handlers[2] = callbacks[2]
    handlers[7] = callbacks[7]
    for slot in pool:
        slot.lookup_halfword = 0
    pool[0].lookup_halfword = 1
    pool[0].type = 2
    pool[0].sequence = 40
    pool[1].lookup_halfword = 1
    pool[1].type = 7
    pool[3].lookup_halfword = 1
    pool[3].type = 61
    pool[4].lookup_halfword = 0
    pool[5].lookup_halfword = -1
    dispatch = lib.recovered_object_pool_dispatch
    dispatch.argtypes = [ctypes.POINTER(Slot), ctypes.POINTER(Handler)]
    dispatch.restype = ctypes.c_uint32
    assert dispatch(pool, handlers) == 2
    assert (2, 40) in seen
    assert (7, 30) in seen

    reset = lib.recovered_object_pool_reset
    reset.argtypes = [ctypes.POINTER(Slot), ctypes.POINTER(ctypes.c_uint32)]
    side_table = (ctypes.c_uint32 * 8)(*[0] * 8)
    reset(pool, side_table)
    assert all(slot.lookup_halfword == -1 and slot.type == 0 for slot in pool)
    assert list(side_table) == [0xffffffff] * 8

print("recovered object-pool create vectors: ok")
