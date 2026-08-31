#!/usr/bin/env python3
import json, struct, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; TOOL=ROOT/'von/tools/export_geometry_family_animation.py'
def main():
 with tempfile.TemporaryDirectory() as temp:
  root=Path(temp); rom=root/'rom'; trace=root/'trace'; fp=root/'fp.json'; out=root/'out.gltf'
  rom.write_bytes(struct.pack('<6fI3I3f3I',0,0,0,1,0,0,2,0,0,0,0,1,0,0,0,0))
  lines=[]
  for t,x in ((1,0),(2,3)):
   lines += [f'[:] vonj_geometry_matrix: time={t} m=1,0,0,0,1,0,0,0,1 t={x},0,0',f'[:] vonj_geometry_object: time={t} tpa=0 tha=0 oba=00000000 count=0 mode=3 source=polygon-rom']
  trace.write_text('\n'.join(lines)+'\n')
  fp.write_text(json.dumps({'families':[{'family':'family-00','first_slot':0,'canonical_obas':['00000000']}]}))
  subprocess.run(['python3',TOOL,'--fingerprints',fp,'--family','family-00','--trace',trace,'--rom',rom,'--output',out],check=True)
  d=json.loads(out.read_text())
  if len(d['nodes'])!=1 or d['extras']['frames']!=2 or len(d['animations'][0]['channels'])!=3: raise SystemExit('family animation structure mismatch')
 print('PASS: stable geometry family animation')
if __name__=='__main__': main()
