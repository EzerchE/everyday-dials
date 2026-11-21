"""Compose static exact-layout previews from sanitized shipped profile manifests."""
from pathlib import Path
import json, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0,str(Path(__file__).parent))
from profile_content import COLORS
ROOT=Path(__file__).resolve().parents[1]
PLUGIN=ROOT/'plugin/com.ezerche.everydaydials.sdPlugin'
FONT=Path(os.environ.get('WINDIR',r'C:\Windows'))/'Fonts/segoeui.ttf'
BOLD=FONT.with_name('segoeuib.ttf')
W,H=1920,960
INK='#F3F6FC';MUTED='#97A8C0';ACCENT='#95DDF5'
def font(n,b=False):return ImageFont.truetype(str(BOLD if b else FONT),n)
def text(d,xy,s,size=24,fill=INK,b=False,anchor=None):d.text(xy,s,font=font(size,b),fill=fill,anchor=anchor)
def fit(d,s,width,n=17,b=False):
 while n>8 and d.textlength(s,font=font(n,b))>width:n-=1
 return font(n,b)
def background():
 im=Image.new('RGB',(W,H));p=im.load()
 for y in range(H):
  for x in range(W):
   a=max(0,1-((x-260)**2+(y-240)**2)**.5/1800)
   p[x,y]=(int(8+4*a),int(14+11*a),int(26+18*a))
 d=ImageDraw.Draw(im)
 for x,y,r in [(1660,150,470),(1720,790,620)]:d.ellipse((x-r,y-r,x+r,y+r),outline='#1B2B40',width=2)
 return im
def data(name):
 identity=next(i for i in json.loads((ROOT/'verification/identity-map.json').read_text()) if i['name']==name)
 base=ROOT/'profiles'/(identity['profile'].upper()+'.sdProfile')/'Profiles'/identity['page'].upper()
 page=json.loads((base/'manifest.json').read_text())
 controllers={c['Type']:c['Actions'] for c in page['Controllers']}
 catalog={s['Id']:s for s in json.loads((PLUGIN/'catalog.json').read_text())}
 return base,controllers,catalog
def device(name):
 base,controllers,catalog=data(name);color=COLORS[name]
 im=Image.new('RGBA',(820,710),(0,0,0,0));d=ImageDraw.Draw(im)
 d.rounded_rectangle((0,0,819,709),radius=30,fill='#101C2D',outline='#2D4058',width=2)
 d.rounded_rectangle((24,25,31,66),radius=3,fill=color)
 text(d,(48,30),name.upper(),29,b=True);text(d,(49,72),'8 KEYS  /  4 DIALS',14,MUTED)
 keysize=144;gap=22;left=(820-4*keysize-3*gap)//2
 for i in range(8):
  a=controllers['Keypad'][f'{i%4},{i//4}'];image=Image.open(base/(a['States'][0].get('Image') or f'Images/key-{i}.png')).convert('RGBA')
  im.alpha_composite(image.resize((keysize,keysize),Image.Resampling.LANCZOS),(left+(i%4)*(keysize+gap),108+(i//4)*162))
 stripy=441;stripw=164
 for i in range(4):
  a=controllers['Encoder'][f'{i},0'];s=catalog[a['Settings']['dialId']];x=left+i*166
  if name=='YouTube Controls':
   from render_youtube import tile
   canvas=tile(PLUGIN,s,volume=42).resize((162,81),Image.Resampling.LANCZOS)
   im.alpha_composite(canvas.convert('RGBA'),(x,stripy+17))
   cx=x+80;cy=622
   d.ellipse((cx-47,cy-47,cx+47,cy+47),fill='#070D17',outline='#465872',width=3)
   d.ellipse((cx-37,cy-37,cx+37,cy+37),fill='#192638',outline='#263A53',width=2)
   d.line((cx,cy-34,cx,cy-20),fill=color,width=4);text(d,(cx,682),str(i+1),12,MUTED,anchor='mm')
   continue
  d.rounded_rectangle((x,stripy,x+stripw-2,stripy+116),radius=9,fill='#081221',outline='#2A3E58',width=1)
  d.text((x+9,stripy+8),s['Title'],font=fit(d,s['Title'],145,15,True),fill=color)
  value='42%' if s['Volume'] else 'Turn or tap'
  text(d,(x+9,stripy+32),value,20,b=True)
  direction=s['LeftLabel']+' / '+s['RightLabel']
  d.text((x+9,stripy+65),direction,font=fit(d,direction,145,12),fill=MUTED)
  press='Push: '+s['PressLabel']
  d.text((x+9,stripy+87),press,font=fit(d,press,145,12,True),fill=INK)
  d.line((x+9,stripy+109,x+154,stripy+109),fill='#354760',width=2)
  if s['Volume']:d.line((x+9,stripy+109,x+70,stripy+109),fill=color,width=3)
  # A neutral physical dial below the exact feedback title, not an app logo.
  cx=x+80;cy=622
  d.ellipse((cx-47,cy-47,cx+47,cy+47),fill='#070D17',outline='#465872',width=3)
  d.ellipse((cx-37,cy-37,cx+37,cy+37),fill='#192638',outline='#263A53',width=2)
  d.line((cx,cy-34,cx,cy-20),fill=color,width=4)
  text(d,(cx,682),str(i+1),12,MUTED,anchor='mm')
 return im
def paste(im,item,x,y,w):
 item=item.resize((w,round(item.height*w/item.width)),Image.Resampling.LANCZOS)
 im.paste(item,(x,y),item)
def header(im,kicker,title,subtitle):
 d=ImageDraw.Draw(im);text(d,(62,30),kicker,16,ACCENT,b=True);text(d,(58,57),title,52,b=True);text(d,(62,126),subtitle,22,MUTED)
def footer(im):
 d=ImageDraw.Draw(im);d.line((62,906,1858,906),fill='#2C3C52',width=1)
 text(d,(62,923),'EVERYDAY DIALS  /  v0.1.1-beta.1  /  V7.1 YOUTUBE ART',15,b=True)
 text(d,(1858,923),'Static layout previews • generic volume example 42% • YouTube neutral • not live screenshots',15,MUTED,anchor='ra')
def gallery(filename,title,subtitle,names):
 im=background();header(im,'WINDOWS  /  STREAM DECK+',title,subtitle)
 if len(names)==2:
  for x,name in zip([80,1040],names):paste(im,device(name),x,177,800)
 else:
  for x,name in zip([60,685,1310],names):paste(im,device(name),x,222,550)
  d=ImageDraw.Draw(im);text(d,(960,806),'MASTER VOLUME FIRST   •   SHORTCUTS GUARDED BY THE FOREGROUND APP',23,ACCENT,b=True,anchor='mm')
 footer(im);im.save(ROOT/'media'/filename)
def main():
 (ROOT/'media').mkdir(exist_ok=True)
 im=background();header(im,'FREE COMMUNITY PROFILE  /  WINDOWS STREAM DECK+','YouTube Video Controls V7.1','Native keys. Four tactile dials. Six bonus profiles for everyday apps.')
 paste(im,device('YouTube Controls'),65,174,820)
 d=ImageDraw.Draw(im)
 text(d,(1000,205),'LESS HUNTING.',43,b=True);text(d,(1000,260),'MORE DOING.',43,ACCENT,b=True)
 for y,num,title,detail in [(355,'01','Volume on the left','Actual Windows output readback'),(459,'02','Keys and dials together','Eight useful keys. Four tactile controls.'),(563,'03','Your apps, in focus','App-guarded shortcuts and honest state')]:
  text(d,(1000,y),num,22,ACCENT,b=True);text(d,(1060,y-4),title,28,b=True);text(d,(1060,y+36),detail,20,MUTED)
 text(d,(1000,675),'SIX OPTIONAL BONUS PROFILES',16,ACCENT,b=True)
 names=['Chrome','Stremio','Spotify','Telegram','WhatsApp','Bambu Studio']
 x,y=1000,706
 for name in names:
  width=round(d.textlength(name,font=font(18,True)))+36
  if x+width>1835:x=1000;y+=53
  d.rounded_rectangle((x,y,x+width,y+39),radius=18,fill='#162840',outline='#344D6B',width=1);text(d,(x+18,y+7),name,18,b=True);x+=width+10
 footer(im);im.save(ROOT/'media/thumbnail.png')
 gallery('gallery-01-browser-video.png','Browser flow. Video control.','The shipped Chrome and YouTube layouts, including adjacent chapter keys and dedicated 1x reset.',['Chrome Daily','YouTube Controls'])
 gallery('gallery-02-music-movies.png','Music and movies, within reach.','Playback stays neutral when state is unknown. Spotify can use a matching Windows media session.',['Spotify Media','Stremio Cinema'])
 gallery('gallery-03-messages-print.png','Messages to model prep.','Separate profiles for each app. No accounts, chat content, printer settings or app logos included.',['Telegram Daily','WhatsApp Daily','Bambu Studio Prep'])
 print('Created thumbnail and 3 galleries at 1920x960 from sanitized profile manifests.')
if __name__=='__main__':main()

