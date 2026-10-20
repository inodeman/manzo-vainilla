# Blender bpy script: stylized 3D "Manzo Vainilla" (fictional character). Run: blender -b -P render_3d.py -- [start end]
import bpy,math,wave,array,sys,os
D='/workspace/manzo_vainilla'; OUT='/tmp/mv3d'; os.makedirs(OUT,exist_ok=True)
argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
FPS=24
segs=[];t=0.4
for i in range(4):
    w=wave.open(f'{D}/l{i}.wav');d=w.getnframes()/w.getframerate();segs.append((t,t+d));t+=d+0.3
TOT=t+0.2; NF=int(TOT*FPS)
w=wave.open(f'{D}/audio.wav');sr=w.getframerate();ch=w.getnchannels()
A=array.array('h',w.readframes(w.getnframes()))[::ch]
def amp(f):
    tt=f/FPS
    if not any(s<=tt<e for s,e in segs[1:3]): return 0
    i=int(tt*sr);s=A[i:i+sr//FPS] or [0]
    return min(1,(sum(abs(x) for x in s)/len(s))/3500)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
def mat(n,c,r=0.5,ss=0.0):
    m=bpy.data.materials.new(n);m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*c,1);b.inputs['Roughness'].default_value=r
    if ss: b.inputs['Subsurface Weight'].default_value=ss;b.inputs['Subsurface Radius'].default_value=(0.3,0.1,0.05)
    return m
def emat(n,c,s=1):
    m=bpy.data.materials.new(n);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear()
    e=nt.nodes.new('ShaderNodeEmission');e.inputs[0].default_value=(*c,1);e.inputs[1].default_value=s
    o=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],o.inputs[0]);return m
SKIN=mat('skin',(0.7,0.42,0.28),0.45,0.15);HAIR=mat('hair',(0.02,0.02,0.025),0.35)
BLUE=mat('blue',(0.02,0.1,0.5),0.6);RED=mat('red',(0.7,0.05,0.05),0.4);WHITE=mat('white',(0.95,0.95,0.95),0.2)
BLACK=mat('black',(0.01,0.01,0.01),0.1);MOUTH=mat('mouth',(0.25,0.03,0.03),0.5);PANTS=mat('pants',(0.08,0.08,0.1),0.6)
WALL=mat('wall',(0.55,0.42,0.3),0.9);FLOOR=mat('floor',(0.35,0.2,0.1),0.5);WOOD=mat('wood',(0.45,0.27,0.12),0.5)
BOARD=mat('board',(0.05,0.18,0.08),0.9);CHALK=emat('chalk',(1,1,1),1.2);PAPER=mat('paper',(1,1,0.97),0.8)
INK=mat('ink',(0.02,0.02,0.02),0.5);DEBT=emat('debt',(1,0.1,0.05),3)
def obj(o,m,name=None):
    o.data.materials.append(m)
    if name: o.name=name
    return o
def sph(loc,scale,m,seg=48):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=seg//2,location=loc);o=bpy.context.object;o.scale=scale
    bpy.ops.object.shade_smooth();return obj(o,m)
def cube(loc,scale,m,bev=0.0,sub=0):
    bpy.ops.mesh.primitive_cube_add(location=loc);o=bpy.context.object;o.scale=scale
    if bev: md=o.modifiers.new('b','BEVEL');md.width=bev;md.segments=4
    if sub: o.modifiers.new('s','SUBSURF').levels=sub;bpy.ops.object.shade_smooth()
    return obj(o,m)
def cyl(loc,r,dep,m,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=r,depth=dep,location=loc,rotation=rot,vertices=32);o=bpy.context.object
    bpy.ops.object.shade_smooth();return obj(o,m)
def text(body,loc,size,m,rot=(math.radians(90),0,0)):
    bpy.ops.object.text_add(location=loc,rotation=rot);o=bpy.context.object;o.data.body=body;o.data.size=size
    o.data.align_x='CENTER';o.data.align_y='CENTER';o.data.extrude=0.01
    f='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    o.data.font=bpy.data.fonts.load(f,check_existing=True);return obj(o,m)
# room
cube((0,3,4),(8,0.1,6),WALL);cube((0,0,-0.05),(8,6,0.05),FLOOR)
cube((1.9,2.85,2.2),(1.35,0.05,0.85),WOOD,0.03);cube((1.9,2.8,2.2),(1.25,0.05,0.75),BOARD)
board=text('...',(1.9,2.74,2.2),0.42,CHALK)
debt=text('',(1.9,2.72,1.8),0.26,DEBT)
# desk + paper
cube((1.5,0.2,0.95),(1.1,0.55,0.05),WOOD,0.02)
for x in(0.5,2.5): cube((x,0.2,0.45),(0.06,0.45,0.45),WOOD)
paper=cube((1.4,0.05,1.01),(0.32,0.42,0.005),PAPER)
ptxt=text('PRÉSTAMO #47',(1.4,0.33,1.02),0.09,INK,(0,0,0))
lines=[cube((1.4,0.15-k*0.09,1.017),(0.25,0.006,0.002),INK) for k in range(5)]
sig=text('',(1.45,-0.3,1.02),0.1,mat('sig',(0.05,0.1,0.9),0.4),(0,0,0))
# character root
bpy.ops.object.empty_add(location=(-0.35,0.3,0));root=bpy.context.object
P=[]
def add(o): o.parent=root;P.append(o);return o
add(cube((0,0,1.5),(0.5,0.32,0.6),BLUE,0.12,2))           # jacket
add(cyl((0,0,2.1),0.18,0.25,SKIN));add(cube((0,-0.26,1.75),(0.1,0.04,0.3),WHITE,0.02,1))       # shirt front
add(cube((0,-0.31,1.72),(0.05,0.02,0.25),RED,0.01,1))       # tie
add(sph((0,-0.32,1.98),(0.07,0.03,0.05),RED,24))            # knot
for x in(-0.2,0.2): add(cyl((x,0,0.55),0.12,1.0,PANTS)); add(sph((x,-0.08,0.06),(0.16,0.24,0.08),BLACK,24))
armL=add(cyl((-0.6,0,1.5),0.11,0.8,BLUE,(0,math.radians(-8),0)));add(sph((-0.65,0,1.05),(0.11,0.11,0.11),SKIN,24))
bpy.ops.object.empty_add(location=(0.6,0,1.9));sh=bpy.context.object;add(sh)
a=cyl((0.6,0,1.5),0.11,0.8,BLUE,(0,math.radians(8),0));h=sph((0.65,0,1.05),(0.11,0.11,0.11),SKIN,24)
for o in(a,h):
    o.parent=sh;o.location.x-=0.6;o.location.z-=1.9
bpy.ops.object.empty_add(location=(0,0,2.55));head=bpy.context.object;add(head)
HP=[]
def hadd(o): o.parent=head;o.location.z-=2.55;return o
hadd(cube((0,0,2.6),(0.5,0.42,0.55),SKIN,0.25,2))  # square-ish head
hadd(cube((0,0.05,3.12),(0.52,0.44,0.14),HAIR,0.1,2))
for k in range(6): hadd(sph((-0.4+k*0.16,-0.36,3.02),(0.14,0.1,0.1),HAIR,24))
for x in(-0.52,0.52): hadd(sph((x,0,2.55),(0.06,0.1,0.14),SKIN,24))
for x in(-0.2,0.2):
    hadd(sph((x,-0.4,2.68),(0.13,0.07,0.12),WHITE,32));hadd(sph((x,-0.46,2.66),(0.05,0.02,0.05),BLACK,24))
    lid=hadd(sph((x,-0.405,2.71),(0.145,0.08,0.13),SKIN,32));
    hadd(cube((x,-0.43,2.86),(0.13,0.02,0.025),HAIR,0.01))  # flat brows
hadd(sph((0,-0.47,2.52),(0.07,0.06,0.08),SKIN,24))  # nose
mouth=hadd(sph((0,-0.42,2.3),(0.09,0.03,0.015),MOUTH,32))
# lids: cut upper-half via scale trick -> use half-closed by lowering lids (droopy). done above via larger sphere offset upward
# sweat
sweat=[hadd(sph((x,-0.35,2.9),(0.03,0.02,0.045),mat('sw',(0.5,0.8,1),0.05),16)) for x in(-0.45,0.47)]
# lights/camera
bpy.ops.object.light_add(type='AREA',location=(-2,-4,5));L=bpy.context.object;L.data.energy=700;L.data.size=4
L.rotation_euler=(math.radians(55),0,math.radians(-25))
bpy.ops.object.light_add(type='AREA',location=(3,-3,3));L2=bpy.context.object;L2.data.energy=250;L2.data.size=3;L2.data.color=(1,0.85,0.7)
L2.rotation_euler=(math.radians(65),0,math.radians(40))
bpy.ops.object.light_add(type='POINT',location=(0,1.5,4));bpy.context.object.data.energy=400
sc.world=bpy.data.worlds.new('w');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(0.6,0.7,0.85,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=0.2
bpy.ops.object.camera_add(location=(0.5,-6.5,2.2),rotation=(math.radians(88),0,0));cam=bpy.context.object;sc.camera=cam;cam.data.lens=36
r=sc.render;r.engine=os.environ.get('ENG','CYCLES');sc.cycles.device='CPU';sc.cycles.samples=int(os.environ.get('SAMPLES','24'));sc.cycles.use_denoising=True
sc.cycles.max_bounces=4;r.resolution_x=int(os.environ.get('RX','720'));r.resolution_y=int(os.environ.get('RX','720'))*16//9;r.use_persistent_data=True;r.resolution_percentage=100
r.image_settings.file_format='JPEG';r.image_settings.quality=92;sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Punchy';sc.view_settings.exposure=-0.4
r.threads_mode='FIXED';r.threads=8
def pose(f):
    tt=f/FPS;s=max([i for i,(a,b) in enumerate(segs) if a<=tt] or [0])
    m=amp(f);mouth.scale=(0.09,0.03,0.015+0.06*m)
    head.rotation_euler=(0.04*math.sin(tt*2),0,0.06*math.sin(tt*1.3))
    root.location.z=0.015*math.sin(tt*4)
    for k,o in enumerate(sweat): o.location.z=(2.9-((tt*0.5+k*0.5)%1)*0.5)
    board.data.body='2 + 2 = 5 ?' if (s>=1 and tt>segs[1][0]+3.2) else ('2 + 2 = ...' if s>=1 else '...')
    vis=s>=2
    for o in [paper,ptxt,sig]+lines: o.hide_render=not vis
    sh.rotation_euler=(math.radians(-60) if s==2 else 0,0,0)
    p=min(1,max(0,(tt-segs[2][0]-1.5)/1.5)) if s>=2 else 0
    sig.data.body='Manzo~'[:int(6*p)]
    debt.data.body=f'DEUDA: ${int(1e6*1.9**((tt-segs[3][0])*3)):,}' if s==3 else ''
    # camera push-in
    cam.location=(0.75,-6.6+0.8*(tt/TOT),2.0)
    board.location.z=2.45 if s==3 else 2.2
    if s==2: cam.location=(0.7,-5.6,1.9)
    sc.frame_set(f)
if argv and argv[0]=='thumb':
    pose(int((segs[1][0]+4.5)*FPS));sh.rotation_euler=(math.radians(-60),0,0)
    for o in [paper,ptxt]+lines: o.hide_render=False
    r.filepath=f'{OUT}/thumb.jpg';bpy.ops.render.render(write_still=True);sys.exit()
st,en=(int(argv[0]),int(argv[1])) if len(argv)>=2 else (0,NF)
STEP=int(os.environ.get('STEP','2'))
for f in range(st - st%STEP,en,STEP):
    fp=f'{OUT}/{f:05d}.jpg'
    if os.path.exists(fp): continue
    pose(f);r.filepath=fp;bpy.ops.render.render(write_still=True)
print('NF',NF)
