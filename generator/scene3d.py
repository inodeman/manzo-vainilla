# Se ejecuta dentro de Blender: blender -b -P scene3d.py -- job.json
import bpy,math,wave,array,sys,os,json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import lib3d as L3
job=json.load(open(sys.argv[sys.argv.index('--')+1],encoding='utf-8'))
ep=job['ep'];L=job['lines'];FPS=job['fps'];TOT=job['total'];OUT=job['frames'];SC=ep['scenes']
w=wave.open(job['audio']);sr=w.getframerate();ch=w.getnchannels()
A=array.array('h',w.readframes(w.getnframes()))[::ch]
def amp(tt,name):
    if not any(l['start']<=tt<l['end'] and l['speaker']==name for l in L): return 0
    i=int(tt*sr);s=A[i:i+sr//FPS] or [0]
    return min(1,(sum(abs(x) for x in s)/len(s))/3500)
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene
# escenarios: uno por cada configuración distinta, en su propia colección
SETS={}
for s in SC:
    key=json.dumps(s['_set'],sort_keys=True)
    if key in SETS: s['_sk']=key;continue
    col=bpy.data.collections.new('set%d'%len(SETS));sc.collection.children.link(col)
    lc=bpy.context.view_layer.layer_collection.children[col.name];bpy.context.view_layer.active_layer_collection=lc
    R=L3.build_set(s['_set']);R['col']=col;R['world']=sc.world;SETS[key]=R;s['_sk']=key
bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection
INK=L3.mat('ink',(0.02,0.02,0.02),0.5)
paper=L3.cube((1.4,0.05,1.01),(0.32,0.42,0.005),L3.mat('paper','#fffff8',0.8));ptxt=L3.text('',(1.4,0.33,1.02),0.09,INK,(0,0,0))
plines=[L3.cube((1.4,0.15-k*0.09,1.017),(0.25,0.006,0.002),INK) for k in range(5)];sig=L3.text('',(1.45,-0.3,1.02),0.1,L3.mat('sig','#0d1ae6',0.4),(0,0,0))
onscreen=[c for c in ep['characters'] if c.get('on_screen',True)]
xs={1:[-0.35],2:[-0.9,0.35]}.get(len(onscreen),[-1.2+i*0.8 for i in range(len(onscreen))])
CH={c['name']:L3.build_character(c,xs[i],'c%d'%i) for i,c in enumerate(onscreen)}
cam=L3.setup_render(job['res'],job['samples'])
def scene_at(tt):
    i=0
    for k,s in enumerate(SC):
        if s['_start']-1e-4<=tt: i=k
    return i
def pose(f):
    tt=f/FPS;si=scene_at(tt);s=SC[si];s0=s['_start'];R=SETS[s['_sk']]
    for k,v in SETS.items(): v['col'].hide_render=(k!=s['_sk'])
    sc.world=R['world']
    for n,c in CH.items():
        m=amp(tt,n);c['mouth'].scale=(0.09,0.03,0.015+0.06*m)
        c['head'].rotation_euler=(0.04*math.sin(tt*2),0,0.06*math.sin(tt*1.3));c['root'].location.z=0.015*math.sin(tt*4)
        for k,o in enumerate(c['sweat']): o.location.z=0.35-((tt*0.5+k*0.5)%1)*0.5
        c['sh'].rotation_euler=(math.radians(-60) if (s.get('sign') and s['sign'].get('signer',n)==n) else 0,0,0)
    bt=''
    for k in range(si+1):
        b=SC[k].get('board')
        if b is not None: bt=b if isinstance(b,str) else b.get('text','')
    b=s.get('board')
    if isinstance(b,dict) and b.get('before') and tt<s0+b.get('reveal_at',2): bt=b['before']
    cn=s.get('counter')
    for v in SETS.values():
        v['board'].data.body=bt;v['board'].data.size=min(0.42,2.3/(0.62*max(1,len(bt))));v['board'].location.z=v['board_z']+(0.25 if cn else 0)
        v['counter'].data.body=f"{cn.get('label','')}{int(cn.get('start',1e6)*cn.get('growth',1.9)**((tt-s0)*3)):,}" if cn else ''
    sg=None
    for k in range(si+1):
        if SC[k].get('sign'): sg=SC[k]['sign'];sk=SC[k]
    for o in [paper,ptxt,sig]+plines: o.hide_render=sg is None
    if sg:
        ptxt.data.body=sg.get('text','');p=min(1,max(0,(tt-sk['_start']-1.5)/1.5)) if sk is s else 1
        sn=sg.get('signature','Firma~');sig.data.body=sn[:int(len(sn)*p)]
    cam.location=(0.75,-6.6+0.8*(tt/TOT),2.0)
    if s.get('camera')=='close': cam.location=(0.7,-5.6,1.9)
    sc.frame_set(f)
r=sc.render;NF=int(TOT*FPS);step=job['step'];th=ep.get('thumbnail',{})
tsi=th.get('scene',min(1,len(SC)-1));pose(int((SC[tsi]['_start']+th.get('at',2.0))*FPS))
s=sc.cycles.samples;sc.cycles.samples=max(s,32);r.filepath=os.path.join(os.path.dirname(OUT),'thumb.jpg');bpy.ops.render.render(write_still=True);sc.cycles.samples=s
for f in range(0,NF,step):
    fp=os.path.join(OUT,f'{f:05d}.jpg')
    if os.path.exists(fp): continue
    pose(f);r.filepath=fp;bpy.ops.render.render(write_still=True)
