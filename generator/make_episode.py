#!/usr/bin/env python3
"""Generador de episodios 3D: python3 make_episode.py episodio.yaml [--preview] [--res 540] [--samples 8]"""
import json,os,sys,subprocess,shutil,wave,argparse,platform,glob
HERE=os.path.dirname(os.path.abspath(__file__))
def load(p):
    t=open(p,encoding='utf-8').read()
    if p.endswith(('.yaml','.yml')):
        import yaml;return yaml.safe_load(t)
    return json.loads(t)
def find_blender():
    for c in [os.environ.get('BLENDER'),shutil.which('blender'),*sorted(glob.glob('/opt/blender/*/blender')),
              '/Applications/Blender.app/Contents/MacOS/Blender',*sorted(glob.glob(r'C:\Program Files\Blender Foundation\Blender*\blender.exe'))]:
        if c and os.path.exists(c): return c
    sys.exit('No encuentro Blender. Define la variable BLENDER=/ruta/a/blender')
def piper_cmd(): return os.environ.get('PIPER') or shutil.which('piper') or 'piper'
def main():
    ap=argparse.ArgumentParser();ap.add_argument('script');ap.add_argument('--res',type=int,default=1080)
    ap.add_argument('--samples',type=int,default=16);ap.add_argument('--fps',type=int,default=24)
    ap.add_argument('--step',type=int,default=2,help='renderizar 1 de cada N cuadros (2 = animación a 12 fps)')
    ap.add_argument('--preview',action='store_true',help='baja resolución y pocas muestras');ap.add_argument('--out')
    a=ap.parse_args()
    if a.preview: a.res,a.samples=360,4
    ep=load(a.script);base=os.path.splitext(os.path.basename(a.script))[0]
    out=a.out or os.path.join(os.path.dirname(os.path.abspath(a.script)),'salida_'+base);os.makedirs(out,exist_ok=True)
    work=os.path.join(out,'work');frames=os.path.join(work,'frames');os.makedirs(frames,exist_ok=True)
    voices=os.environ.get('VOICES',os.path.join(HERE,'voices'))
    sys.path.insert(0,HERE);import parse_desc as PD
    for i,c in enumerate(ep['characters']):
        d=c.get('descripcion') or c.get('description')
        if d: ep['characters'][i]=c=PD.merge(PD.parse_character(d),c);print('Personaje',c['name'],'->',{k:v for k,v in c.items() if k!='name'})
        c.setdefault('voice','es_MX-ald-medium.onnx')
    last=PD.parse_set('oficina con escritorio y pizarron')
    for s in ep['scenes']:
        e=s.get('escenario') or s.get('set')
        if e is not None:
            if isinstance(e,str): e={'descripcion':e}
            d=e.get('descripcion') or e.get('description')
            last=PD.merge(PD.parse_set(d) if d else last,e);print('Escenario ->',last)
        s['_set']=last
    chars={c['name']:c for c in ep['characters']}
    # 1) TTS
    t=float(ep.get('start_pad',0.4));gap=float(ep.get('gap',0.3));lines=[];n=0
    for si,s in enumerate(ep['scenes']):
        for ln in s['lines']:
            c=chars[ln['speaker']];wav=os.path.join(work,f'l{n:03d}.wav')
            model=c['voice'] if os.path.isabs(c['voice']) else os.path.join(voices,c['voice'])
            if not os.path.exists(wav):
                subprocess.run([piper_cmd(),'-m',model,'--length_scale',str(c.get('length_scale',1.05)),'-f',wav],
                               input=ln['text'].encode(),check=True,stderr=subprocess.DEVNULL)
            w=wave.open(wav);d=w.getnframes()/w.getframerate()
            lines.append(dict(start=t,end=t+d,speaker=ln['speaker'],text=ln['text'],scene=si,wav=wav));t+=d+gap;n+=1
    total=t+float(ep.get('end_pad',0.2))
    # 2) mezcla de audio
    inp=sum([['-i',l['wav']] for l in lines],[])
    flt=';'.join(f"[{i}]adelay={int(l['start']*1000)}:all=1[a{i}]" for i,l in enumerate(lines))
    flt+=';'+''.join(f'[a{i}]' for i in range(len(lines)))+f'amix=inputs={len(lines)}:normalize=0,apad,atrim=0:{total}'
    audio=os.path.join(work,'audio.wav')
    subprocess.run(['ffmpeg','-y','-v','error',*inp,'-filter_complex',flt,audio],check=True)
    # escenas: inicio/fin
    for si,s in enumerate(ep['scenes']):
        ls=[l for l in lines if l['scene']==si];s['_start']=ls[0]['start'];s['_end']=ls[-1]['end']+gap
    job=dict(ep=ep,lines=lines,total=total,audio=audio,frames=frames,res=a.res,samples=a.samples,fps=a.fps,step=a.step)
    jp=os.path.join(work,'job.json');json.dump(job,open(jp,'w',encoding='utf-8'),ensure_ascii=False)
    # 3) render Blender
    nice=['nice','-n','15'] if platform.system()!='Windows' and shutil.which('nice') else []
    subprocess.run(nice+[find_blender(),'-b','-P',os.path.join(HERE,'scene3d.py'),'--',jp],check=True)
    # 4) subtítulos + título + video
    NF=int(total*a.fps)
    for f in range(NF):
        p=os.path.join(frames,f'{f:05d}.jpg')
        if not os.path.exists(p): shutil.copy(os.path.join(frames,f'{f-f%a.step:05d}.jpg'),p)
    W=a.res;H=W*16//9;k=W/1080
    ts=lambda x:f'0:{int(x//60):02d}:{x%60:05.2f}'
    hdr=f'[Script Info]\nPlayResX: {W}\nPlayResY: {H}\n[V4+ Styles]\nFormat: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding\n'
    st=lambda n,sz,col,bs,ol,al,mv,back='&HA0000000':f'Style: {n},DejaVu Sans,{int(sz*k)},{col},&H0,&H001A3A5B,{back},1,0,0,0,100,100,0,0,{bs},{max(1,int(ol*k))},0,{al},{int(40*k)},{int(40*k)},{int(mv*k)},1\n'
    sty=st('Title',118,'&H00A0E9FF',1,8,8,110)+st('Sub2',40,'&H00FFFFFF',1,3,8,245)+st('Big',96,'&H00FFFFFF',3,22,2,260,'&H002B39C0')+st('Small',58,'&H00A0E9FF',3,14,2,150,'&H002B39C0')
    for c in chars.values(): sty+=st('C_'+c['name'].replace(' ','_'),56,c.get('subtitle_color','&H00FFFFFF'),3,14,2,150)
    ev='[Events]\nFormat: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text\n'
    E=ts(total);ev+=f"Dialogue: 0,0:00:00.00,{E},Title,,0,0,0,,{{\\fad(300,0)}}{ep['title']}\n"
    if ep.get('subtitle'): ev+=f"Dialogue: 0,0:00:00.00,{E},Sub2,,0,0,0,,{ep['subtitle']}\n"
    for l in lines: ev+=f"Dialogue: 0,{ts(l['start'])},{ts(l['end'])},C_{l['speaker'].replace(' ','_')},,0,0,0,,{l['text']}\n"
    ass=os.path.join(work,'subs.ass');open(ass,'w',encoding='utf-8').write(hdr+sty+ev)
    mp4=os.path.join(out,base+'.mp4')
    esc=lambda p:p.replace('\\','/').replace(':','\\:')
    subprocess.run(nice+['ffmpeg','-y','-v','error','-framerate',str(a.fps),'-i',os.path.join(frames,'%05d.jpg'),'-i',audio,
        '-vf',f'ass={esc(ass)}','-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest',mp4],check=True)
    th=ep.get('thumbnail',{});tass=os.path.join(work,'thumb.ass')
    tev='[Events]\nFormat: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text\n'+f"Dialogue: 0,0:00:00.00,0:00:05.00,Title,,0,0,0,,{ep['title']}\n"
    if th.get('text'): tev+=f"Dialogue: 0,0:00:00.00,0:00:05.00,Big,,0,0,0,,{th['text']}\n"
    if th.get('subtext'): tev+=f"Dialogue: 0,0:00:00.00,0:00:05.00,Small,,0,0,0,,{th['subtext']}\n"
    open(tass,'w',encoding='utf-8').write(hdr+sty+tev)
    jpg=os.path.join(out,base+'_thumb.jpg')
    subprocess.run(['ffmpeg','-y','-v','error','-i',os.path.join(work,'thumb.jpg'),'-vf',f'ass={esc(tass)}','-q:v','2',jpg],check=True)
    if not os.environ.get('KEEP_FRAMES'): shutil.rmtree(frames)
    print('LISTO:',mp4,jpg)
if __name__=='__main__': main()
