"""Select V7.1 native assets from supplied V8 data; no supplied code executes."""
from pathlib import Path
import json,shutil,subprocess,tempfile,hashlib
from PIL import Image
KEYS={1:'prev-chapter-alt',0:'play-pause',2:'next-chapter-alt',4:'mute',5:'captions',3:'fullscreen',6:'mini-player',7:'theater'}
DIALS={2:'volume',0:'seek',1:'speed',3:'frame'}
FIELDS=['Image','PlayImage','PauseImage','UnknownImage','MutedImage','UnmutedImage']

def validate_layout(layout):
    items=layout['items'];assert len({i['key'] for i in items})==len(items),'Duplicate layout key'
    for a in items:
        x,y,w,h=a['rect'];assert x>=0 and y>=0 and w>0 and h>0 and x+w<=200 and y+h<=100,('Layout bounds',a['key'])
    for index,a in enumerate(items):
        ax,ay,aw,ah=a['rect']
        for b in items[index+1:]:
            if a.get('zOrder',0)!=b.get('zOrder',0):continue
            bx,by,bw,bh=b['rect']
            assert not (ax<bx+bw and bx<ax+aw and ay<by+bh and by<ay+ah),('Same-zOrder overlap',a['key'],b['key'])

def encoder_icon(originals,stem):
    # Same supplied 24-unit stroke/shape, 54px optical box on a transparent 144px
    # editor image. The Stream Deck application's own gray frame is host-owned.
    svg=(originals/'vectors'/('dial-'+stem+'.svg')).read_text().replace('currentColor','#F3F5F7')
    magick=shutil.which('magick') or r'C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe'
    with tempfile.TemporaryDirectory() as tmp:
        source=Path(tmp)/'glyph.svg';dest=Path(tmp)/'glyph.png';source.write_text(svg)
        subprocess.run([magick,'-background','none','-density','576',str(source),'-resize','54x54',str(dest)],check=True,capture_output=True)
        glyph=Image.open(dest).convert('RGBA');im=Image.new('RGBA',(144,144),(0,0,0,0));im.alpha_composite(glyph,((144-glyph.width)//2,(144-glyph.height)//2));return im

def apply(plugin,originals):
    plugin=Path(plugin);originals=Path(originals);copied=[]
    specs=json.loads((plugin/'key-catalog.json').read_text())
    for spec in specs:
        if not spec['Id'].startswith('youtube-controls-key-'):continue
        stem=KEYS[int(spec['Id'].rsplit('-',1)[1])]
        for relative in set(spec[f] for f in FIELDS):
            target=plugin/relative;target.parent.mkdir(parents=True,exist_ok=True)
            for suffix in ['', '-pressed']:
                dest=target if not suffix else target.with_stem(target.stem+suffix)
                source=originals/'keys/labeled/144'/(stem+suffix+'.png')
                assert Image.open(source).size==(144,144)
                shutil.copyfile(source,dest);copied.append(dest.relative_to(plugin).as_posix())
    folder=plugin/'images/youtube-dials';folder.mkdir(parents=True,exist_ok=True)
    encoders=plugin/'images/youtube-encoders';encoders.mkdir(parents=True,exist_ok=True)
    # Remove only known superseded derived directional editor images.
    for stem in DIALS.values():
        for state in ['-left','-right']:
            old=encoders/('dial-'+stem+state+'.png')
            if old.exists():old.unlink()
        for state in ['','-left','-right','-pressed']:
            source=originals/'dials/200x100'/('dial-'+stem+state+'.png');target=folder/source.name
            assert Image.open(source).size==(200,100)
            # Supplied 1x is the existing bounded reset action, never readback.
            # All current native images are copied byte for byte, with no paint.
            shutil.copyfile(source,target)
            copied.append(target.relative_to(plugin).as_posix())
        target=encoders/('dial-'+stem+'.png');encoder_icon(originals,stem).save(target);copied.append(target.relative_to(plugin).as_posix())
        # Catalog/profile editor uses this same clean semantic symbol.
        spec=next(s for s in json.loads((plugin/'catalog.json').read_text()) if s['Id']=='youtube-controls-'+str(next(k for k,v in DIALS.items() if v==stem)))
        shutil.copyfile(target,plugin/spec['Icon']);copied.append(spec['Icon'])
    for state in ['', '-pressed']:
        source=originals/'dials/states/200x100'/('dial-volume-muted'+state+'.png');shutil.copyfile(source,folder/source.name);copied.append((folder/source.name).relative_to(plugin).as_posix())
    hashes={path:hashlib.sha256((plugin/path).read_bytes()).hexdigest() for path in copied if path.startswith('images/keys/')}
    (plugin/'youtube-v71-key-sha256.json').write_text(json.dumps(hashes,indent=2)+'\n')
    namespace=json.loads((plugin/'manifest.json').read_text())['UUID']
    layout={'$schema':'https://schemas.elgato.com/streamdeck/plugins/layout.json','id':namespace+'.youtube','controller':'Encoder','items':[{'key':'canvas','type':'pixmap','rect':[0,0,200,100]}]}
    validate_layout(layout);(plugin/'layouts/youtube.json').write_text(json.dumps(layout,indent=2)+'\n');copied.append('layouts/youtube.json')
    return sorted(set(copied))
