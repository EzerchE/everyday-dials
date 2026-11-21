"""Create original neutral artwork and seven Stream Deck+ profile candidates."""
from pathlib import Path
import json,uuid,subprocess,shutil,zipfile,os
from PIL import Image,ImageDraw,ImageFont
from profile_content import PROFILES,COLORS,KEY_ORIGINAL_INDEX,DIAL_ORIGINAL_INDEX,ENCODER_ART
ROOT=Path(__file__).resolve().parents[1]
PLUGIN=ROOT/'plugin/com.ezerche.everydaydials.sdPlugin'
NAMESPACE='com.ezerche.everydaydials'
NS=uuid.UUID('8e34566f-610c-42d5-9306-a19d3ee43374')
FONT=Path(os.environ.get('WINDIR',r'C:\Windows'))/'Fonts/segoeui.ttf'
BOLD=FONT.with_name('segoeuib.ttf')
MAGICK=shutil.which('magick') or r'C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe'
def font(s,b=False):return ImageFont.truetype(str(BOLD if b else FONT),s)
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def uid(t):return str(uuid.uuid5(NS,t))
def slug(s):return s.lower().replace(' ','-')
def app(s):return s.split()[0] if not s.startswith('Bambu') else 'Bambu Studio'
def glyph(name,size=156):
 p=ROOT/'build/glyphs'/(name+'.png')
 if not p.exists():
  source=ROOT/'assets/glyphs'/(name+'.svg');text=source.read_text().replace('currentColor','#F2F6FC');tmp=p.with_suffix('.svg');tmp.parent.mkdir(parents=True,exist_ok=True);tmp.write_text(text)
  subprocess.run([MAGICK,'-background','none','-density','576',str(tmp),'-resize','192x192',str(p)],check=True,capture_output=True)
 im=Image.open(p).convert('RGBA');im.thumbnail((size,size),Image.Resampling.LANCZOS);return im

def artwork(p,label,symbol,color,profile,dial=False,modifier=None,pressed=False):
 im=Image.new('RGBA',(432,432),(0,0,0,0) if dial else '#111925');d=ImageDraw.Draw(im)
 if dial:
  d.ellipse((10,10,422,422),fill='#142132',outline=color,width=10);d.arc((30,30,402,402),135,315,fill='#6B7A91',width=4)
  g=glyph(symbol,218);im.alpha_composite(g,(216-g.width//2,193-g.height//2))
  d.rounded_rectangle((64,304,368,367),radius=18,fill='#0C1522');d.text((216,332),app(profile).upper(),anchor='mm',font=font(30,True),fill=color)
  if modifier:d.text((338,88),modifier.upper() if len(modifier)==1 else {'clock':'TIME','size':'SIZE','voice':'VOICE','previous':'PREV'}.get(modifier,modifier),anchor='mm',font=font(21,True),fill=color)
 else:
  d.rounded_rectangle((6,6,426,426),radius=34,fill='#192536',outline=color if pressed else '#36485F',width=10 if pressed else 3)
  d.rounded_rectangle((26,24,406,81),radius=16,fill='#0D1725');d.text((48,52),app(profile).upper(),anchor='lm',font=font(26,True),fill=color);d.ellipse((368,42,387,61),fill=color)
  g=glyph(symbol);im.alpha_composite(g,(216-g.width//2,203-g.height//2))
  for i,line in enumerate(label.split('\n')):
   fs=35
   while d.textlength(line,font=font(fs,True))>360:fs-=1
   d.text((216,(327 if '\n' in label else 347)+i*43),line,anchor='mm',font=font(fs,True),fill='#F3F7FC')
 if pressed:d.rounded_rectangle((15,15,417,417),radius=29,outline='#FFFFFF',width=3)
 p.parent.mkdir(parents=True,exist_ok=True);im.resize((144,144),Image.Resampling.LANCZOS).save(p)

def generate():
 for sub in ['images/keys','layouts','licenses']: (PLUGIN/sub).mkdir(parents=True,exist_ok=True)
 catalog=json.loads((ROOT/'assets/catalog.json').read_text());keys=json.loads((ROOT/'assets/key-catalog.json').read_text())
 for name,p in PROFILES.items():
  for spec in [s for s in catalog if s['Id'].startswith(slug(name)+'-')]:
   semantic=int(spec['Id'].split('-')[-1]);idx=DIAL_ORIGINAL_INDEX[name].index(semantic);sym,mod=ENCODER_ART[name][idx]
   artwork(PLUGIN/spec['Icon'],'',sym,COLORS[name],name,True,mod)
  for spec in [s for s in keys if s['Id'].startswith(slug(name)+'-key-')]:
   token=spec['Id'].split('-')[-1];index=KEY_ORIGINAL_INDEX[name].index(int(token) if token.isdigit() else token);label,symbol,command=p['keys'][index]
   if symbol=='brand-youtube':symbol='play'
   variants={path:(label,symbol) for path in [spec['Image'],spec['PlayImage'],spec['PauseImage'],spec['UnknownImage'],spec['MutedImage'],spec['UnmutedImage']]}
   if spec['Kind']=='media':variants.update({spec['PlayImage']:('PLAY','play'),spec['PauseImage']:('PAUSE','pause'),spec['UnknownImage']:('PLAY /\nPAUSE','play-pause')})
   if spec['Kind']=='mute':variants.update({spec['MutedImage']:('MUTE','volume-x'),spec['UnmutedImage']:('UNMUTE','volume-2')})
   for path,(lbl,sym) in variants.items():
    artwork(PLUGIN/path,lbl,sym,COLORS[name],name);artwork(PLUGIN/Path(path).with_stem(Path(path).stem+'-pressed'),lbl,sym,COLORS[name],name,pressed=True)
 dump(PLUGIN/'catalog.json',catalog);dump(PLUGIN/'key-catalog.json',keys)
 layout={'$schema':'https://schemas.elgato.com/streamdeck/plugins/layout.json','id':NAMESPACE+'.layout','controller':'Encoder','items':[
  {'key':'title','type':'text','rect':[7,2,186,18],'font':{'size':13,'weight':700},'alignment':'left','color':'#FFFFFF'},
  {'key':'icon','type':'pixmap','rect':[8,24,43,43]},
  {'key':'value','type':'text','rect':[57,24,136,23],'font':{'size':16,'weight':700},'alignment':'left','color':'#FFFFFF'},
  {'key':'detail','type':'text','rect':[57,47,136,15],'font':{'size':9,'weight':500},'alignment':'left','color':'#AEB8C6'},
  {'key':'activity','type':'bar','rect':[57,65,135,4],'range':{'min':0,'max':100},'value':0,'bar_bg_c':'#303948','bar_fill_c':'#FFFFFF','border_w':0},
  {'key':'directions','type':'text','rect':[5,72,190,12],'font':{'size':10,'weight':500},'alignment':'center','color':'#C5CBD6'},
  {'key':'press','type':'text','rect':[5,86,190,12],'font':{'size':10,'weight':600},'alignment':'center','color':'#FFFFFF'}]}
 dump(PLUGIN/'layouts/control.json',layout)
 for label,size in [('plugin',256),('action',20),('category',28)]:
  for scale,suffix in [(1,''),(2,'@2x')]:
   im=Image.new('RGBA',(size*scale,size*scale),(0,0,0,0));d=ImageDraw.Draw(im);s=size*scale;d.ellipse((s*.12,s*.12,s*.88,s*.88),outline='#90D5F3',width=max(2,round(s*.075)));d.line((s*.5,s*.5,s*.72,s*.28),fill='#FFFFFF',width=max(2,round(s*.075)));im.save(PLUGIN/f'images/{label}{suffix}.png')
 manifest={'$schema':'https://schemas.elgato.com/streamdeck/plugins/manifest.json','UUID':NAMESPACE,'Name':'Everyday Dials','Author':'ezerche','Description':'Seven Windows Stream Deck+ shortcut layouts with guarded foreground app input and Windows master volume readback.','Version':'0.1.1.0','SDKVersion':2,'CodePath':'bin/EverydayDials.exe','Icon':'images/plugin','Category':'Everyday Dials','CategoryIcon':'images/category','Software':{'MinimumVersion':'6.5'},'OS':[{'Platform':'windows','MinimumVersion':'10'}],'Actions':[
 {'UUID':NAMESPACE+'.control','Name':'App control','Icon':'images/action','Controllers':['Encoder'],'Encoder':{'layout':'layouts/control.json','Icon':'images/action','TriggerDescription':{'Rotate':'Previous / next or decrease / increase','Push':'Perform displayed action','Touch':'Perform displayed action'}},'States':[{'Image':'images/plugin','ShowTitle':False}]},
 {'UUID':NAMESPACE+'.key','Name':'App key','Icon':'images/action','Controllers':['Keypad'],'DisableAutomaticStates':True,'States':[{'Image':'images/plugin','ShowTitle':False}]}]}
 dump(PLUGIN/'manifest.json',manifest)
 from youtube_art import apply
 apply(PLUGIN,ROOT/'assets/youtube-v8/originals')
 for f in (ROOT/'licenses').glob('*'):shutil.copy2(f,PLUGIN/'licenses'/f.name)
 for name,p in PROFILES.items():
  pid=uid('profile/'+name).upper();pageid=uid('page/'+name);default=uid('default/'+name);base=ROOT/'profiles'/(pid+'.sdProfile');page=base/'Profiles'/pageid.upper()
  # Anonymous zero UUID contains no physical device serial. Import needs recipient binding.
  dump(base/'manifest.json',{'Device':{'Model':'20GBD9901','UUID':'00000000-0000-0000-0000-000000000000'},'Name':'Everyday Dials - '+name,'Pages':{'Current':pageid,'Default':default,'Pages':[pageid]},'Version':'3.0'})
  dump(base/'Profiles'/default.upper()/'manifest.json',{'Controllers':[{'Actions':None,'Type':'Keypad'},{'Actions':None,'Type':'Encoder'}],'Icon':'','Name':''})
  ka={};da={}
  def action(kind,setting,image,identity):return {'ActionID':uid(identity),'LinkedTitle':True,'Name':'App key' if kind=='key' else 'App control','Plugin':{'Name':'Everyday Dials','UUID':NAMESPACE,'Version':'0.1.1.0'},'Resources':None,'Settings':setting,'State':0,'States':[{'Image':image,'Title':'','ShowTitle':False}],'UUID':NAMESPACE+'.'+kind}
  for i in range(8):
   keyid=slug(name)+'-key-'+str(KEY_ORIGINAL_INDEX[name][i]);spec=next(s for s in keys if s['Id']==keyid);image=f'Images/key-{i}.png';(page/'Images').mkdir(parents=True,exist_ok=True);shutil.copy2(PLUGIN/spec['Image'],page/image);ka[f'{i%4},{i//4}']=action('key',{'keyId':keyid},image,name+'/key/'+str(KEY_ORIGINAL_INDEX[name][i]))
   # Profile-level images override SDK setImage. Let the plugin manage every
   # key's normal/held/media state; retain copied Images/key-N.png for previews.
   ka[f'{i%4},{i//4}']['States']=[{'Title':'','ShowTitle':False}]
  for i in range(4):
   semantic=DIAL_ORIGINAL_INDEX[name][i];did=slug(name)+'-'+str(semantic);spec=next(s for s in catalog if s['Id']==did);image=f'Images/dial-{i}.png';shutil.copy2(PLUGIN/spec['Icon'],page/image);da[f'{i},0']=action('control',{'dialId':did},image,name+'/dial/'+str(semantic))
   if name=='YouTube Controls':da[f'{i},0']['States']=[{'Title':'','ShowTitle':False}]
  dump(page/'manifest.json',{'Controllers':[{'Actions':ka,'Type':'Keypad'},{'Actions':da,'Type':'Encoder'}],'Icon':'','Name':name})
  package={'AppVersion':'7.2.1.22472','DeviceModel':'20GBD9901','DeviceSettings':None,'FormatVersion':1,'OSType':'Windows','OSVersion':'10.0.19041','RequiredPlugins':[NAMESPACE]}
  dump(ROOT/'profiles/package.json',package)
  # Local Stream Deck-exported profile container; structural checks do not prove UI import.
  target=ROOT/'artifacts'/(slug(name)+'.streamDeckProfile');target.parent.mkdir(exist_ok=True)
  with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
   z.writestr('package.json',json.dumps(package,separators=(',',':')))
   for f in sorted(base.rglob('*')):
    if f.is_file():z.write(f,'Profiles/'+base.name+'/'+f.relative_to(base).as_posix())
 dump(ROOT/'verification/identity-map.json',[{'name':name,'profile':uid('profile/'+name),'page':uid('page/'+name),'default':uid('default/'+name)} for name in PROFILES])
 print(f'Generated {len(PROFILES)} profile candidates, {len(catalog)} dials and {len(keys)} keys with all original neutral artwork.')
if __name__=='__main__':generate()
