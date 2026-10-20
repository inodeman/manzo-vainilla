# Biblioteca procedural para Blender: escenarios, utilería y personajes estilizados (ficticios).
import bpy,math,os
_M={}
def hexc(h,default='#888888'):
    h=(h or default).lstrip('#');return tuple((int(h[i:i+2],16)/255)**2.2 for i in (0,2,4))
def mat(n,c,r=0.5,ss=0.0,em=0):
    if isinstance(c,str): c=hexc(c)
    key=(n,c,r,ss,em)
    if key in _M: return _M[key]
    m=bpy.data.materials.new(n);m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*c,1);b.inputs['Roughness'].default_value=r
    if ss: b.inputs['Subsurface Weight'].default_value=ss;b.inputs['Subsurface Radius'].default_value=(0.3,0.1,0.05)
    if em: b.inputs['Emission Color'].default_value=(*c,1);b.inputs['Emission Strength'].default_value=em
    _M[key]=m;return m
def emat(n,c,s=1):
    m=bpy.data.materials.new(n);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear()
    e=nt.nodes.new('ShaderNodeEmission');e.inputs[0].default_value=(*c,1);e.inputs[1].default_value=s
    o=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],o.inputs[0]);return m
def fin(o,m): o.data.materials.append(m);return o
def sph(loc,scale,m,seg=40):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=seg//2,location=loc);o=bpy.context.object;o.scale=scale
    bpy.ops.object.shade_smooth();return fin(o,m)
def cube(loc,scale,m,bev=0.0,sub=0,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(location=loc,rotation=rot);o=bpy.context.object;o.scale=scale
    if bev: md=o.modifiers.new('b','BEVEL');md.width=bev;md.segments=4
    if sub: o.modifiers.new('s','SUBSURF').levels=sub;bpy.ops.object.shade_smooth()
    return fin(o,m)
def cyl(loc,r,dep,m,rot=(0,0,0),v=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=r,depth=dep,location=loc,rotation=rot,vertices=v);o=bpy.context.object
    bpy.ops.object.shade_smooth();return fin(o,m)
def cone(loc,r,dep,m,v=24):
    bpy.ops.mesh.primitive_cone_add(radius1=r,depth=dep,location=loc,vertices=v);o=bpy.context.object;bpy.ops.object.shade_smooth();return fin(o,m)
FONTP='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def text(body,loc,size,m,rot=(math.radians(90),0,0)):
    bpy.ops.object.text_add(location=loc,rotation=rot);o=bpy.context.object;o.data.body=body;o.data.size=size
    o.data.align_x='CENTER';o.data.align_y='CENTER';o.data.extrude=0.01
    if os.path.exists(FONTP): o.data.font=bpy.data.fonts.load(FONTP,check_existing=True)
    return fin(o,m)
WOOD=lambda:mat('wood','#8a5a30',0.5)
# ---------- utilería ----------
def p_desk(x=1.5,y=0.2):
    cube((x,y,0.95),(1.1,0.55,0.05),WOOD(),0.02)
    for dx in(-1,1): cube((x+dx,y,0.45),(0.06,0.45,0.45),WOOD())
def p_papers(x=0.6,y=0.4):
    for k in range(4): cube((x+0.05*k,y,1.02+0.02*k),(0.2,0.27,0.008),mat('pap','#f4f1e6',0.8),rot=(0,0,0.2*k-0.3))
def p_chair(x,y):
    m=mat('chair','#6b3a1e',0.6);cube((x,y,0.5),(0.25,0.25,0.04),m,0.02)
    cube((x,y+0.24,0.85),(0.25,0.03,0.33),m,0.02)
    for dx in(-0.2,0.2):
        for dy in(-0.2,0.2): cyl((x+dx,y+dy,0.25),0.025,0.5,m)
def p_window(night,x=-1.3,z=3.6):
    cube((x,2.93,z),(0.8,0.04,0.65),mat('frame','#f0ead8',0.6))
    sky='#0d1530' if night else '#9fd0ff';cube((x,2.9,z),(0.7,0.03,0.55),emat('glass',hexc(sky),1.0 if not night else 0.6))
    cube((x,2.88,z),(0.03,0.03,0.55),mat('frame','#f0ead8',0.6));cube((x,2.88,z),(0.7,0.03,0.03),mat('frame','#f0ead8',0.6))
    if night: sph((x+0.4,2.87,z+0.3),(0.1,0.01,0.1),emat('moon',(1,1,0.85),3))
def p_door(x=-3.3): cube((x,2.93,1.1),(0.5,0.04,1.1),mat('door','#6b3a1e',0.5),0.02);sph((x+0.38,2.86,1.1),(0.05,0.05,0.05),mat('knob','#c9a227',0.2))
def p_plant(x,y):
    cyl((x,y,0.25),0.2,0.5,mat('pot','#a0522d',0.6))
    for k in range(5): sph((x+0.15*math.cos(k*1.3),y+0.15*math.sin(k*1.3),0.7+0.08*k),(0.18,0.18,0.25),mat('leaf','#2e8b3a',0.6),16)
def p_tree(x,y,s=1):
    cyl((x,y,1.0*s),0.15*s,2.0*s,mat('trunk','#5a3518',0.8))
    for k,(dx,dz) in enumerate([(0,2.3),(-0.4,2.0),(0.4,2.0),(0,1.8)]): sph((x+dx*s,y,dz*s+0.2),(0.8*s,0.8*s,0.7*s),mat('fol','#2f7a2f',0.7),24)
def p_kiosk(x=-1.8,y=2.0):
    m=mat('kio','#e8e0c8',0.5);cyl((x,y,0.15),1.4,0.3,m,v=8)
    for k in range(8): a=k*math.pi/4;cyl((x+1.25*math.cos(a),y+1.25*math.sin(a),1.4),0.06,2.2,mat('kc','#2a6a3a',0.4))
    cone((x,y,2.9),1.6,0.9,mat('roof','#2a6a3a',0.4),8)
def p_bench(x,y):
    m=mat('bench','#7a4a22',0.6);cube((x,y,0.45),(0.7,0.2,0.04),m,0.02);cube((x,y+0.18,0.75),(0.7,0.03,0.18),m,0.02)
    for dx in(-0.6,0.6): cube((x+dx,y,0.22),(0.04,0.18,0.22),mat('iron','#222222',0.3))
def p_car(x=3.2,y=1.2):
    c=mat('car','#c02020',0.25);cube((x,y,0.55),(1.0,0.5,0.3),c,0.15,1);cube((x-0.1,y,0.95),(0.6,0.45,0.22),c,0.12,1)
    cube((x-0.1,y-0.46,0.95),(0.5,0.01,0.15),mat('glass2','#223344',0.05))
    for dx in(-0.6,0.6):
        for dy in(-0.5,0.5): cyl((x+dx,y+dy,0.25),0.25,0.15,mat('tire','#111111',0.8),(math.pi/2,0,0))
def p_lamppost(x,y,night):
    cyl((x,y,1.6),0.05,3.2,mat('iron','#222222',0.3));sph((x,y,3.25),(0.18,0.18,0.18),emat('bulb',(1,0.85,0.5),8 if night else 1))
    if night: bpy.ops.object.light_add(type='POINT',location=(x,y-0.3,3.1));bpy.context.object.data.energy=300;bpy.context.object.data.color=(1,0.8,0.5)
def p_sofa(x=-2.4,y=1.6):
    m=mat('sofa','#7a2a3a',0.8);cube((x,y,0.35),(0.9,0.4,0.2),m,0.1,1);cube((x,y+0.33,0.75),(0.9,0.1,0.35),m,0.08,1)
    for dx in(-0.85,0.85): cube((x+dx,y,0.55),(0.1,0.4,0.25),m,0.06,1)
def p_tv(x=3.0,y=2.2):
    cube((x,y,0.4),(0.6,0.3,0.4),WOOD(),0.02);cube((x,y,1.25),(0.65,0.04,0.4),mat('tvb','#111111',0.2));cube((x,y-0.05,1.25),(0.6,0.01,0.35),emat('scr',(0.3,0.5,0.9),1.5))
def p_flag(x=-2.4,y=2.4):
    cyl((x,y,1.3),0.03,2.6,mat('pole','#c9a227',0.2))
    for k,c in enumerate(['#1f7a2e','#f0f0f0','#b81010']): cube((x+0.25+0.3*k,y,2.25),(0.15,0.01,0.3),mat('fl'+c,c,0.7))
def p_umbrella(x=-2.0,y=1.5):
    cyl((x,y,1.1),0.03,2.2,mat('pole','#eeeeee',0.3));cone((x,y,2.3),1.2,0.4,mat('umb','#e05050',0.6),12)
def p_fridge(x=-2.6,y=2.4): cube((x,y,1.0),(0.45,0.4,1.0),mat('fridge','#e8e8e8',0.2),0.05,1)
def p_stove(x=3.0,y=2.3):
    cube((x,y,0.45),(0.5,0.4,0.45),mat('stove','#dddddd',0.3),0.03)
    for dx in(-0.2,0.2):
        for dy in(-0.15,0.15): cyl((x+dx,y+dy,0.91),0.1,0.02,mat('burn','#222222',0.4))
def p_rain():
    m=mat('drop','#9fc8ff',0.05)
    import random;random.seed(3)
    for k in range(250): cube((random.uniform(-4,5),random.uniform(-3,2.5),random.uniform(0.2,6)),(0.008,0.008,0.12),m)
def build_set(p):
    """p: dict de parse_set (o explícito). Devuelve dict con objetos del pizarrón/letrero para animar."""
    night=p.get('time')=='night';out=p.get('outdoor',False);props=p.get('props',[])
    floor=mat('floor',p.get('floor','#9e7a58'),0.6);cube((0,0,-0.05),(12,8,0.05),floor)
    if out:
        sky={'night':(0.01,0.015,0.05),'sunset':(0.9,0.45,0.25),'morning':(0.65,0.75,0.9),'day':(0.45,0.65,0.95)}[p.get('time','day')]
        if p.get('weather')in('cloudy','rain'): sky=tuple(0.5*s+0.2 for s in sky)
        bgcol,bgs=sky,(0.15 if night else 1.0)
        if p.get('type')=='street': 
            for k,c in enumerate(['#d89a6a','#7fa8c9','#e3c86a','#b5c98a']): cube((-4.5+k*3,5,2.5),(1.4,1,2.5),mat('bld'+c,c,0.8),0.05)
        if p.get('type')=='beach': cube((0,9,0.02),(30,3,0.02),mat('sea','#1f6fae',0.1))
    else:
        cube((0,3,4),(8,0.1,6),mat('wall',p.get('wall','#c4ad93'),0.9))
        if p.get('old'):
            for k in range(6): cube((-3+k*1.3,2.88,0.15),(0.6,0.02,0.15),mat('base','#5a4630',0.8))
        bgcol,bgs=(0.6,0.7,0.85),(0.05 if night else 0.2)
    sun_e=0 if night else 3
    sc=bpy.context.scene;sc.world=bpy.data.worlds.new('w');sc.world.use_nodes=True;bg=sc.world.node_tree.nodes['Background']
    bg.inputs[0].default_value=(*bgcol,1);bg.inputs[1].default_value=bgs
    if out:
        bpy.ops.object.light_add(type='SUN',location=(0,0,10),rotation=(math.radians(50),0,math.radians(-30)));s=bpy.context.object.data;s.energy=sun_e if p.get('weather')=='sunny' else sun_e*0.4
        if p.get('time')=='sunset': s.color=(1,0.6,0.4)
    # luces de personaje (siempre)
    k=0.5 if night else 1
    bpy.ops.object.light_add(type='AREA',location=(-2,-4,5));l=bpy.context.object;l.data.energy=700*k;l.data.size=4;l.rotation_euler=(math.radians(55),0,math.radians(-25))
    bpy.ops.object.light_add(type='AREA',location=(3,-3,3));l=bpy.context.object;l.data.energy=250*k;l.data.size=3;l.data.color=(1,0.85,0.7) if not night else (0.6,0.7,1);l.rotation_euler=(math.radians(65),0,math.radians(40))
    if not out: bpy.ops.object.light_add(type='POINT',location=(0,1.5,4));bpy.context.object.data.energy=400*k
    R={}
    # pizarrón / letrero (siempre existe para textos de escena)
    if out:
        cyl((1.0,2.6,1.3),0.05,2.6,WOOD());cyl((2.8,2.6,1.3),0.05,2.6,WOOD())
        cube((1.9,2.6,2.2),(1.35,0.05,0.85),mat('sign','#f0ead8',0.6),0.03);cube((1.9,2.55,2.2),(1.25,0.05,0.75),mat('board','#1d3d6a',0.8));by=2.49
    else:
        show='board' in props or True
        cube((1.9,2.85,2.2),(1.35,0.05,0.85),WOOD(),0.03);cube((1.9,2.8,2.2),(1.25,0.05,0.75),mat('board','#0e3a18',0.9));by=2.74
    R['board']=text('',(1.9,by,2.2),0.42,emat('chalk',(1,1,1),1.2));R['counter']=text('',(1.9,by-0.02,1.8),0.26,emat('cnt',(1,0.1,0.05),3))
    R['board_z']=2.2
    # mesa para firmar (siempre que haya 'desk' o se use 'sign')
    p_desk() if ('desk' in props or not out) else cube((1.5,0.2,0.95),(1.1,0.55,0.05),WOOD(),0.02) or [cyl((1.5+dx,0.2,0.45),0.05,0.9,WOOD()) for dx in(-1,1)]
    if 'papers' in props: p_papers()
    if 'chairs' in props: p_chair(2.9,0.9);p_chair(-2.0,0.5)
    if 'window' in props and not out: p_window(night)
    if 'door' in props and not out: p_door()
    if 'plants' in props: p_plant(-2.2,1.8)
    if 'trees' in props: p_tree(-2.6,3.8);p_tree(3.8,4.2,1.2)
    if 'kiosk' in props: p_kiosk(-1.2,5.0)
    if 'bench' in props: p_bench(-2.0,2.2)
    if 'car' in props: p_car(3.4,3.5)
    if 'lampposts' in props: p_lamppost(-2.4,2.2,night);p_lamppost(3.4,1.5,night)
    if 'sofa' in props: p_sofa()
    if 'tv' in props: p_tv()
    if 'flag' in props and not out: p_flag()
    if 'umbrella' in props: p_umbrella()
    if 'fridge' in props: p_fridge()
    if 'stove' in props: p_stove()
    if p.get('weather')=='rain' and out: p_rain()
    return R
# ---------- personaje ----------
def build_character(c,x=-0.35,name='P'):
    n=name;SKIN=mat(n+'skin',c.get('skin','#d9ad8f'),0.45,0.15);HAIR=mat(n+'hair',c.get('hair','#0a0a0a'),0.35)
    SH=mat(n+'shirt',c.get('shirt','#0a3fb8'),0.6);PANTS=mat(n+'p',c.get('pants','#141418'),0.6)
    WHITE=mat('white',(0.95,0.95,0.95),0.2);BLACK=mat('black',(0.01,0.01,0.01),0.1);MOUTH=mat('mouth',(0.25,0.03,0.03),0.5)
    h=float(c.get('height',1.0));b=float(c.get('build',1.0));fem=c.get('gender')=='female'
    bpy.ops.object.empty_add(location=(x,0.3,0));root=bpy.context.object;root.scale=(1,1,h)
    def add(o,p=root,off=(0,0,0)): o.parent=p;o.location.x-=off[0];o.location.y-=off[1];o.location.z-=off[2];return o
    outfit=c.get('outfit','shirt')
    add(cube((0,0,1.5),(0.5*b,0.32*b,0.6),SH,0.12+0.1*(b>1.1),2))
    if b>1.1: add(sph((0,-0.08*b,1.25),(0.47*b,0.3*b,0.42),SH))
    add(cyl((0,0,2.1),0.18,0.25,SKIN))
    if outfit!='tshirt': add(cube((0,-0.26*b-0.01,1.75),(0.1,0.04,0.3),WHITE,0.02,1))
    tie=c.get('tie',False)
    if tie: T=mat(n+'tie',tie if isinstance(tie,str) else '#c01010',0.4);add(cube((0,-0.31*b-0.01,1.72),(0.05,0.02,0.25),T,0.01,1));add(sph((0,-0.32*b-0.01,1.98),(0.07,0.03,0.05),T,24))
    if outfit=='dress' or (fem and outfit!='suit'): add(cone((0,0,0.85),0.55*b,0.7,SH))
    for xx in(-0.2,0.2): add(cyl((xx*b,0,0.55),0.12*min(b,1.2),1.0,PANTS if not fem else SKIN));add(sph((xx*b,-0.08,0.06),(0.16,0.24,0.08),BLACK,24))
    add(cyl((-0.6*b,0,1.5),0.11*b,0.8,SH,(0,math.radians(-8),0)));add(sph((-0.65*b,0,1.05),(0.11,0.11,0.11),SKIN,24))
    bpy.ops.object.empty_add(location=(0.6*b,0,1.9));sh=add(bpy.context.object);o3=(0.6*b,0,1.9)
    add(cyl((0.6*b,0,1.5),0.11*b,0.8,SH,(0,math.radians(8),0)),sh,o3);add(sph((0.65*b,0,1.05),(0.11,0.11,0.11),SKIN,24),sh,o3)
    bpy.ops.object.empty_add(location=(0,0,2.55));head=add(bpy.context.object);O=(0,0,2.55);hd=lambda o:add(o,head,O)
    hs=c.get('head','square')
    if hs=='square': hd(cube((0,0,2.6),(0.5,0.42,0.55),SKIN,0.25,2))
    elif hs=='oval': hd(sph((0,0,2.62),(0.44,0.42,0.62),SKIN))
    else: hd(sph((0,0,2.6),(0.52,0.46,0.55),SKIN))
    st=c.get('hair_style','short')
    if st!='bald':
        hd(cube((0,0.05,3.12),(0.52,0.44,0.14),HAIR,0.1,2))
        if st=='spiky':
            for k in range(6): hd(cone((-0.4+k*0.16,0,3.3),0.1,0.3,HAIR,8))
        elif st=='curly':
            for k in range(14): a=k*0.45;hd(sph((0.48*math.cos(a),0.4*math.sin(a),3.05+0.08*math.sin(k)),(0.15,0.15,0.15),HAIR,16))
        else:
            for k in range(6): hd(sph((-0.4+k*0.16,-0.36,3.02),(0.14,0.1,0.1),HAIR,24))
        if st=='long':
            hd(cube((0,0.35,2.55),(0.55,0.15,0.55),HAIR,0.1,2))
            for s in(-1,1): hd(cube((s*0.52,0.05,2.6),(0.07,0.35,0.5),HAIR,0.05,2))
    else: hd(sph((0,0.05,2.95),(0.48,0.4,0.25),SKIN))
    for s in(-1,1): hd(sph((s*0.52,0,2.55),(0.06,0.1,0.14),SKIN,24))
    droopy=c.get('eyes','normal')=='droopy'
    for xx in(-0.2,0.2):
        hd(sph((xx,-0.4,2.68),(0.13,0.07,0.12),WHITE,32));hd(sph((xx,-0.46,2.66),(0.05,0.02,0.05),BLACK,24))
        hd(sph((xx,-0.405,2.71 if droopy else 2.82),(0.145,0.08,0.13),SKIN,32))
        ang=0.25*(xx>0 and 1 or -1) if c.get('expression')=='angry' else 0
        hd(cube((xx,-0.43,2.86),(0.13,0.02,0.025),HAIR,0.01,rot=(0,ang,0)))
        if fem: hd(cube((xx+(0.12 if xx>0 else -0.12),-0.46,2.76),(0.04,0.01,0.01),BLACK))
    if c.get('glasses'):
        G=mat('gl','#111111',0.2)
        for xx in(-0.2,0.2):
            bpy.ops.mesh.primitive_torus_add(location=(xx,-0.5,2.67),rotation=(math.pi/2,0,0),major_radius=0.15,minor_radius=0.015);hd(fin(bpy.context.object,G))
        hd(cube((0,-0.5,2.7),(0.05,0.01,0.01),G))
    hd(sph((0,-0.47,2.52),(0.07,0.06,0.08),SKIN,24))
    if c.get('moustache'): hd(cube((0,-0.46,2.41),(0.15,0.03,0.035),HAIR,0.02,1))
    if c.get('beard'): hd(sph((0,-0.3,2.22),(0.42,0.2,0.2),HAIR))
    if c.get('hat'): hd(cyl((0,0,3.25),0.75,0.04,mat('hat','#c8a060',0.7)));hd(cyl((0,0,3.4),0.45,0.3,mat('hat','#c8a060',0.7)))
    mz=2.3
    mouth=hd(sph((0,-0.42,mz),(0.09,0.03,0.015),MOUTH,32))
    if c.get('expression')=='happy': hd(sph((0,-0.41,mz+0.02),(0.12,0.02,0.02),WHITE,24))
    sweat=[hd(sph((xx,-0.35,2.9),(0.03,0.02,0.045),mat('sw',(0.5,0.8,1),0.05),16)) for xx in(-0.45,0.47)] if c.get('sweat') else []
    return dict(root=root,sh=sh,head=head,mouth=mouth,sweat=sweat,x=x)
def setup_render(res,samples,cam_loc=(0.75,-6.6,2.0)):
    sc=bpy.context.scene;r=sc.render;r.engine='CYCLES';sc.cycles.device='CPU'
    try:
        pr=bpy.context.preferences.addons['cycles'].preferences
        for typ in ('OPTIX','CUDA','HIP','METAL','ONEAPI'):
            try: pr.compute_device_type=typ
            except TypeError: continue
            pr.get_devices();devs=[d for d in pr.devices if d.type==typ]
            if devs:
                for d in pr.devices: d.use=(d.type==typ)
                sc.cycles.device='GPU';print('GPU:',typ,[d.name for d in devs]);break
    except Exception as e: print('sin GPU:',e)
    if sc.cycles.device=='CPU': print('Render en CPU')
    sc.cycles.samples=samples;sc.cycles.use_denoising=True;sc.cycles.max_bounces=4
    r.resolution_x=res;r.resolution_y=res*16//9;r.use_persistent_data=True
    r.image_settings.file_format='JPEG';r.image_settings.quality=92
    sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Punchy';sc.view_settings.exposure=-0.4
    bpy.ops.object.camera_add(location=cam_loc,rotation=(math.radians(88),0,0));cam=bpy.context.object;sc.camera=cam;cam.data.lens=36
    return cam
