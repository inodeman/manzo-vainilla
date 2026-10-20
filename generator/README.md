# Generador de episodios 3D (Manzo Vainilla y otros)

Escribe un guion (YAML o JSON) y genera con **un solo comando** un video vertical 1080x1920 en 3D:
voz (Piper TTS, ritmo normal/pausado) → render 3D en Blender (Cycles, GPU automática o CPU) →
movimiento de boca sincronizado con el audio → subtítulos + título → **MP4 + miniatura**.

> Todos los personajes son caricaturas procedurales ficticias, hechas con figuras geométricas. No se usan fotos.

## Uso rápido
```bash
python3 make_episode.py ejemplos/manzo_ep1.json            # calidad final 1080x1920
python3 make_episode.py ejemplos/mini_prueba.yaml --preview # prueba rápida (360x640, 4 muestras)
```
Salida: `ejemplos/salida_<nombre>/<nombre>.mp4` y `<nombre>_thumb.jpg`.

Opciones: `--res 720` (ancho), `--samples 16` (calidad Cycles), `--step 2` (renderiza 1 de cada 2 cuadros = animación a 12 fps; `--step 1` para 24 fps reales), `--out carpeta`.
Variables de entorno: `BLENDER=/ruta/blender`, `PIPER=/ruta/piper`, `VOICES=/carpeta/voces`, `KEEP_FRAMES=1`.

## Describir personajes con texto
En lugar de poner los parámetros uno por uno, escribe una descripción:
```yaml
characters:
  - name: Manzo
    descripcion: "hombre alto, cara cuadrada, pelo negro corto, camisa azul, sin bigote, cara aburrida, gordito"
    shirt: "#0a3fb8"   # los parámetros explícitos SIEMPRE ganan sobre la descripción
```
Vista previa en PNG:
```bash
python3 describe_character.py "mujer bajita, cara redonda, pelo rubio largo, lentes, vestido rojo, feliz" -o maria.png
```
Palabras reconocidas (español e inglés):
| Rasgo | Ejemplos |
|---|---|
| género | hombre, mujer, señora, chica, woman, man |
| estatura | alto, bajo, bajito, chaparro, tall, short |
| complexión | gordo, gordito, panzón, flaco, delgado, musculoso |
| cara | cuadrada, redonda, ovalada/alargada |
| piel | piel clara, piel morena, piel oscura, tez morena clara |
| pelo | pelo negro/castaño/rubio/canoso/pelirrojo, corto, largo, rizado, parado, calvo |
| vello facial | bigote / sin bigote, barba / sin barba |
| accesorios | lentes, gafas, sombrero, gorra, corbata (color), sin corbata |
| ropa | camisa/playera/traje/saco/vestido + color; pantalón/jeans/falda + color |
| expresión | aburrido, cansado, apático (ojos caídos), feliz, enojado, nervioso (sudor) |
| voz | automática por género; "voz grave" usa la del narrador |

Colores: negro, blanco, azul, azul marino, celeste, rojo, verde, amarillo, naranja, morado, rosa, gris, café, beige/crema/vainilla, dorado, guinda.

## Describir escenarios con texto
```yaml
scenes:
  - escenario: {descripcion: "oficina vieja de gobierno, escritorio con papeles, ventana de noche"}
  - escenario: {descripcion: "plaza del pueblo con kiosco, día soleado", floor: "#a59a8a"}
```
Si una escena no trae `escenario`, se reutiliza el anterior. Vista previa:
```bash
python3 describe_set.py "calle de noche con faroles y un carro, lloviendo" -o calle.png
```
| Rasgo | Palabras |
|---|---|
| lugar | oficina/gobierno/despacho, salón de clases/escuela, cocina, casa/sala/cuarto, calle/avenida, plaza/zócalo, parque/jardín, playa |
| interior/exterior | automático según el lugar |
| hora | mañana, día, tarde/atardecer, noche |
| clima | soleado, nublado, lluvia |
| estado | viejo/antiguo/deteriorado |
| colores | pared(es) <color>, piso <color> |
| utilería | escritorio, sillas, papeles, ventana, puerta, plantas, árboles, kiosco, bancas, carro, faroles, sofá, tele, pizarrón, bandera, sombrilla, refri, estufa |

## Formato del guion
```yaml
title: "Manzo Vainilla"
subtitle: "(personaje ficticio · sátira)"
characters:
  - {name: Narrador, voice: es_MX-claude-high.onnx, on_screen: false}
  - {name: Manzo, voice: es_MX-ald-medium.onnx, descripcion: "...", subtitle_color: "&H0000FFFF"}
scenes:
  - escenario: {descripcion: "..."}
    board: "texto del pizarrón/letrero"         # o {before: "2 + 2 = ...", text: "2 + 2 = 5 ?", reveal_at: 3.2}
    sign: {text: "PRÉSTAMO #47", signature: "Manzo~", signer: Manzo}   # papel que se firma
    counter: {label: "DEUDA: $", start: 1000000, growth: 1.9}          # contador que crece
    camera: close                                # wide (por defecto) o close
    lines:
      - {speaker: Manzo, text: "Gobernar está difícil..."}
thumbnail: {scene: 1, at: 4.5, text: "¡NO SABE SUMAR!", subtext: "...y pide otro préstamo"}
```
`length_scale` por personaje controla la velocidad de la voz (1.0 normal, 1.05–1.15 más pausado).

## Instalación
Necesitas **Python 3.9+**, **Blender 4.x**, **ffmpeg** (con libass) y **Piper** + voces.

### Linux
```bash
sudo apt install python3 python3-pip ffmpeg
wget https://download.blender.org/release/Blender4.2/blender-4.2.3-linux-x64.tar.xz
sudo tar -xf blender-4.2.3-linux-x64.tar.xz -C /opt   # se detecta solo en /opt/blender*/
pip install piper-tts pyyaml
```
### macOS
```bash
brew install python ffmpeg
brew install --cask blender           # usa GPU Metal automáticamente en Apple Silicon
pip3 install piper-tts pyyaml
```
### Windows
1. Instala Python desde python.org (marca "Add to PATH").
2. Instala Blender desde blender.org (se busca en `C:\Program Files\Blender Foundation\`).
3. ffmpeg: `winget install Gyan.FFmpeg`.
4. `pip install piper-tts pyyaml`
5. Ejecuta: `python make_episode.py ejemplos\manzo_ep1.json`

### Voces (Piper)
Descarga los `.onnx` y `.onnx.json` de https://huggingface.co/rhasspy/piper-voices (carpeta `es/es_MX/...`)
y ponlos en `generator/voices/` (o define `VOICES`). Usadas: `es_MX-ald-medium`, `es_MX-claude-high`, `es_AR-daniela-high`.

### GPU
Se prueba automáticamente OPTIX → CUDA → HIP → METAL → ONEAPI; si no hay ninguna, se usa CPU.
En CPU, usa `--preview` para pruebas y `--samples 12 --step 2` para finales más rápidos.

## Archivos
- `make_episode.py` — orquestador (TTS, audio, Blender, subtítulos, MP4, miniatura)
- `scene3d.py` — escena animada dentro de Blender
- `lib3d.py` — biblioteca procedural: escenarios, utilería y personajes
- `parse_desc.py` — interpreta descripciones de texto (personajes y escenarios)
- `describe_character.py`, `describe_set.py`, `preview3d.py` — vistas previas PNG
- `ejemplos/` — `manzo_ep1.json` (episodio completo) y `mini_prueba.yaml` (prueba corta con personaje y escenarios descritos)
