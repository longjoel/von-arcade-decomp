#!/usr/bin/env python3
"""Infer stable parent candidates from exact-family world transform samples."""
from __future__ import annotations
import argparse, json, math, statistics
from pathlib import Path
from export_geometry_frame_gltf import MATRIX, OBJECT

def inverse3(m):
 d=m[0]*(m[4]*m[8]-m[5]*m[7])-m[1]*(m[3]*m[8]-m[5]*m[6])+m[2]*(m[3]*m[7]-m[4]*m[6])
 if abs(d)<1e-8:return None
 return ((m[4]*m[8]-m[5]*m[7])/d,(m[2]*m[7]-m[1]*m[8])/d,(m[1]*m[5]-m[2]*m[4])/d,(m[5]*m[6]-m[3]*m[8])/d,(m[0]*m[8]-m[2]*m[6])/d,(m[2]*m[3]-m[0]*m[5])/d,(m[3]*m[7]-m[4]*m[6])/d,(m[1]*m[6]-m[0]*m[7])/d,(m[0]*m[4]-m[1]*m[3])/d)
def relative(parent, child):
 inv=inverse3(parent[:9]); delta=[child[i+9]-parent[i+9] for i in range(3)]
 return tuple(sum(inv[row*3+col]*delta[col] for col in range(3)) for row in range(3)) if inv else None
def main():
 p=argparse.ArgumentParser(description=__doc__); p.add_argument('--fingerprints',type=Path,required=True); p.add_argument('--family',required=True); p.add_argument('--trace',type=Path,required=True); p.add_argument('--output',type=Path,required=True); p.add_argument('--min-objects',type=int,default=1); a=p.parse_args()
 d=json.loads(a.fingerprints.read_text()); f=next(x for x in d['families'] if x['family']==a.family); obas=[int(x,16) for x in f['canonical_obas']]; start=f['first_slot']; cur=(1.,0.,0.,0.,1.,0.,0.,0.,1.,0.,0.,0.); frames={}
 for line in a.trace.open(errors='replace'):
  line=line.rstrip(); m=MATRIX.search(line)
  if m: cur=tuple(float(x) for x in m[2].split(','))+tuple(float(x) for x in m[3].split(',')); continue
  m=OBJECT.search(line)
  if m and int(m[6])==3 and m[7]=='polygon-rom': frames.setdefault(float(m[1]),[]).append((int(m[4],16),cur))
 samples=[x[start:start+len(obas)] for x in frames.values() if len(x)>=a.min_objects and [v[0] for v in x[start:start+len(obas)]]==obas]
 nodes=[]
 for child in range(len(obas)):
  candidates=[]
  for parent in range(len(obas)):
   if parent==child:continue
   values=[relative(frame[parent][1],frame[child][1]) for frame in samples]; values=[v for v in values if v]
   mean=[statistics.fmean(v[i] for v in values) for i in range(3)]
   rms=math.sqrt(statistics.fmean(sum((v[i]-mean[i])**2 for i in range(3)) for v in values))
   candidates.append({'parent_slot':start+parent,'parent_oba':f'{obas[parent]:08x}','relative_translation_rms':rms})
  nodes.append({'slot':start+child,'oba':f'{obas[child]:08x}','candidates':sorted(candidates,key=lambda x:x['relative_translation_rms'])[:3]})
 out={'family':a.family,'frames':len(samples),'nodes':nodes}; a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+'\n'); print(f'inferred candidates for {len(nodes)} nodes across {len(samples)} frames')
if __name__=='__main__':main()
