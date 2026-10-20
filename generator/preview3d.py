# blender -b -P preview3d.py -- params.json salida.png
import bpy,sys,os,json,math
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import lib3d as L3
a=sys.argv[sys.argv.index('--')+1:];j=json.load(open(a[0],encoding='utf-8'))
bpy.ops.wm.read_factory_settings(use_empty=True)
L3.build_set(j.get('set') or {'type':'office','props':[]})
if j.get('character'):
    c=L3.build_character(j['character'],-0.35)
cam=L3.setup_render(j.get('res',540),j.get('samples',16))
if j.get('character') and j.get('close'): cam.location=(-0.35,-5.0,2.0)
sc=bpy.context.scene;sc.render.image_settings.file_format='PNG';sc.render.filepath=os.path.abspath(a[1]);bpy.ops.render.render(write_still=True)
