import wave,math,subprocess,os,random
from PIL import Image,ImageDraw,ImageFont
W,H,FPS=1080,1920,24
lines=[l.strip().split('|',1) for l in open('script.txt')]
segs=[];t=0.4
for i,(who,txt) in enumerate(lines):
    w=wave.open(f'l{i}.wav');d=w.getnframes()/w.getframerate();segs.append((t,t+d,who,txt,i));t+=d+0.3
TOT=round(t+0.2,2)
# build audio
inp=' '.join(f'-i l{i}.wav' for i in range(len(lines)))
flt=';'.join(f'[{i}]adelay={int(s[0]*1000)}:all=1[a{i}]' for i,s in enumerate(segs))
mix=''.join(f'[a{i}]' for i in range(len(segs)))+f'amix=inputs={len(segs)}:normalize=0,apad,atrim=0:{TOT}'
subprocess.run(f'ffmpeg -y -v error {inp} -filter_complex "{flt};{mix}" audio.wav',shell=True,check=True)
F='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
ft=lambda s:ImageFont.truetype(F,s)
def wrap(txt,n=24):
    out,cur=[], ''
    for w in txt.split():
        if len(cur)+len(w)>n: out.append(cur);cur=w
        else: cur=(cur+' '+w).strip()
    return out+[cur]
def manzo(d,cx,cy,mouth,t,sweat=True,arm=0):
    # body: vanilla cream suit
    d.rounded_rectangle([cx-170,cy+150,cx+170,cy+560],60,fill='#2f6fd6',outline='#7a5c2e',width=8)
    d.polygon([(cx-40,cy+150),(cx+40,cy+150),(cx,cy+260)],fill='white')
    d.polygon([(cx-18,cy+165),(cx+18,cy+165),(cx+10,cy+330),(cx,cy+350),(cx-10,cy+330)],fill='#c0392b')
    for s in(-1,1):
        ang=arm if s==1 else 0
        ex=cx+s*230; ey=cy+330-ang
        d.line([(cx+s*160,cy+200),(ex,ey)],fill='#2f6fd6',width=60)
        d.ellipse([ex-35,ey-35,ex+35,ey+35],fill='#f1c9a5',outline='#7a5c2e',width=5)
    d.rectangle([cx-120,cy+560,cx-40,cy+700],fill='#3a3a4a');d.rectangle([cx+40,cy+560,cx+120,cy+700],fill='#3a3a4a')
    d.ellipse([cx-150,cy+680,cx-20,cy+730],fill='#5b3a1a');d.ellipse([cx+20,cy+680,cx+150,cy+730],fill='#5b3a1a')
    # square-ish head
    d.rounded_rectangle([cx-210,cy-280,cx+210,cy+180],70,fill='#f1c9a5',outline='#3a2a1a',width=8)
    d.rounded_rectangle([cx-215,cy-320,cx+215,cy-150],50,fill='#111111')
    for k in range(5): d.polygon([(cx-200+k*90,cy-160),(cx-160+k*90,cy-100),(cx-120+k*90,cy-160)],fill='#111111')
    for s in(-1,1):
        ex=cx+s*85
        d.ellipse([ex-48,cy-80,ex+48,cy+5],fill='white',outline='black',width=5)
        d.ellipse([ex-16,cy-40,ex+16,cy-8],fill='black')
        d.chord([ex-52,cy-86,ex+52,cy+20],180,360,fill='#e0b48f',outline='black',width=5)  # droopy lids
        d.line([ex-45,cy-110,ex+45,cy-105-s*0],fill='#111',width=10)
    d.ellipse([cx-28,cy+10,cx+28,cy+60],fill='#e8a07a')
    mo=int(6+40*mouth)
    d.ellipse([cx-55,cy+95,cx+55,cy+95+mo],fill='#6b1f1f',outline='black',width=5)
    if sweat:
        for k in range(3):
            ph=(t*0.8+k*0.33)%1
            x=cx+(-200 if k%2 else 190);y=cy-160+ph*250
            d.polygon([(x,y-25),(x-14,y+8),(x+14,y+8)],fill='#7ec8ff');d.ellipse([x-14,y-6,x+14,y+20],fill='#7ec8ff')
os.makedirs('frames',exist_ok=True)
import array
w=wave.open('audio.wav');sr=w.getframerate();ch=w.getnchannels()
a=array.array('h',w.readframes(w.getnframes()))[::ch]
def amp(t):
    i=int(t*sr);s=a[i:i+sr//FPS] or [0]
    return min(1,(sum(abs(x) for x in s)/len(s))/3500)
def frame(t,thumb=False):
    im=Image.new('RGB',(W,H),'#87CEEB');d=ImageDraw.Draw(im)
    d.rectangle([0,1250,W,H],fill='#6aa84f')
    # town hall
    d.rectangle([90,700,990,1250],fill='#e9d8b4',outline='#7a5c2e',width=6)
    d.polygon([(60,700),(540,480),(1020,700)],fill='#c97b4a')
    d.text((540,620),'PALACIO MUNICIPAL',font=ft(40),fill='white',anchor='mm')
    cur=[s for s in segs if s[0]<=t<s[1]]; idx=cur[0][4] if cur else -1
    sc=max([s[4] for s in segs if s[0]<=t] or [0])
    # props per scene
    if sc==1 or thumb:
        d.rectangle([600,820,1040,1120],fill='#1f4d2b',outline='#7a5c2e',width=12)
        p=min(1,max(0,(t-segs[1][0])/4)) if not thumb else 1
        txt='2 + 2 = '+('5 ?' if p>0.7 else '...')
        d.text((820,970),txt,font=ft(80),fill='white',anchor='mm')
    if sc>=2 and not thumb:
        d.rectangle([660,1050,1040,1400],fill='white',outline='black',width=5)
        d.text((850,1100),'PRÉSTAMO #47',font=ft(38),fill='black',anchor='mm')
        for k in range(5): d.line([700,1160+k*40,1000,1160+k*40],fill='#999',width=4)
        p=min(1,max(0,(t-segs[2][0]-1.5)/1.5))
        pts=[(700+i*6,1360+20*math.sin(i/3)) for i in range(int(50*p))]
        if len(pts)>1: d.line(pts,fill='#1a3cff',width=6)
    if sc==3 and not thumb:
        debt=int(1e6*1.9**((t-segs[3][0])*3))
        d.rounded_rectangle([90,1450,990,1600],30,fill='#c0392b')
        d.text((540,1525),f'DEUDA: ${debt:,}',font=ft(62),fill='white',anchor='mm')
    m=amp(t) if (idx>=0 and segs[idx][2]=='M') else 0
    bob=8*math.sin(t*4)
    manzo(d,330 if (sc>=1 or thumb) else 540,1000+bob-(0 if not thumb else 0),m,t,arm=(120 if sc==2 else 0))
    # title
    tf=ft(120);y=230+6*math.sin(t*2)
    for dx,dy in[(-6,0),(6,0),(0,-6),(0,6),(6,6)]: d.text((540+dx,y+dy),'Manzo Vainilla',font=tf,fill='#5b3a1a',anchor='mm')
    d.text((540,y),'Manzo Vainilla',font=tf,fill='#FFE9A0',anchor='mm')
    d.text((540,y+105),'(personaje ficticio · sátira)',font=ft(40),fill='#333',anchor='mm')
    if thumb:
        d.rounded_rectangle([60,1450,1020,1700],30,fill='#c0392b')
        d.text((540,1530),'¡NO SABE SUMAR!',font=ft(90),fill='white',anchor='mm')
        d.text((540,1630),'...y pide otro préstamo',font=ft(52),fill='#ffe9a0',anchor='mm')
    elif idx>=0:
        ls=wrap(segs[idx][3]);y0=1700
        d.rounded_rectangle([40,y0-20,1040,y0+len(ls)*62+10],25,fill=(0,0,0))
        for k,l in enumerate(ls): d.text((540,y0+k*62+25),l,font=ft(50),fill='yellow' if segs[idx][2]=='M' else 'white',anchor='mm')
    return im
frame(0,True).save('manzo_vainilla_thumb.jpg',quality=92)
for n in range(int(TOT*FPS)): frame(n/FPS).save(f'frames/{n:05d}.jpg',quality=90)
subprocess.run(f'ffmpeg -y -v error -framerate {FPS} -i frames/%05d.jpg -i audio.wav -c:v libx264 -pix_fmt yuv420p -crf 20 -c:a aac -b:a 160k -shortest manzo_vainilla.mp4',shell=True,check=True)
