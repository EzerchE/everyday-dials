"""Render packaged V7 images at native pixels; all captions are outside assets."""
from pathlib import Path
import json,os
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
FONT=Path(os.environ.get('WINDIR',r'C:\Windows'))/'Fonts/segoeui.ttf'
BOLD=FONT.with_name('segoeuib.ttf')
def tile(plugin,spec,direction=0,volume=42,active=False,muted=False,pressed=False):
    kind={2:'volume',0:'seek',1:'speed',3:'frame'}[int(spec['Id'].rsplit('-',1)[1])]
    suffix='-pressed' if pressed else '-left' if direction<0 else '-right' if direction>0 else ''
    state='-muted' if kind=='volume' and muted and (pressed or not direction) else ''
    return Image.open(Path(plugin)/('images/youtube-dials/dial-'+kind+state+suffix+'.png')).convert('RGB')
def preview(plugin,out,title='YouTube V7 — native controls',keyorder=None):
    plugin=Path(plugin);catalog={s['Id']:s for s in json.loads((plugin/'catalog.json').read_text())};keys={s['Id']:s for s in json.loads((plugin/'key-catalog.json').read_text())}
    im=Image.new('RGB',(1920,960),'#0D1015');d=ImageDraw.Draw(im)
    def text(x,y,s,size=24,color='#F1F1F3',bold=False):d.text((x,y),s,font=ImageFont.truetype(str(BOLD if bold else FONT),size),fill=color)
    text(55,22,title,38,bold=True);text(55,76,'Static packaged assets • no browser state or rate readback • not a hardware screenshot',21,'#A3ADB8')
    text(55,115,'NORMAL • native 144 × 144',17,'#A3ADB8');text(750,115,'HELD • native 144 × 144',17,'#A3ADB8')
    for index,semantic in enumerate(keyorder or [1,0,2,4,5,3,6,7]):
        s=keys['youtube-controls-key-'+str(semantic)]
        for pressed,x in [(False,55),(True,750)]:
            path=plugin/s['Image'];path=path.with_stem(path.stem+'-pressed') if pressed else path
            image=Image.open(path).convert('RGB');assert image.size==(144,144)
            im.paste(image,(x+(index%4)*156,146+(index//4)*156))
    text(1430,164,'Release restores neutral.',22)
    text(1430,205,'Direction lasts ~140 ms',22)
    text(1430,238,'after the last tick.',22)
    text(1430,295,'Reset labels an action.',22)
    text(1430,336,'Only Windows master mute',20,'#A3ADB8')
    text(1430,367,'has verified state readback.',20,'#A3ADB8')
    text(55,487,'NORMAL STRIP • four independent 200 × 100 canvases',18,'#A3ADB8')
    for i,semantic in enumerate([2,0,1,3]):
        spec=catalog['youtube-controls-'+str(semantic)];im.paste(tile(plugin,spec),(55+i*200,535))
    text(55,653,'Native 800 × 100 strip; no extra frame, glow or text layers.',18,'#A3ADB8')
    for x,label in [(990,'NORMAL'),(1215,'LEFT'),(1440,'RIGHT'),(1665,'HELD / TAP')]:text(x,474,label,17,'#A3ADB8')
    for row,semantic in enumerate([2,0,1,3]):
        spec=catalog['youtube-controls-'+str(semantic)]
        for col,direction in enumerate([0,-1,1,0]):im.paste(tile(plugin,spec,direction,pressed=col==3),(990+225*col,505+row*110))
    for i,semantic in enumerate([2,0,1,3]):
        icon=Image.open(plugin/('images/youtube-encoders/dial-'+{2:'volume',0:'seek',1:'speed',3:'frame'}[semantic]+'.png')).convert('RGBA');im.paste(icon,(55+i*156,705),icon)
    text(55,856,'Transparent editor symbols • supplied SVGs • 54 px optical bounds',18,'#A3ADB8')
    text(55,903,'Windows master volume first. Held rotation cancels the push action.',18,'#A3ADB8')
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True);im.save(out)
def main():
    preview(ROOT/'plugin/com.ezerche.everydaydials.sdPlugin',ROOT/'media/youtube-library/thumbnail-1920x960.png')
    print('Rendered V7 native keys and canvases in retained private order; static examples disclosed.')
if __name__=='__main__':main()
