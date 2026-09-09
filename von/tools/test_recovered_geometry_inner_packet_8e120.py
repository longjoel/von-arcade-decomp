#!/usr/bin/env python3
import ctypes, pathlib, subprocess, tempfile
root=pathlib.Path(__file__).resolve().parents[2]; src=root/'von/i960/recovered_geometry_inner_packet_8e120.c'
listing=(root/'von/build/disasm/vonj-maincpu.lst').read_text()
for address, text in (("8e130", "ld"), ("8e134", "cmpibe"),
                      ("8e138", "cmpibe"), ("8e2b4", "ld"),
                      ("8e2b8", "cmpobl"), ("8e2d0", "stl")):
    assert any(address+":" in line and text in line for line in listing.splitlines())
class I(ctypes.Structure): _fields_=[(n,ctypes.c_uint32) for n in ('value_m2','value_0','value_2','value_4','value_6','value_8','parameter','object_word','object_field4','object_field8','object_word_c','fifo_response','frame_readback','returned_low','returned_high','direct_destination','table_index','table_arm_active','selection_flag')]
class P(ctypes.Structure): _fields_=[('fifo_word',ctypes.c_uint32*13),('fifo_count',ctypes.c_uint32),('selected_offset',ctypes.c_uint32),('selected_value',ctypes.c_uint32),('control_address',ctypes.c_uint32),('control_value',ctypes.c_uint32),('window_address',ctypes.c_uint32*4),('window_word',ctypes.c_uint32*4),('completion_word',ctypes.c_uint32),('fifo_read_address',ctypes.c_uint32),('fifo_read_value',ctypes.c_uint32),('low_address',ctypes.c_uint32),('high_address',ctypes.c_uint32),('low_value',ctypes.c_uint32),('high_value',ctypes.c_uint32),('table_write',ctypes.c_uint32),('table_address',ctypes.c_uint32)]
with tempfile.TemporaryDirectory() as d:
 so=pathlib.Path(d)/'inner.so'; subprocess.run(['cc','-shared','-fPIC','-O2','-I',str(root/'von/i960'),'-o',str(so),str(src)],check=True); f=ctypes.CDLL(str(so)).recovered_geometry_inner_packet_8e120; f.argtypes=[ctypes.POINTER(I),ctypes.POINTER(P)]
 i=I(1,2,3,4,5,6,7,0x11111111,0x22222222,0x33333333,0x44444444,0,0x55555555,0x66666666,0x77777777,1,2,0,0); p=P(); f(ctypes.byref(i),ctypes.byref(p)); assert p.selected_offset==4 and p.selected_value==0x22222222 and p.low_address==0x174 and p.high_address==0x17c
 i.fifo_response=1; i.direct_destination=0; i.table_arm_active=1; i.selection_flag=1; f(ctypes.byref(i),ctypes.byref(p)); assert p.selected_offset==8 and p.selected_value==0x33333333 and p.table_write and p.low_address==0x562448 and p.high_address==0x562450
 i.selection_flag=0; f(ctypes.byref(i),ctypes.byref(p)); assert p.selected_offset==4 and p.selected_value==0x22222222 and p.fifo_read_value == 1
 i.table_index=5; f(ctypes.byref(i),ctypes.byref(p)); assert p.table_write
 i.table_index=6; f(ctypes.byref(i),ctypes.byref(p)); assert not p.table_write
 i = I(0xffff,0x8000,1,2,3,0x8001,0x8002,0x11111111,0x22222222,0x33333333,0x44444444,0,0x55555555,0x66666666,0x77777777,0,2,0,0)
 f(ctypes.byref(i),ctypes.byref(p))
 assert list(p.fifo_word[2:11]) == [0xffff,0x8000,1,22,2,21,3,20,0xffff8001]
print('recovered geometry 0x8e120 inner-packet fixtures: ok')
