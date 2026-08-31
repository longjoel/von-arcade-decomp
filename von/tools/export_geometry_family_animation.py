#!/usr/bin/env python3
"""Export a stable geometry family as a transform-only glTF animation."""
from __future__ import annotations
import argparse, base64, json, struct
from pathlib import Path
from export_geometry_animation_gltf import parse_mesh, transform_trs
from export_geometry_frame_gltf import MATRIX, OBJECT

def main():
 p=argparse.ArgumentParser(description=__doc__); p.add_argument('--fingerprints',type=Path,required=True); p.add_argument('--family',required=True); p.add_argument('--trace',type=Path,required=True); p.add_argument('--rom',type=Path,required=True); p.add_argument('--output',type=Path,required=True); p.add_argument('--min-objects',type=int,default=1); a=p.parse_args()
 d=json.loads(a.fingerprints.read_text()); fam=next((x for x in d['families'] if x['family']==a.family),None)
 if not fam: raise SystemExit('family not found')
 canonical=[int(x,16) for x in fam['canonical_obas']]; start=fam['first_slot']; current=(1.,0.,0.,0.,1.,0.,0.,0.,1.,0.,0.,0.); frames={}
 for line in a.trace.open(errors='replace'):
  line=line.rstrip(); m=MATRIX.search(line)
  if m: current=tuple(float(x) for x in m[2].split(','))+tuple(float(x) for x in m[3].split(',')); continue
  m=OBJECT.search(line)
  if m and int(m[6])==3 and m[7]=='polygon-rom': frames.setdefault(float(m[1]),[]).append((int(m[4],16),current))
 selected=[(t,x[start:start+len(canonical)]) for t,x in sorted(frames.items()) if len(x)>=a.min_objects and [v[0] for v in x[start:start+len(canonical)]]==canonical]
 if len(selected)<2: raise SystemExit('fewer than two exact canonical-family frames')
 blob=bytearray(); views=[]; accessors=[]; meshes=[]; nodes=[]; samplers=[]; channels=[]
 def add(data,target=None):
  off=len(blob); blob.extend(data); v={'buffer':0,'byteOffset':off,'byteLength':len(data)}
  if target:v['target']=target
  views.append(v); return len(views)-1
 rom=a.rom.read_bytes()
 for slot,oba in enumerate(canonical):
  verts,inds=parse_mesh(rom,oba); pv=add(b''.join(struct.pack('<3f',*v) for v in verts),34962); iv=add(b''.join(struct.pack('<I',i) for i in inds),34963); pos=len(accessors); accessors += [{'bufferView':pv,'componentType':5126,'count':len(verts),'type':'VEC3'},{'bufferView':iv,'componentType':5125,'count':len(inds),'type':'SCALAR'}]; meshes.append({'name':f'oba_{oba:08x}','primitives':[{'attributes':{'POSITION':pos},'indices':pos+1,'mode':4}]}); nodes.append({'mesh':slot,'name':f'family_slot_{start+slot:03d}_oba_{oba:08x}'})
 times=[t for t,_ in selected]; tv=add(b''.join(struct.pack('<f',t-times[0]) for t in times)); ti=len(accessors); accessors.append({'bufferView':tv,'componentType':5126,'count':len(times),'type':'SCALAR','min':[0.],'max':[times[-1]-times[0]]})
 for slot in range(len(canonical)):
  matrices=[x[slot][1] for _,x in selected]
  for path,data,typ in [('translation',b''.join(struct.pack('<3f',*m[9:12]) for m in matrices),'VEC3'),('rotation',b''.join(struct.pack('<4f',*transform_trs(m)[0]) for m in matrices),'VEC4'),('scale',b''.join(struct.pack('<3f',*transform_trs(m)[1]) for m in matrices),'VEC3')]:
   oi=len(accessors); accessors.append({'bufferView':add(data),'componentType':5126,'count':len(times),'type':typ}); samplers.append({'input':ti,'output':oi,'interpolation':'LINEAR'}); channels.append({'sampler':len(samplers)-1,'target':{'node':slot,'path':path}})
 out={'asset':{'version':'2.0','generator':'von export_geometry_family_animation.py'},'scene':0,'scenes':[{'nodes':list(range(len(nodes)))}],'nodes':nodes,'meshes':meshes,'animations':[{'name':a.family,'samplers':samplers,'channels':channels}],'buffers':[{'byteLength':len(blob),'uri':'data:application/octet-stream;base64,'+base64.b64encode(blob).decode()}],'bufferViews':views,'accessors':accessors,'extras':{'family':a.family,'frames':len(times),'start_time':times[0],'end_time':times[-1]}}
 a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+'\n'); print(f'wrote {len(nodes)} nodes and {len(times)} clean family frames to {a.output}')
if __name__=='__main__': main()
