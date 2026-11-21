from pathlib import Path
import json, io, shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageColor
import cairosvg
ROOT=Path(__file__).parent/'handoff'
ROOT.mkdir(exist_ok=True)
T={'surfaceTop':'#2D3035','surfaceBottom':'#08090B','activeTop':'#382327','activeBottom':'#100B0E','pressTop':'#4C252B','pressBottom':'#180B0F','activeForeground':'#FF777C','background':'#111315','foreground':'#F3F5F7','muted':'#B5BDC4','accent':'#FF454B','feedbackBackground':'#251619','divider':'#343A40','sheet':'#23272B'}
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def font(n):return ImageFont.truetype(FONT,n)
P={
'play-pause':'<path d="M3 5v14l9-7zM16 5v14M21 5v14"/>',
'fullscreen':'<path d="M3 9V3h6M21 9V3h-6M3 15v6h6M21 15v6h-6"/>',
'captions':'<rect x="2" y="4" width="20" height="16" rx="3"/><path d="M9 9H6v6h3M18 9h-3v6h3"/>',
'mute':'<path d="M2 9h4l5-4v14l-5-4H2zM16 9l6 6M22 9l-6 6"/>',
'prev-chapter':'<path d="M3 5v14M19 5v14l-11-7z"/>',
'next-chapter':'<path d="M21 5v14M5 5v14l11-7z"/>',
'prev-chapter-alt':'<path d="M2 6v12M12 6l-6 6 6 6M21 6l-6 6 6 6"/>',
'next-chapter-alt':'<path d="M22 6v12M3 6l6 6-6 6M12 6l6 6-6 6"/>',
'prev-video':'<rect x="2" y="4" width="20" height="16" rx="3"/><path d="M7 8v8M17 8v8l-7-4z"/>',
'next-video':'<rect x="2" y="4" width="20" height="16" rx="3"/><path d="M17 8v8M7 8v8l7-4z"/>',
'mini-player':'<rect x="2" y="4" width="20" height="16" rx="3"/><rect x="12" y="12" width="7" height="5" rx="1"/>',
 'theater':'<rect x="1" y="6" width="22" height="12" rx="2"/>',
'frame-back':'<rect x="2" y="4" width="20" height="16" rx="2"/><path d="M8 4v16M17 8l-4 4 4 4"/>',
'frame-forward':'<rect x="2" y="4" width="20" height="16" rx="2"/><path d="M16 4v16M7 8l4 4-4 4"/>',
'restart':'<path d="M5 8a8 8 0 1 1-1 8M5 3v6h6"/>',
'jump-end':'<path d="M2 12h16M12 6l6 6-6 6M22 4v16"/>',
'caption-size-up':'<rect x="2" y="4" width="20" height="16" rx="3"/><path d="M7 12h10M12 7v10"/>',
'caption-size-down':'<rect x="2" y="4" width="20" height="16" rx="3"/><path d="M7 12h10"/>',
'search':'<circle cx="10" cy="10" r="7"/><path d="M15 15l7 7"/>',
'shortcuts':'<rect x="1" y="5" width="22" height="14" rx="2"/><path d="M5 9h1M10 9h1M15 9h1M19 9h1M5 13h1M10 13h1M15 13h1M7 16h10"/>',
'dial-volume':'<path d="M2 9h4l5-4v14l-5-4H2zM15 8a6 6 0 0 1 0 8M19 5a10 10 0 0 1 0 14"/>',
'dial-seek':'<path d="M2 12h20M7 7l-5 5 5 5M17 7l5 5-5 5"/>',
'dial-speed':'<path d="M2 18a10 10 0 1 1 20 0M12 17l5-7"/>',
'dial-frame':'<rect x="2" y="4" width="20" height="16" rx="2"/><path d="M8 4v16M16 4v16"/>'}
for n in ['volume-up','volume-down']:
 P[n]='<path d="M1 9h4l5-4v14l-5-4H1zM15 12h8"/>'+('<path d="M19 8v8"/>' if n.endswith('up') else '')
for n in ['speed-up','speed-down']:
 P[n]='<path d="M2 17a9 9 0 1 1 18 0M11 16l5-7M17 21h6"/>'+('<path d="M20 18v5"/>' if n.endswith('up') else '')
LABELS={'play-pause':'Play / Pause','fullscreen':'Full Screen','captions':'Captions','mute':'Mute','prev-chapter':'Previous','next-chapter':'Next','prev-chapter-alt':'Prev Chapter','next-chapter-alt':'Next Chapter','prev-video':'Prev Video','next-video':'Next Video','mini-player':'Mini Player','theater':'Theater','frame-back':'Frame −1','frame-forward':'Frame +1','restart':'Restart','jump-end':'Jump to End','caption-size-up':'Caption +','caption-size-down':'Caption −','search':'Search','shortcuts':'Shortcuts','volume-up':'Volume +','volume-down':'Volume −','speed-up':'Speed +','speed-down':'Speed −'}
for sec in [10,5]:
 for direction,label in [('rewind','Back'),('forward','Forward')]:
  n=f'{direction}-{sec}';LABELS[n]=f'{label} {sec}s'
  P[n]=('<path d="M5 7a9 9 0 1 1-2 9M5 2v6h6"/>' if direction=='rewind' else '<path d="M19 7a9 9 0 1 0 2 9M19 2v6h-6"/>')+f'<text x="12" y="15" text-anchor="middle" fill="currentColor" stroke="none" font-family="DejaVu Sans" font-size="8" font-weight="bold">{sec}</text>'
def svg(n,color):return f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" color="{color}"><g fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{P[n]}</g></svg>'
def icon(n,s,color):return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg(n,color).encode(),output_width=s,output_height=s))).convert('RGBA')
def center(d,txt,x,y,size,color):d.text((x,y),txt,font=font(size),fill=color,anchor='mm')
def save(im,path):
 p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
def background(size,state='normal'):
 w,h=size
 top=T['pressTop'] if state=='pressed' else T['activeTop'] if state=='active' else T['surfaceTop']
 bottom=T['pressBottom'] if state=='pressed' else T['activeBottom'] if state=='active' else T['surfaceBottom']
 a=ImageColor.getrgb(top);b=ImageColor.getrgb(bottom)
 im=Image.new('RGB',size);d=ImageDraw.Draw(im)
 for y in range(h):
  t=(y/(h-1))**.72
  c=tuple(round(a[i]*(1-t)+b[i]*t) for i in range(3))
  d.line((0,y,w,y),fill=c)
 # Safe inset glow: follows the rounded frame, never a rectangular edge.
 if state=='pressed':
  scale=w/288;inset=round(14*scale);r=round(36*scale) if w==h else round(16*scale)
  layer=Image.new('RGBA',size);ld=ImageDraw.Draw(layer)
  ld.rounded_rectangle((inset,inset,w-1-inset,h-1-inset),radius=r,outline=(*ImageColor.getrgb(T['accent']),100),width=max(2,round(6*scale)))
  layer=layer.filter(ImageFilter.GaussianBlur(5*scale))
  im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')
 return im

def key(n,state,labeled):
 im=background((288,288),state);d=ImageDraw.Draw(im)
 if state=='pressed':d.rounded_rectangle((14,14,273,273),radius=36,outline=T['accent'],width=4)
 s=100 if labeled else 128
 if state=='pressed':s-=4
 ic=icon(n,s,T['foreground']);im.paste(ic,((288-s)//2,(96 if labeled else 144)-s//2),ic)
 if labeled:
  text=LABELS[n];size=22
  while d.textlength(text,font=font(size))>244:size-=1
  center(d,text,144,209,size,T['foreground'])
 return im
DIALS={'volume':('Volume','−     /     +','Mute'),'seek':('Seek','−10s  /  +10s','Play / Pause'),'speed':('Speed','−     /     +',None),'frame':('Frame','−1    /    +1','Play / Pause')}
def dial(n,state):
 im=background((400,200),'pressed' if state=='pressed' else 'active' if state!='normal' else 'normal');d=ImageDraw.Draw(im)
 title,value,push=DIALS[n];center(d,title,200,30,24,T['muted'])
 if state in ['left','right']:value='←' if state=='left' else '→'
 if state=='pressed':value=push or '—'
 center(d,value,200,99,36,T['accent'] if state!='normal' else T['foreground'])
 if push:center(d,'Press: '+push,200,168,21,T['muted'])
 return im
P['play']='<path d="M7 3v18l14-9z"/>'
P['pause']='<path d="M7 3v18M17 3v18"/>'
P['unmute']=P['dial-volume']
for n in P:
 savepath=ROOT/'vectors'/f'{n}.svg';savepath.parent.mkdir(exist_ok=True);savepath.write_text(svg(n,T['foreground']))
for n in LABELS:
 for state in ['normal','pressed']:
  suffix='' if state=='normal' else '-pressed'
  for variant in ['labeled','icon-only']:
   im=key(n,state,variant=='labeled');save(im,Path('keys')/variant/'288'/f'{n}{suffix}.png');save(im.resize((144,144),Image.Resampling.LANCZOS),Path('keys')/variant/'144'/f'{n}{suffix}.png')
for n in DIALS:
 for state in ['normal','left','right','pressed']:
  suffix='' if state=='normal' else '-'+state
  im=dial(n,state);save(im,Path('dials/400x200')/f'dial-{n}{suffix}.png');save(im.resize((200,100),Image.Resampling.LANCZOS),Path('dials/200x100')/f'dial-{n}{suffix}.png')
# Canvas-only SDK example: each encoder owns one 200x100 slot.
layout={'$schema':'https://schemas.elgato.com/streamdeck/plugins/layout.json','id':'MinimalVideoFeedback','items':[{'key':'canvas','type':'pixmap','rect':[0,0,200,100],'value':'../dials/200x100/dial-volume.png'}]}
(ROOT/'layout').mkdir(exist_ok=True);(ROOT/'layout/encoder-canvas.json').write_text(json.dumps(layout,indent=2));(ROOT/'design-tokens.json').write_text(json.dumps(T,indent=2))
# Device-region schematic, not a device photograph or working software.
im=Image.new('RGB',(1600,1060),T['sheet']);d=ImageDraw.Draw(im)
center(d,'Video controls',800,53,36,T['foreground']);center(d,'Stream Deck + • visual handoff',800,98,20,T['muted'])
order=['prev-chapter-alt','play-pause','next-chapter-alt','mute','captions','fullscreen','mini-player','theater']
for i,n in enumerate(order):
 x=280+(i%4)*280;y=145+(i//4)*240
 tile=key(n,'normal',True).resize((210,210),Image.Resampling.LANCZOS)
 mask=Image.new('L',(210,210));ImageDraw.Draw(mask).rounded_rectangle((0,0,209,209),radius=25,fill=255);im.paste(tile,(x,y),mask)
for i,n in enumerate(DIALS):im.paste(dial(n,'normal').resize((260,130),Image.Resampling.LANCZOS),(275+i*260,652))
for i,n in enumerate(DIALS):
 x=405+i*260;d.ellipse((x-66,817,x+66,949),fill=T['background']);ic=icon('dial-'+n,56,T['foreground']);im.paste(ic,(x-28,842),ic);center(d,DIALS[n][0],x,982,21,T['muted'])
center(d,'No live values shown without verified playback data.',800,1030,18,T['muted']);save(im,Path('reference/01-target-layout.png'))
# Every delivered raster shown in QA contact sheets, with variant & state named.
for variant in ['labeled','icon-only']:
 names=list(LABELS);sheet=Image.new('RGB',(1500,1900),T['sheet']);ds=ImageDraw.Draw(sheet)
 center(ds,f'{variant} • normal / pressed',750,35,28,T['foreground'])
 for i,n in enumerate(names):
  col=i%4;row=i//4;x=24+col*372;y=75+row*252
  for j,state in enumerate(['normal','pressed']):sheet.paste(key(n,state,variant=='labeled').resize((156,156),Image.Resampling.LANCZOS),(x+j*169,y))
  center(ds,n,x+162,y+180,17,T['muted'])
 save(sheet,Path('reference')/f'02-{variant}-all-states.png')
sheet=Image.new('RGB',(1680,1030),T['sheet']);ds=ImageDraw.Draw(sheet)
for r,n in enumerate(DIALS):
 for c,state in enumerate(['normal','left','right','pressed']):
  x=20+c*415;y=40+r*240;sheet.paste(dial(n,state),(x,y));center(ds,f'{n} / {state}',x+200,y+217,17,T['muted'])
save(sheet,Path('reference/03-dial-all-states.png'))
# Native 200x100 reference, exact pixels, no marketing enlargement.
sheet=Image.new('RGB',(800,100),T['background'])
for i,n in enumerate(DIALS):sheet.paste(dial(n,'normal').resize((200,100),Image.Resampling.LANCZOS),(200*i,0))
save(sheet,Path('reference/04-native-touch-strip.png'))
print('Rendered',len(LABELS),'actions; PNG files:',len(list(ROOT.rglob('*.png'))))

# Persistent state assets are separate from momentary normal/pressed assets.
# Label = next command; small status line = confirmed current player state.
STATES={
 'playback-playing':{'icon':'pause','label':'Pause','status':'Playing','active':True,'action':'K'},
 'playback-paused':{'icon':'play','label':'Play','status':'Paused','active':False,'action':'K'},
 'captions-on':{'icon':'captions','label':'Captions','status':'On','active':True,'action':'C'},
 'captions-off':{'icon':'captions','label':'Captions','status':'Off','active':False,'action':'C'},
 'mute-on':{'icon':'mute','label':'Unmute','status':'Muted','active':True,'action':'M'},
 'mute-off':{'icon':'unmute','label':'Mute','status':'Sound On','active':False,'action':'M'},
 'fullscreen-on':{'icon':'fullscreen','label':'Full Screen','status':'On','active':True,'action':'F'},
 'fullscreen-off':{'icon':'fullscreen','label':'Full Screen','status':'Off','active':False,'action':'F'},
 'theater-on':{'icon':'theater','label':'Theater','status':'On','active':True,'action':'T'},
 'theater-off':{'icon':'theater','label':'Theater','status':'Off','active':False,'action':'T'},
 'mini-player-on':{'icon':'mini-player','label':'Mini Player','status':'On','active':True,'action':'I'},
 'mini-player-off':{'icon':'mini-player','label':'Mini Player','status':'Off','active':False,'action':'I'}
}
def state_key(n,pressed,labeled):
 cfg=STATES[n];im=background((288,288),'pressed' if pressed else 'active' if cfg['active'] else 'normal');d=ImageDraw.Draw(im)
 color=T['foreground']
 s=100 if labeled else 128
 if pressed:s-=4
 ic=icon(cfg['icon'],s,color);im.paste(ic,((288-s)//2,(88 if labeled else 130)-s//2),ic)
 if pressed:d.rounded_rectangle((14,14,273,273),radius=36,outline=T['accent'],width=4)
 # Status indicator is persistent, unlike the press frame. Off is hollow.
 d.ellipse((247,27,260,40),fill=T['accent'] if cfg['active'] else None,outline=T['accent'] if cfg['active'] else T['muted'],width=2)
 if labeled:
  center(d,cfg['label'],144,186,22,T['foreground'])
  center(d,cfg['status'],144,231,20,T['activeForeground'] if cfg['active'] else T['muted'])
 return im
for n in STATES:
 for pressed in [False,True]:
  for variant in ['labeled','icon-only']:
   im=state_key(n,pressed,variant=='labeled');suffix='-pressed' if pressed else ''
   for size in [288,144]:save(im.resize((size,size),Image.Resampling.LANCZOS),Path('states')/variant/str(size)/f'{n}{suffix}.png')
(ROOT/'state-map.json').write_text(json.dumps(STATES,indent=2))
# Additional dial state feedback (no false percentages or speeds).
DIAL_STATES={'volume-muted':('Volume','Muted','Unmute',True), 'volume-unmuted':('Volume','Sound On','Mute',False), 'seek-playing':('Seek','Playing','Pause',True), 'seek-paused':('Seek','Paused','Play',False)}
def state_dial(n,pressed):
 title,status,push,active=DIAL_STATES[n]
 im=background((400,200),'pressed' if pressed else 'active' if active else 'normal');d=ImageDraw.Draw(im)
 center(d,title,200,30,24,T['muted']);center(d,status,200,97,34,T['activeForeground'] if active else T['foreground']);center(d,'Press: '+push,200,168,21,T['muted'])
 if pressed:d.rounded_rectangle((10,10,389,189),radius=20,outline=T['accent'],width=3)
 return im
for n in DIAL_STATES:
 for pressed in [False,True]:
  im=state_dial(n,pressed);suffix='-pressed' if pressed else ''
  for size,path in [((400,200),'400x200'),((200,100),'200x100')]:save(im.resize(size,Image.Resampling.LANCZOS),Path('dials/states')/path/f'dial-{n}{suffix}.png')
# Complete state sheet: action pair, then their held-press variants.
for variant in ['labeled','icon-only']:
 sheet=Image.new('RGB',(1300,1620),T['sheet']);ds=ImageDraw.Draw(sheet)
 center(ds,'Persistent state / held press • '+variant,650,37,27,T['foreground'])
 names=list(STATES)
 for row in range(6):
  for c,(idx,pressed) in enumerate([(row*2,False),(row*2+1,False),(row*2,True),(row*2+1,True)]):
   n=names[idx];x=45+c*312;y=95+row*250;tile=state_key(n,pressed,variant=='labeled').resize((200,200),Image.Resampling.LANCZOS)
   mask=Image.new('L',(200,200));ImageDraw.Draw(mask).rounded_rectangle((0,0,199,199),radius=24,fill=255);sheet.paste(tile,(x,y),mask)
   center(ds,n+(' / press' if pressed else ''),x+100,y+222,15,T['muted'])
 save(sheet,Path('reference')/f'05-{variant}-persistent-states.png')
sheet=Image.new('RGB',(850,1020),T['sheet']);ds=ImageDraw.Draw(sheet)
for r,n in enumerate(DIAL_STATES):
 for c,pressed in enumerate([False,True]):
  x=15+c*415;y=20+r*245;sheet.paste(state_dial(n,pressed),(x,y));center(ds,n+(' / press' if pressed else ''),x+200,y+220,17,T['muted'])
save(sheet,Path('reference/06-dial-persistent-states.png'))
print('V6 exports:',len(list(ROOT.rglob('*.png'))),'PNG;',len(list(ROOT.rglob('*.svg'))),'SVG')
