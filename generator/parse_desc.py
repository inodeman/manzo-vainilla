"""Parsers de descripciones en texto libre (español/inglés) -> parámetros de personaje y escenario. Sin APIs externas."""
import re,unicodedata
def norm(t): return ''.join(c for c in unicodedata.normalize('NFD',t.lower()) if unicodedata.category(c)!='Mn')
COLORS={'negro|negra|black':'#0a0a0a','blanco|blanca|white':'#f0f0f0','azul marino|navy':'#0b1f4d','azul claro|celeste|light blue':'#7fb2e5',
 'azul|blue':'#0a3fb8','rojo|roja|red':'#b81010','verde|green':'#1f7a2e','amarillo|amarilla|yellow':'#e8c420','naranja|orange':'#e06a10',
 'morado|morada|purpura|purple':'#6a2a9a','rosa|rosado|pink':'#e87aa8','gris|gray|grey':'#777777','cafe|marron|brown':'#5a3518',
 'castano|castana':'#4a2c14','rubio|rubia|blond|blonde|guero|guera':'#d8b04a','pelirrojo|pelirroja|redhead|ginger':'#b0451a',
 'canoso|canosa|cano|plateado|gray-haired':'#bdbdbd','beige|crema|cream|vainilla':'#e8dcb0','dorado|gold':'#c9a227','vino|guinda':'#6b0f1a'}
def color_after(t,words):
    """color que aparece cerca (después o antes) de alguna palabra clave"""
    for w in words:
        m=re.search(rf'\b{w}\w*\b((?:\s+\w+){{0,3}})',t)
        if m:
            seg=m.group(1)
            for k,v in COLORS.items():
                if re.search(rf'\b({k})\b',seg): return v
        m=re.search(rf'((?:\w+\s+){{0,2}})\b{w}\w*\b',t)
    return None
def has(t,pat): return re.search(rf'\b({pat})\b',t) is not None
SKIN={'muy claro|palido|palida|pale':'#f2d3bd','claro|clara|blanco de piel|fair|light skin':'#e8bfa0','moreno claro|morena clara|trigueno|triguena|olive':'#c99872',
 'moreno|morena|tan|brown skin':'#a8724c','oscuro|oscura|negro de piel|dark skin|piel negra|afro':'#5e3a22'}
def parse_character(text):
    t=norm(text);p={}
    p['gender']='female' if has(t,'mujer|senora|chica|nina|female|woman|girl|ella|abuela|alcaldesa') else 'male'
    p['height']=1.15 if has(t,'alto|alta|tall|grandote') else 0.85 if has(t,'bajo|baja|bajito|bajita|chaparro|chaparra|short|pequeno') else 1.0
    p['build']=1.3 if has(t,'gordo|gorda|gordito|gordita|panzon|robusto|fat|chubby|llenito') else 0.8 if has(t,'flaco|flaca|delgado|delgada|thin|skinny') else 1.15 if has(t,'musculoso|fuerte|muscular') else 1.0
    p['head']='square' if has(t,'cuadrada|cuadrado|square') else 'round' if has(t,'redonda|redondo|round') else 'oval' if has(t,'ovalada|alargada|oval|long face') else 'square'
    p['skin']='#d9ad8f'
    for k,v in SKIN.items():
        if re.search(rf'(piel|skin|tez)\s+({k})\b|\b({k})\s+(skin)',t): p['skin']=v
    hc=color_after(t,['pelo','cabello','hair'])
    for k in ['rubio|rubia|blond|blonde|guero|guera','pelirrojo|pelirroja|redhead|ginger','canoso|canosa|cano']:
        if has(t,k): hc=COLORS[k]
    p['hair']=hc or '#0a0a0a'
    p['hair_style']='bald' if has(t,'calvo|calva|pelon|bald') else 'long' if has(t,'largo|larga|long|melena|cola de caballo|ponytail') else 'curly' if has(t,'rizado|chino|curly|afro') else 'spiky' if has(t,'parado|picos|spiky|erizo') else 'short'
    if p['gender']=='female' and not has(t,'corto|short|calva'): p['hair_style']=p['hair_style'] if p['hair_style']!='short' else 'long'
    p['moustache']=has(t,'bigote|bigotes|mustache|moustache') and not has(t,'sin bigote|no mustache|without mustache')
    p['beard']=has(t,'barba|beard|barbon') and not has(t,'sin barba|no beard')
    p['glasses']=has(t,'lentes|anteojos|gafas|glasses|espejuelos') and not has(t,'sin lentes|sin gafas|no glasses')
    p['shirt']=color_after(t,['camisa','playera','saco','traje','blusa','shirt','jacket','suit','sueter','vestido','dress']) or '#0a3fb8'
    p['pants']=color_after(t,['pantalon','pantalones','jeans','falda','pants','skirt']) or ('#1b2f5a' if has(t,'jeans|mezclilla') else '#141418')
    p['outfit']='suit' if has(t,'traje|saco|suit|elegante|formal') else 'tshirt' if has(t,'playera|camiseta|t-shirt|tshirt') else 'dress' if has(t,'vestido|dress') else 'shirt'
    p['tie']=(color_after(t,['corbata','tie']) or '#c01010') if (has(t,'corbata|tie') or p['outfit']=='suit') and not has(t,'sin corbata|no tie') else False
    p['hat']=has(t,'sombrero|gorra|hat|cap|tejana')
    p['sweat']=has(t,'nervioso|nerviosa|sudando|sudoroso|nervous|sweat')
    p['eyes']='droopy' if has(t,'aburrido|aburrida|cansado|cansada|apatico|apatica|flojo|floja|bored|tired|sleepy|desganado|sueno') else 'normal'
    p['expression']='happy' if has(t,'feliz|alegre|sonriente|happy|smiling') else 'angry' if has(t,'enojado|enojada|angry|furioso') else 'bored' if p['eyes']=='droopy' else 'neutral'
    p['voice']=('es_AR-daniela-high.onnx' if p['gender']=='female' else 'es_MX-ald-medium.onnx')
    if has(t,'voz grave|voz profunda|deep voice|narrador'): p['voice']='es_MX-claude-high.onnx'
    return p
SETS={'office':'oficina|office|despacho|ayuntamiento|gobierno|palacio municipal','classroom':'salon de clases|aula|escuela|classroom|school',
 'kitchen':'cocina|kitchen','house':'casa|sala|living|recamara|cuarto|house|home|departamento','street':'calle|avenida|street|road|banqueta',
 'plaza':'plaza|zocalo|kiosco|kiosko|square','park':'parque|park|jardin|bosque','beach':'playa|beach|mar|costa'}
OUTDOOR={'street','plaza','park','beach'}
PROPS={'desk':'escritorio|desk|mesa','chairs':'silla|sillas|chair','papers':'papeles|documentos|papers|expedientes','window':'ventana|window',
 'door':'puerta|door','plants':'planta|plantas|maceta|plant','trees':'arbol|arboles|tree|trees|palmera','kiosk':'kiosco|kiosko|kiosk|gazebo',
 'bench':'banca|bancas|banco|bench','car':'carro|coche|auto|car','lampposts':'farol|faroles|poste|postes|lamp post|streetlight','sofa':'sofa|sillon|couch',
 'tv':'tele|television|tv','board':'pizarron|pizarra|chalkboard|blackboard','flag':'bandera|flag','umbrella':'sombrilla|umbrella','fridge':'refrigerador|refri|fridge','stove':'estufa|stove'}
DEFAULT_PROPS={'office':['desk','board','window','flag'],'classroom':['board','desk','chairs'],'kitchen':['fridge','stove','window'],'house':['sofa','tv','window','plants'],
 'street':['lampposts','car','trees'],'plaza':['kiosk','bench','trees','lampposts'],'park':['trees','bench','plants'],'beach':['umbrella','trees']}
def parse_set(text):
    t=norm(text);p={'type':'office'}
    for k,v in SETS.items():
        if has(t,v): p['type']=k;break
    p['outdoor']=p['type'] in OUTDOOR
    p['time']='night' if has(t,'noche|night|nocturno') else 'sunset' if has(t,'atardecer|tarde|sunset|ocaso') else 'morning' if has(t,'manana|amanecer|morning') else 'day'
    p['weather']='rain' if has(t,'lluvia|lloviendo|rain|rainy') else 'cloudy' if has(t,'nublado|cloudy|gris') else 'sunny'
    p['old']=has(t,'vieja|viejo|antigua|old|abandonada|deteriorada')
    p['wall']=color_after(t,['pared','paredes','muro','wall']) or ('#9c8a6e' if p['old'] else '#c4ad93')
    p['floor']=color_after(t,['piso','suelo','floor']) or {'beach':'#e6d29a','park':'#4f8a3a','plaza':'#a59a8a','street':'#4a4a4e'}.get(p['type'],'#9e7a58')
    props=[k for k,v in PROPS.items() if has(t,v)]
    p["props"]=list(dict.fromkeys(props+DEFAULT_PROPS[p["type"]])) if len(props)<2 else props
    if p['type']=='office' and 'board' not in p['props']: p['props'].append('board')
    return p
def merge(desc_params,explicit):
    out=dict(desc_params);out.update({k:v for k,v in explicit.items() if k not in('descripcion','description')});return out
