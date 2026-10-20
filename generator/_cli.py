import sys,os,json,subprocess,tempfile,argparse
HERE=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,HERE)
import parse_desc as PD
from make_episode import find_blender
def run(kind):
    ap=argparse.ArgumentParser();ap.add_argument('texto');ap.add_argument('-o','--out');ap.add_argument('--res',type=int,default=540);ap.add_argument('--samples',type=int,default=16)
    a=ap.parse_args()
    p=PD.parse_character(a.texto) if kind=='character' else PD.parse_set(a.texto)
    print(json.dumps(p,ensure_ascii=False,indent=2))
    out=a.out or f'preview_{kind}.png'
    j={kind:p,'res':a.res,'samples':a.samples}
    if kind=='character': j['set']={'type':'office','props':[],'wall':'#c4ad93'};j['close']=True
    f=tempfile.NamedTemporaryFile('w',suffix='.json',delete=False,encoding='utf-8');json.dump(j,f,ensure_ascii=False);f.close()
    subprocess.run([find_blender(),'-b','-P',os.path.join(HERE,'preview3d.py'),'--',f.name,out],check=True,stdout=subprocess.DEVNULL)
    print('Vista previa:',os.path.abspath(out))
