#!/usr/bin/env python3
import ctypes, pathlib, subprocess, tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_diagnostic_packet_8e4a0.c"

class Input(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "seed_word", "payload_word_1", "payload_word_2", "masked_word_a",
        "masked_word_b", "masked_word_c", "frame_readback")]
class Plan(ctypes.Structure):
    _fields_ = [("fifo_word", ctypes.c_uint32 * 16), ("fifo_count", ctypes.c_uint32),
                ("control_value", ctypes.c_uint32), ("masked_word_a", ctypes.c_uint32),
                ("masked_word_b", ctypes.c_uint32), ("masked_word_c", ctypes.c_uint32)]
class WindowPlan(ctypes.Structure):
    _fields_ = [("selected_response", ctypes.c_uint32),
                ("window_word", ctypes.c_uint32 * 4),
                ("control_address", ctypes.c_uint32), ("control_value", ctypes.c_uint32),
                ("completion_word", ctypes.c_uint32), ("next_record_stride", ctypes.c_uint32),
                ("next_record_pointer", ctypes.c_uint32),
                ("record_endpoint", ctypes.c_uint32), ("loop_continues", ctypes.c_uint32)]
class TerminalPlan(ctypes.Structure):
    _fields_ = [("fifo_word", ctypes.c_uint32 * 7), ("fifo_count", ctypes.c_uint32),
                ("frame_readback", ctypes.c_uint32)]
class RoutePlan(ctypes.Structure):
    _fields_ = [("state_word", ctypes.c_uint32), ("response_word", ctypes.c_uint32),
                ("next_target", ctypes.c_uint32)]
class RoutePacketPlan(ctypes.Structure):
    _fields_ = [("window_word", ctypes.c_uint32 * 4),
                ("control_address", ctypes.c_uint32), ("control_value", ctypes.c_uint32),
                ("next_target", ctypes.c_uint32)]
class ZeroStatePlan(ctypes.Structure):
    _fields_ = [("response_word", ctypes.c_uint32), ("frame_base_offset", ctypes.c_uint32),
                ("frame_word", ctypes.c_uint32 * 4), ("control_address", ctypes.c_uint32),
                ("control_value", ctypes.c_uint32), ("next_target", ctypes.c_uint32)]
class ModGatePlan(ctypes.Structure):
    _fields_ = [("counter", ctypes.c_uint32), ("modulus", ctypes.c_uint32),
                ("remainder", ctypes.c_uint32), ("completion_word", ctypes.c_uint32),
                ("next_target", ctypes.c_uint32)]
class TableSelectPlan(ctypes.Structure):
    _fields_ = [("remainder", ctypes.c_uint32), ("state_word", ctypes.c_uint32),
                ("table_base", ctypes.c_uint32), ("table_index", ctypes.c_uint32),
                ("selected_table_address", ctypes.c_uint32)]
class ConvergedPlan(ctypes.Structure):
    _fields_ = [("fifo_word", ctypes.c_uint32 * 10), ("fifo_count", ctypes.c_uint32),
                ("table_word_0", ctypes.c_uint32), ("table_word_1", ctypes.c_uint32),
                ("table_word_2", ctypes.c_uint32), ("frame_word_3", ctypes.c_uint32),
                ("frame_readback", ctypes.c_uint32),
                ("initial_window_word", ctypes.c_uint32 * 4),
                ("window_word", ctypes.c_uint32 * 4),
                ("final_window_word_3", ctypes.c_uint32),
                ("control_address", ctypes.c_uint32), ("control_value", ctypes.c_uint32),
                ("completion_word", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "diagnostic.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_packet_8e4a0
    fn.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Plan)]
    sample = Input(0x11111111, 0x22222222, 0x33333333,
                   0xaaaa0001, 0xbbbb0002, 0xcccc0003, 0xdeadbeef)
    plan = Plan(); fn(ctypes.byref(sample), ctypes.byref(plan))
    assert list(plan.fifo_word) == [5, 19, 0x40000000, 0x40000000, 0x40000000,
                                    5, 46, 0x11111111, 0x22222222, 0x33333333,
                                    1, 2, 46, 3, 46, 0xdeadbeef]
    assert plan.fifo_count == 16 and plan.control_value == 0x101
    assert (plan.masked_word_a, plan.masked_word_b, plan.masked_word_c) == (1, 2, 3)
    window_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_window_8e5b4
    window_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32),
                          ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32,
                          ctypes.c_uint32, ctypes.POINTER(WindowPlan)]
    zero_window = (ctypes.c_uint32 * 3)(1, 2, 3)
    nonzero_window = (ctypes.c_uint32 * 3)(4, 5, 6)
    window = WindowPlan()
    window_fn(0, zero_window, nonzero_window, 0x100, 0x12b, ctypes.byref(window))
    assert list(window.window_word) == [1, 2, 3, 0]
    window_fn(1, zero_window, nonzero_window, 0x100, 0x12b, ctypes.byref(window))
    assert list(window.window_word) == [4, 5, 6, 0]
    assert (window.control_address, window.control_value,
            window.completion_word, window.next_record_stride) == (0x800010, 0x101, 6, 0x2c)
    assert (window.next_record_pointer, window.record_endpoint,
            window.loop_continues) == (0x12c, 0x12b, 0)
    window_fn(0, zero_window, nonzero_window, 0x100, 0x12c, ctypes.byref(window))
    assert window.loop_continues
    terminal_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_terminal_8e67c
    terminal_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(TerminalPlan)]
    terminal = TerminalPlan(); terminal_fn(0xabcdef01, ctypes.byref(terminal))
    assert list(terminal.fifo_word) == [5, 18, 0xc0789518, 0x4192b46e,
                                        0x80000000, 46, 0xabcdef01]
    assert terminal.fifo_count == 7 and terminal.frame_readback == 0xabcdef01
    route_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_route_8e6f8
    route_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(RoutePlan)]
    route = RoutePlan()
    route_fn(0, 1, ctypes.byref(route)); assert route.next_target == 0x8e774
    route_fn(1, 0, ctypes.byref(route)); assert route.next_target == 0x8e704
    route_fn(1, 1, ctypes.byref(route)); assert route.next_target == 0x8e738
    packet704 = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_route_packet_8e704
    packet704.argtypes = [ctypes.POINTER(RoutePacketPlan)]
    packet738 = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_route_packet_8e738
    packet738.argtypes = [ctypes.c_uint32, ctypes.POINTER(RoutePacketPlan)]
    packet = RoutePacketPlan(); packet704(ctypes.byref(packet))
    assert list(packet.window_word) == [0x400de4, 0x400ea4, 0x84cf72, 0]
    assert (packet.control_address, packet.control_value, packet.next_target) == (0x800010, 0x101, 0x8e7f4)
    packet738(0x12345678, ctypes.byref(packet))
    assert list(packet.window_word) == [0x400de4, 0x5af93a, 0x84cf72, 0x12345678]
    assert packet.next_target == 0x8e7ec
    zero_state_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_zero_state_8e774
    zero_state_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ZeroStatePlan)]
    zero_state = ZeroStatePlan(); zero_state_fn(0, 0x1234, ctypes.byref(zero_state))
    assert (zero_state.frame_base_offset, list(zero_state.frame_word)) == (
        0x50, [0x9aee8, 0x9afa8, 0x9e35b7, 0x1234])
    zero_state_fn(1, 0x5678, ctypes.byref(zero_state))
    assert (zero_state.frame_base_offset, list(zero_state.frame_word)) == (
        0x60, [0x9aee8, 0x58f6ea, 0x9e35b7, 0x5678])
    assert (zero_state.control_address, zero_state.control_value,
            zero_state.next_target) == (0x800010, 0x101, 0x8e7ec)
    mod_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_mod_gate_8e7f4
    mod_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(ModGatePlan)]
    mod = ModGatePlan(); mod_fn(0x168 + 19, ctypes.byref(mod))
    assert (mod.modulus, mod.remainder, mod.completion_word, mod.next_target) == (0x168, 19, 6, 0x8e818)
    mod_fn(0x168 + 20, ctypes.byref(mod))
    assert mod.remainder == 20 and mod.next_target == 0x8e834
    table_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_table_select_8e818
    table_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(TableSelectPlan)]
    table = TableSelectPlan()
    table_fn(19, 0, ctypes.byref(table))
    assert (table.table_base, table.table_index, table.selected_table_address) == (
        0x2be4d10 - 0x5a60, 0, 0x2be4d10 - 0x5a60)
    table_fn(20, 1, ctypes.byref(table))
    assert (table.table_base, table.table_index, table.selected_table_address) == (
        0x2be4d10, 0, 0x2be4d10)
    table_fn(139, 0, ctypes.byref(table))
    assert (table.table_base, table.table_index, table.selected_table_address) == (
        0x2be4770, 59, 0x2be4770 + 59 * 4)
    table_fn(239, 1, ctypes.byref(table))
    assert (table.table_base, table.table_index, table.selected_table_address) == (
        0x2be4fd4, 0, 0x2be4fd4)
    table_fn(240, 1, ctypes.byref(table))
    assert (table.table_base, table.table_index, table.selected_table_address) == (
        0x2be4770, 59, 0x2be4770 + 59 * 4)
    table_fn(359, 0, ctypes.byref(table))
    assert (table.table_base, table.table_index, table.selected_table_address) == (
        0x2be4d10, 0, 0x2be4d10)
    converged_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_converged_8e8f4
    converged_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                             ctypes.c_uint32, ctypes.c_uint32,
                             ctypes.POINTER(ConvergedPlan)]
    converged = ConvergedPlan()
    converged_fn(0x11111111, 0x22222222, 0x33333333, 0x44444444,
                 0x55555555, ctypes.byref(converged))
    assert list(converged.fifo_word) == [5, 44, 0x4071ff2e, 0x41417c85,
                                         0x3fae1134, 0x1588, 0x44444444,
                                         0xfff8, 46, 0x55555555]
    assert list(converged.initial_window_word) == [0x11111111, 0x22222222,
                                                   0x33333333, 0x44444444]
    assert list(converged.window_word) == [0x11111111, 0x22222222, 0x33333333,
                                           0x44444444]
    assert converged.final_window_word_3 == 0x44444444
    assert (converged.control_address, converged.control_value,
            converged.completion_word) == (0x800010, 0x101, 6)
print("recovered geometry 0x8e4a0 diagnostic-packet fixture: ok")
