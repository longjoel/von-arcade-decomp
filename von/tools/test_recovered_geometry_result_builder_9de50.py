"""Validate the entry-point contract for the shared 0x9de50 builder."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
source = ROOT / "von/i960/recovered_geometry_result_builder_9de50.c"
library = pathlib.Path(tempfile.mkdtemp()) / "lib.so"
subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(source), "-o", str(library)], check=True)
lib = ctypes.CDLL(str(library))

class Plan(ctypes.Structure):
    _fields_ = [("selector", ctypes.c_uint32), ("selector_stride_bytes", ctypes.c_uint32), ("parameter_table_address", ctypes.c_uint32), ("parameter_halfword_offset", ctypes.c_uint32 * 3), ("request38_address", ctypes.c_uint32), ("request38_word_count", ctypes.c_uint32), ("response_scratch_offset", ctypes.c_uint32), ("paired_record_offset", ctypes.c_uint32 * 3), ("paired_record_mirror_offset", ctypes.c_uint32 * 3), ("flag_offset", ctypes.c_uint32), ("flag_set_delta_request", ctypes.c_uint32), ("flag_clear_fallback_table", ctypes.c_uint32), ("common_request31", ctypes.c_uint32), ("common_request31_word_count", ctypes.c_uint32), ("final_sharc_handler", ctypes.c_uint32), ("final_sharc_parameter_count", ctypes.c_uint32), ("final_host_parameter_count", ctypes.c_uint32), ("final_sharc_output_pc", ctypes.c_uint32), ("final_host_read_pc", ctypes.c_uint32), ("final_host_read_count", ctypes.c_uint32), ("final_output_register", ctypes.c_uint32 * 3), ("final_output_state_offset", ctypes.c_uint32 * 3), ("final_distance_operand_pair", (ctypes.c_uint32 * 2) * 3), ("final_first_output_is_first_host_operand", ctypes.c_uint32), ("final_host_stream_requires_followup_words", ctypes.c_uint32), ("final_flag0_means_input_fifo_empty", ctypes.c_uint32), ("final_response_offset", ctypes.c_uint32)]

class ClearFields(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "output_0c", "output_0e", "output_10", "output_14",
        "mirror_04", "mirror_06", "mirror_08", "mirror_0a", "mirror_1c")]

fn = lib.recovered_geometry_result_builder_9de50_plan
fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]

selector_parameters = lib.recovered_geometry_result_builder_selector_parameters
selector_parameters.argtypes = [
    ctypes.POINTER(ctypes.c_int16), ctypes.c_uint32,
    ctypes.POINTER(ctypes.c_int16),
]
table = (ctypes.c_int16 * 9)(100, -200, 300, -400, 500, -600, 32767, -32768, 1)
parameters = (ctypes.c_int16 * 3)()
selector_parameters(table, 2, parameters)
assert list(parameters) == [32767, -32768, 1]

clear_fields = lib.recovered_geometry_result_builder_clear_fields
clear_fields.argtypes = [
    ctypes.c_int16, ctypes.c_int16, ctypes.c_uint32, ctypes.c_uint32,
    ctypes.POINTER(ClearFields),
]
fields = ClearFields()
clear_fields(-2, -32768, 0x101, 0xdeadbeef, ctypes.byref(fields))
assert [getattr(fields, name) for name, _ in ClearFields._fields_] == [
    0xfffffffe, 0xffff8000, 0x101, 0xdeadbeef,
    0x101, 0xfffffffe, 0xffff8000, 0x101, 0x101,
]

for flag, delta in ((0, 0), (1, 1)):
    plan = Plan()
    fn(2, flag, ctypes.byref(plan))
    assert plan.selector == 2 and plan.selector_stride_bytes == 12
    assert plan.parameter_table_address == 0x562436
    assert list(plan.parameter_halfword_offset) == [0, 2, 4]
    assert plan.request38_address == 0x884000 and plan.request38_word_count == 4
    assert plan.response_scratch_offset == 0x40
    assert list(plan.paired_record_offset) == [0, 4, 8]
    assert list(plan.paired_record_mirror_offset) == [0x10, 0x14, 0x18]
    assert plan.flag_offset == 0xa0 and plan.flag_set_delta_request == delta
    assert plan.flag_clear_fallback_table == 0x562cde
    assert plan.common_request31 == 31 and plan.common_request31_word_count == 7
    assert plan.final_sharc_handler == 0x203ea
    assert plan.final_sharc_parameter_count == 6 and plan.final_host_parameter_count == 6
    assert plan.final_sharc_output_pc == 0x20409
    assert plan.final_host_read_pc == 0x9e240 and plan.final_host_read_count == 1
    assert list(plan.final_output_register) == [0, 0, 0]
    assert list(plan.final_output_state_offset) == [0, 0, 0]
    assert [list(pair) for pair in plan.final_distance_operand_pair] == [[1, 4], [2, 5], [3, 6]]
    assert plan.final_first_output_is_first_host_operand == 0
    assert plan.final_host_stream_requires_followup_words == 0
    assert plan.final_flag0_means_input_fifo_empty == 1
    assert plan.final_response_offset == 0x28

result_is_length = lib.recovered_geometry_result_command31_result_is_length
result_is_length.argtypes = []
result_is_length.restype = ctypes.c_uint32
assert result_is_length() == 1

pairs = lib.recovered_geometry_result_command31_operand_pairs
pairs.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)]
pairs.restype = None
packet = (ctypes.c_uint32 * 7)(31, 10, 20, 30, 1, 2, 3)
differences = (ctypes.c_uint32 * 3)()
pairs(packet, differences)
assert list(differences) == [9, 18, 27]

related_differences = lib.recovered_geometry_result_builder_related_differences
related_differences.argtypes = [
    ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
    ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
]
response = (ctypes.c_uint32 * 3)(10, 20, 30)
related = (ctypes.c_uint32 * 3)(100, 5, 0)
output = (ctypes.c_uint32 * 3)()
mirror = (ctypes.c_uint32 * 3)()
related_differences(response, related, output, mirror)
assert list(output) == [90, 0xfffffff1, 0xffffffe2]
assert list(mirror) == list(output)
print("PASS: 0x9de50 shared result-builder entry")
