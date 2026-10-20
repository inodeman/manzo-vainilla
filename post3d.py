import wave,os,subprocess
D='/workspace/manzo_vainilla';O='/tmp/mv3d'
lines=[l.strip().split('|',1) for l in open(f'{D}/script.txt')]
segs=[];t=0.4
for i,(who,txt) in enumerate(lines):
    w=wave.open(f'{D}/l{i}.wav');d=w.getnframes()/w.getframerate();segs.append((t,t+d,who,txt));t+=d+0.3
NF=int((t+0.2)*24)
for f in range(NF):
    p=f'{O}/{f:05d}.jpg'
    if not os.path.exists(p): os.symlink(f'{O}/{f-f%2:05d}.jpg',p)
ts=lambda x:f'0:{int(x//60):02d}:{x%60:05.2f}'
ass='''[Script Info]
PlayResX: 1080
PlayResY: 1920
[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Title,DejaVu Sans,118,&H00A0E9FF,&H0,&H001A3A5B,&H80000000,1,0,0,0,100,100,0,0,1,8,6,8,20,20,110,1
Style: Sub2,DejaVu Sans,40,&H00FFFFFF,&H0,&H00000000,&H0,1,0,0,0,100,100,0,0,1,3,0,8,20,20,245,1
Style: M,DejaVu Sans,56,&H0000FFFF,&H0,&H00000000,&HA0000000,1,0,0,0,100,100,0,0,3,14,0,2,60,60,150,1
Style: N,DejaVu Sans,56,&H00FFFFFF,&H0,&H00000000,&HA0000000,1,0,0,0,100,100,0,0,3,14,0,2,60,60,150,1
[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
'''
E=ts(t+0.2)
ass+=f'Dialogue: 0,0:00:00.00,{E},Title,,0,0,0,,{{\\fad(300,0)}}Manzo Vainilla\n'
ass+=f'Dialogue: 0,0:00:00.00,{E},Sub2,,0,0,0,,(personaje ficticio · sátira)\n'
for s,e,who,txt in segs: ass+=f'Dialogue: 0,{ts(s)},{ts(e)},{who},,0,0,0,,{txt}\n'
open(f'{D}/subs_3d.ass','w').write(ass)
subprocess.run(f'nice -n 15 ffmpeg -y -v error -framerate 24 -i {O}/%05d.jpg -i {D}/audio.wav -vf "ass={D}/subs_3d.ass" -c:v libx264 -preset slow -crf 19 -pix_fmt yuv420p -c:a aac -b:a 160k -shortest {D}/manzo_vainilla_3d.mp4',shell=True,check=True)
th=f'''[Script Info]
PlayResX: 1080
PlayResY: 1920
[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Title,DejaVu Sans,124,&H00A0E9FF,&H0,&H001A3A5B,&H80000000,1,0,0,0,100,100,0,0,1,9,6,8,20,20,110,1
Style: Big,DejaVu Sans,96,&H00FFFFFF,&H0,&H00000000,&H002B39C0,1,0,0,0,100,100,0,0,3,22,0,2,40,40,260,1
Style: Small,DejaVu Sans,58,&H00A0E9FF,&H0,&H00000000,&H002B39C0,1,0,0,0,100,100,0,0,3,14,0,2,40,40,150,1
[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
Dialogue: 0,0:00:00.00,0:00:05.00,Title,,0,0,0,,Manzo Vainilla
Dialogue: 0,0:00:00.00,0:00:05.00,Big,,0,0,0,,¡NO SABE SUMAR!
Dialogue: 0,0:00:00.00,0:00:05.00,Small,,0,0,0,,...y pide otro préstamo
'''
open('/tmp/th.ass','w').write(th)
subprocess.run(f'ffmpeg -y -v error -i {O}/thumb.jpg -vf ass=/tmp/th.ass -q:v 2 {D}/manzo_vainilla_3d_thumb.jpg',shell=True,check=True)
