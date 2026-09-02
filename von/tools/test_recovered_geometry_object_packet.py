#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_object_packet.c"

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "object-packet.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_geometry_object_packet_prefix
    build.restype = ctypes.c_uint32
    build.argtypes = [
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32),
    ]

    base = (ctypes.c_uint32 * 3)(0x0000B6D0, 0x00004C4C, 0x0000BB8B)
    packet = (ctypes.c_uint32 * 10)()
    assert build(base, 0x6C, 0x17, 0xFFFFFF80, packet) == 10
    assert list(packet) == [
        0x2F, 0xB6D0, 0x4C4C, 0xBB8B,
        0x16, 0x6C, 0x15, 0x17, 0x14, 0xFFFFFF80,
    ]

    extended = lib.recovered_geometry_object_packet_transform_prefix
    extended.restype = ctypes.c_uint32
    extended.argtypes = [
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
        ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32),
    ]
    packet16 = (ctypes.c_uint32 * 16)()
    assert extended(base, 0x6C, 0x17, 0xFFFFFF80, 0, 0, 0x0FEC, packet16) == 16
    assert list(packet16) == list(packet) + [0x15, 0, 0x14, 0, 0x3A, 0x0FEC]

    status = lib.recovered_geometry_object_packet_status_request
    status.restype = ctypes.c_uint32
    status.argtypes = [
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32),
    ]
    packet11 = (ctypes.c_uint32 * 11)()
    assert status(base, 0x6C, 0x17, 0xFFFFFF80, packet11) == 11
    assert list(packet11) == list(packet) + [0x20]

    length = lib.recovered_geometry_object_length_request
    length.restype = ctypes.c_uint32
    length.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)]
    endpoints = (ctypes.c_uint32 * 6)(0, 0xBEDDB3E1, 0, 0, 0, 0xBE800000)
    packet7 = (ctypes.c_uint32 * 7)()
    assert length(endpoints, packet7) == 7
    assert list(packet7) == [0x1F, 0, 0xBEDDB3E1, 0, 0, 0, 0xBE800000]

    profile_length = lib.recovered_geometry_object_profile_length_request
    profile_length.restype = ctypes.c_uint32
    profile_length.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)]
    profile_vector = (ctypes.c_uint32 * 3)(0xBEDDB3E1, 0xBF5DB3D0, 0xBE800000)
    profile_packet = (ctypes.c_uint32 * 7)()
    assert profile_length(profile_vector, profile_packet) == 7
    assert list(profile_packet) == [0x1F, 0, 0xBEDDB3E1, 0, 0, 0, 0xBE800000]

    scalar = lib.recovered_geometry_object_scalar_request
    scalar.restype = ctypes.c_uint32
    scalar.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
    packet3 = (ctypes.c_uint32 * 3)()
    assert scalar(0x3F000004, 0xBF5DB3D0, packet3) == 3
    assert list(packet3) == [0x0A, 0x3F000004, 0xBF5DB3D0]
    assert scalar(0x3F000003, 0xBF5DB3D0, packet3) == 3
    assert list(packet3) == [0x0A, 0x3F000003, 0xBF5DB3D0]

    xz_output = lib.recovered_geometry_object_xz_state_output_request
    xz_output.restype = ctypes.c_uint32
    xz_output.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)]
    selected = (ctypes.c_uint32 * 3)(0x4124FFFF, 0x40AA9FFF, 0xC23DB800)
    xz_packet = (ctypes.c_uint32 * 4)()
    assert xz_output(selected, xz_packet) == 4
    assert list(xz_packet) == [26, 0x4124FFFF, 0, 0xC23DB800]

    descriptor_copy = lib.recovered_geometry_descriptor_parameter_copy
    descriptor_copy.argtypes = [
        ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
    ]
    descriptor = (ctypes.c_uint32 * (0x68C // 4))(*([0xDEADBEEF] * (0x68C // 4)))
    descriptor[0x67C // 4] = 0x11111111
    descriptor[0x680 // 4] = 0x22222222
    descriptor[0x684 // 4] = 0x33333333
    descriptor[0x688 // 4] = 0x44444444
    related = (ctypes.c_uint32 * (0x64 // 4))(*([0xA5A5A5A5] * (0x64 // 4)))
    descriptor_copy(descriptor, related)
    assert [related[index] for index in (0x54 // 4, 0x58 // 4, 0x5C // 4, 0x60 // 4)] == [
        0x11111111, 0x22222222, 0x33333333, 0x44444444,
    ]
    assert related[0x50 // 4] == 0xA5A5A5A5

    copy_response = lib.recovered_geometry_object_response_copy
    copy_response.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)]
    responses = (ctypes.c_uint32 * 3)(0xBED9FFFF, 0x41896FFE, 0xC273C580)
    record = (ctypes.c_uint32 * 11)(*[0xA5A5A5A5] * 11)
    copy_response(responses, record)
    assert list(record[8:11]) == list(responses)
    assert list(record[:8]) == [0xA5A5A5A5] * 8

    state_copy = lib.recovered_geometry_object_state_response_copy
    state_copy.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)]
    state_record = (ctypes.c_uint32 * 11)(*[0x5A5A5A5A] * 11)
    state_copy(responses, state_record)
    assert state_record[8] == responses[0]
    assert state_record[6] == responses[1]
    assert state_record[10] == responses[2]
    assert [state_record[index] for index in (0, 1, 2, 3, 4, 5, 7, 9)] == [0x5A5A5A5A] * 8

    late_copy = lib.recovered_geometry_object_late_response_copy
    late_copy.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)]
    late_record = (ctypes.c_uint32 * 89)(*[0x3C3C3C3C] * 89)
    late_copy(responses, late_record)
    assert [late_record[index] for index in (0x158 // 4, 0x15C // 4, 0x160 // 4)] == list(responses)
    assert [late_record[index] for index in (0, 1, 8, 10, 85)] == [0x3C3C3C3C] * 5

    late_followup_copy = lib.recovered_geometry_object_late_followup_response_copy
    late_followup_copy.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)]
    late_followup_record = (ctypes.c_uint32 * 92)(*[0x6D6D6D6D] * 92)
    late_followup_copy(responses, late_followup_record)
    assert [late_followup_record[index] for index in (0x164 // 4, 0x168 // 4, 0x16C // 4)] == list(responses)
    assert [late_followup_record[index] for index in (0, 1, 2, 86, 88)] == [0x6D6D6D6D] * 5

    select_vector = lib.recovered_geometry_object_select_response_vector
    select_vector.argtypes = [
        ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32),
    ]
    selected_record = (ctypes.c_uint32 * 92)(*[0x7E7E7E7E] * 92)
    selected_record[0x14 // 4:0x20 // 4] = (0x11111111, 0x22222222, 0x33333333)
    selected_record[0x158 // 4:0x160 // 4] = (0x4124FFFF, 0x40AA9FFF)
    selected_record[0x160 // 4] = 0xC23DB800
    selected_record[0x164 // 4:0x16C // 4] = (0xC0777FFE, 0x41427FFE)
    selected_record[0x16C // 4] = 0xC25B8000
    vector = (ctypes.c_uint32 * 3)()
    select_vector(selected_record, 0, vector)
    assert list(vector) == [0x11111111, 0x22222222, 0x33333333]
    select_vector(selected_record, 1, vector)
    assert list(vector) == [0x4124FFFF, 0x40AA9FFF, 0xC23DB800]
    select_vector(selected_record, 2, vector)
    assert list(vector) == [0xC0777FFE, 0x41427FFE, 0xC25B8000]
    select_vector(selected_record, 3, vector)
    assert list(vector) == [0, 0, 0]

    setup = lib.recovered_geometry_object_state_setup
    setup.restype = ctypes.c_uint32
    setup.argtypes = [
        ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32),
    ]
    setup_packet = (ctypes.c_uint32 * 7)()
    assert setup(0, 0x80000000, 0xC2700000, 0x3F800000, setup_packet) == 7
    assert list(setup_packet) == [
        0x10, 0x12, 0, 0x80000000, 0xC2700000, 0x2A, 0x3F800000,
    ]

    bridge = lib.recovered_geometry_object_state_bridge
    bridge.restype = ctypes.c_uint32
    bridge.argtypes = [
        ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint32),
    ]
    next_base = (ctypes.c_uint32 * 3)(0x2FF9, 0x4996, 0xB20C)
    bridge_packet = (ctypes.c_uint32 * 7)()
    assert bridge(0, next_base, bridge_packet) == 7
    assert list(bridge_packet) == [0x15, 0, 0x05, 0x2F, 0x2FF9, 0x4996, 0xB20C]

    affine = lib.recovered_geometry_object_affine_request
    affine.restype = ctypes.c_uint32
    affine.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)]
    affine_inputs = (ctypes.c_uint32 * 3)(0x2F, 0xAFF9, 0xC997)
    affine_packet = (ctypes.c_uint32 * 4)()
    assert affine(affine_inputs, affine_packet) == 4
    assert list(affine_packet) == [0x1A, 0x2F, 0xAFF9, 0xC997]

print("recovered geometry object-packet vectors: ok")
