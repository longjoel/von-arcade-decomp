#!/usr/bin/env python3
import json, struct, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; TOOL=ROOT/"von/tools/export_geometry_family_assets.py"
def main():
 with tempfile.TemporaryDirectory() as temp:
  root=Path(temp); rom=root/'rom'; trace=root/'trace'; fingerprints=root/'fingerprints.json'; output=root/'assets'
  rom.write_bytes(struct.pack('<6fI3I3f3I',0,0,0,1,0,0,2,0,0,0,0,1,0,0,0,0))
  trace.write_text('[:] vonj_geometry_matrix: time=1 m=1,0,0,0,1,0,0,0,1 t=0,0,0\n[:] vonj_geometry_object: time=1 tpa=0 tha=0 oba=00000000 count=0 mode=3 source=polygon-rom\n')
  fingerprints.write_text(json.dumps({'assemblies':[{'fingerprint':'a','first_time':1,'first_slot':0,'object_count':1,'obas':['00000000']},{'fingerprint':'b','first_time':2,'first_slot':0,'object_count':1,'obas':['00000001']}], 'families':[{'family':'family-00','canonical':'a','variants':['a','b'],'frames':2}]}))
  subprocess.run(['python3',TOOL,'--fingerprints',fingerprints,'--trace',trace,'--rom',rom,'--output-dir',output],check=True)
  m=json.loads((output/'family-00/manifest.json').read_text())
  if m['core_obas'] or m['optional_obas'] != ['00000000'] or not (output/'family-00/canonical.gltf').exists(): raise SystemExit('family asset manifest mismatch')
 print('PASS: geometry family assets')
if __name__=='__main__': main()
