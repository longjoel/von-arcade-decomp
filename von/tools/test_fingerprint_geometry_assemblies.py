#!/usr/bin/env python3
import json, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; TOOL=ROOT/"von/tools/fingerprint_geometry_assemblies.py"
def main():
 with tempfile.TemporaryDirectory() as temp:
  root=Path(temp); trace=root/"trace"; output=root/"out.json"; lines=[]
  for time in (1,2):
   for x,oba in ((0,"00000001"),(1,"00000002"),(30,"00000003")):
    lines += [f"[:] vonj_geometry_matrix: time={time} m=1,0,0,0,1,0,0,0,1 t={x},0,0", f"[:] vonj_geometry_object: time={time} tpa=0 tha=0 oba={oba} count=0 mode=3 source=polygon-rom"]
  trace.write_text("\n".join(lines)+"\n")
  subprocess.run(["python3",TOOL,"--trace",trace,"--output",output,"--min-objects","3","--distance","10"],check=True)
  data=json.loads(output.read_text())
  if data["complete_frames"] != 2 or [x["frames"] for x in data["assemblies"]] != [2,2] or len(data["families"]) != 2: raise SystemExit("fingerprint frame tracking mismatch")
 print("PASS: geometry assembly fingerprints")
if __name__=="__main__": main()
