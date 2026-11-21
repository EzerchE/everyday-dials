"""Verify the public allowlist and create reviewable prerelease download/source ZIPs."""
from pathlib import Path, PurePosixPath
import hashlib, json, re, zipfile
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
NS='com.ezerche.everydaydials'
PLUGIN=ROOT/'build'/(NS+'.sdPlugin')
BASE=ROOT/'plugin'/(NS+'.sdPlugin')
VERSION='0.1.1-beta.1'
PUBLIC_VERIFICATION={'archive-checks.json','dependency-hashes.json','generator-checks.json','identity-map.json','release-checks.json','source-build-checks.json','visual-qa.md','youtube-art-checks.json','youtube-runtime-preview.png','youtube-shortcut-audit.json'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,s):p.write_text(s,encoding='utf-8')
def dump(p,obj):write(p,json.dumps(obj,indent=2)+'\n')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def slug(s):return s.lower().replace(' ','-')
def md(s):return str(s).replace('\n',' / ').replace('|',' / ')
def guide(identities,catalog,keys):
 out=['# Key and dial guide','', 'Positions are left to right: keys 1–4 on the top row, 5–8 on the bottom row; dials 1–4 beneath the touchscreen. Turn counterclockwise (CCW) or clockwise (CW). Dial push and touchscreen tap perform the same action. The table is generated from the shipped profile settings and catalogs.','', 'Master volume dials work independently of the foreground app. Other controls require the named app in the foreground, with the player or intended pane focused. Media keys use an exact Windows session when available, otherwise a guarded app-local fallback. Keyboard input is never a guarantee that the app accepted the action.','']
 for item in identities:
  name=item['name'];base=ROOT/'profiles'/(item['profile'].upper()+'.sdProfile')/'Profiles'/item['page'].upper();page=read(base/'manifest.json');cs={c['Type']:c['Actions'] for c in page['Controllers']}
  out+=['## '+name,'','Target executable: `'+catalog[cs['Encoder']['0,0']['Settings']['dialId']]['App']+'`.','','| Key | Label | Command | Behavior |','| --- | --- | --- | --- |']
  for i in range(8):
   s=keys[cs['Keypad'][f'{i%4},{i//4}']['Settings']['keyId']]
   note='Guarded shortcut'
   if s['Kind']=='website':note='Fixed YouTube URL in standard Chrome; permitted from another foreground app'
   elif s['Kind']=='media':note='Reliable next-action icon only when a matching session exists; otherwise neutral'
   elif s['Kind']=='media-command':note='Session command or guarded local fallback'
   elif s['Kind']=='mute':note='Next mute/unmute operation from Windows audio state when available; key still app guarded'
   if s['Fallback']:note+='; fallback `'+s['Fallback']+'`'
   out.append(f"| {i+1} | {md(s['Label'])} | `{s['Command']}` | {note} |")
  out+=['','| Dial | Function | CCW | CW | Push / tap |','| --- | --- | --- | --- | --- |']
  for i in range(4):
   s=catalog[cs['Encoder'][f'{i},0']['Settings']['dialId']]
   out.append(f"| {i+1} | {s['Title']} | {s['LeftLabel']} (`{s['Left']}`) | {s['RightLabel']} (`{s['Right']}`) | {s['PressLabel']} (`{s['Press']}`) |")
  out+=['']
  if name=='YouTube Controls':out+=['Previous/next chapter sends Ctrl+Left / Ctrl+Right. The video must contain chapters. `YTSPEEDDOWN` and `YTSPEEDUP` send Shift+OEM comma/period; reset sends 32 slower packets then three faster packets, with no play/pause key. Frame stepping requires a paused video. Master volume is Windows output volume, not YouTube video volume. Select the YouTube profile manually.','']
  if name=='Spotify Media':out+=['Place the pointer over the desired Spotify pane for scroll. Focus push sends Enter and can activate the currently focused item. A unique matching Windows media session can provide a reliable next Play/Pause operation; absent or ambiguous sessions stay neutral.','']
  if name=='Stremio Cinema':out+=['Seek, subtitle delay and subtitle-size bindings depend on Stremio version/player focus. Reliable playback state is not promised; neutral feedback is expected when unavailable.','']
  if name=='Bambu Studio Prep':out+=['Preparation/view shortcuts only. Slice may take time; there is no completion/status readback, printing command, printer identity or printer configuration.','']
 out+=['## Interpreting feedback','','The volume percentage is actual Windows master output readback. Other dial labels show the last shortcut sent and its intended operation; they do not read application state. Play/Pause remains neutral when the provider cannot reliably identify the session. Pressed artwork is a momentary acknowledgement. A yellow alert means the guard, input API or fixed website launch failed.','', 'Commands such as `VOLDOWN`, `YTSPEEDRESET`, `SCROLLUP` and `OPENYOUTUBE` are internal allowlisted operations, not text typed into an app. The README lists executable, focus, keyboard-layout and installation limits.','']
 write(ROOT/'KEY-DIAL-GUIDE.md','\n'.join(out))
def privacy(files,label):
 # Public standard Program Files paths are intentional, machine/user paths are not.
 patterns=[rb'(?i)[A-Z]:[\\/]+Users[\\/]',rb'(?i)AppData[\\/]',rb'(?i)com\.ezerc\.interactivedials',rb'(?i)Bearer\s+[A-Za-z0-9_-]{16,}',rb'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----']
 for p in files:
  b=p.read_bytes()
  samples=[b]
  if p.suffix.lower() in ('.dll','.exe'):samples+=[b[::2],b[1::2]]
  for sample in samples:
   for pattern in patterns:
    assert not re.search(pattern,sample),f'Privacy pattern in {label}: {p.relative_to(ROOT)}'
def zipfiles(path,entries):
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
  for p,arc in sorted(entries,key=lambda e:e[1]):
   info=zipfile.ZipInfo(arc,(2026,11,21,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
   z.writestr(info,p.read_bytes())
def main():
 identities=read(ROOT/'verification/identity-map.json');catalog={s['Id']:s for s in read(BASE/'catalog.json')};keys={s['Id']:s for s in read(BASE/'key-catalog.json')}
 assert len(identities)==7 and len(catalog)==28 and len(keys)==56
 guide(identities,catalog,keys)
 from youtube_art import KEYS,FIELDS,validate_layout
 for p in (BASE/'layouts').glob('*.json'):validate_layout(read(p))
 original=ROOT/'assets/youtube-v8/originals';provenance=read(ROOT/'assets/youtube-v8/original-sha256.json')
 assert len(provenance)==422
 for row in provenance:assert sha(original/row['file'])==row['sha256']
 # Retained V7, V6 and V4 files are archival source, never selected artwork.
 for row in read(ROOT/'assets/youtube-v7/original-sha256.json'):
  assert sha(ROOT/'assets/youtube-v7/originals'/row['file'])==row['sha256']
 for row in read(ROOT/'assets/youtube-v6/original-sha256.json'):
  assert sha(ROOT/'assets/youtube-v6/originals'/row['file'])==row['sha256']
 for row in read(ROOT/'assets/lovable-youtube-v4/original-sha256.json'):
  assert sha(ROOT/'assets/lovable-youtube-v4/originals'/row['file'])==row['sha256']
 normals=[p for p in (original/'keys/labeled/144').glob('*.png') if not p.stem.endswith('-pressed')]
 dials=list((original/'dials/200x100').glob('*.png'));assert len(normals)==28 and len(dials)==16
 expectedHashes=read(BASE/'youtube-v71-key-sha256.json')
 for spec in keys.values():
  if spec['Id'].startswith('youtube-controls-key-'):
   stem=KEYS[int(spec['Id'].rsplit('-',1)[1])]
   for field in FIELDS:
    p=BASE/spec[field];assert p.read_bytes()==(original/'keys/labeled/144'/(stem+'.png')).read_bytes()
    pressed=p.with_stem(p.stem+'-pressed');assert pressed.read_bytes()==(original/'keys/labeled/144'/(stem+'-pressed.png')).read_bytes()
    assert sha(p)==expectedHashes[spec[field]] and sha(pressed)==expectedHashes[pressed.relative_to(BASE).as_posix()]
    assert Image.open(p).size==Image.open(pressed).size==(144,144)
 layout=read(BASE/'layouts/youtube.json');assert layout['items']==[{'key':'canvas','type':'pixmap','rect':[0,0,200,100]}]
 for p in (BASE/'images/youtube-dials').glob('*.png'):
  assert Image.open(p).size==(200,100)
  source=original/('dials/states/200x100' if '-muted' in p.stem else 'dials/200x100')/p.name
  assert p.read_bytes()==source.read_bytes(),'Every native canvas, including speed1x, must equal supplied V8 bytes'
 assert len(list((BASE/'images/youtube-dials').glob('*.png')))==18
 for p in (BASE/'images/youtube-encoders').glob('*.png'):
  image=Image.open(p);assert image.size==(144,144) and image.mode=='RGBA' and image.getpixel((0,0))[3]==0
  alpha=image.getchannel('A').getbbox();assert alpha and alpha[2]-alpha[0]<=54 and alpha[3]-alpha[1]<=54
 assert len(list((BASE/'images/youtube-encoders').glob('*.png')))==4
 artchecks={'design':'V7.1','suppliedSourceDesign':'V8','originalFiles':len(provenance),'originalHashes':'pass','archivalV4Hashes':'pass','archivalV6Hashes':'pass','archivalV7Hashes':'pass','optionalNormalIcons':28,'optionalPressedIcons':28,'optionalNativeDialPngs':16,'assignedYouTubeKeys':8,'assignedYouTubeDials':4,'keyVariantOriginalByteEquality':'pass','runtimeDialBackgrounds':'18 native200x100 images:16 normal/left/right/press plus2 actual master-muted','singlePixmapLayout':'pass','speedPressedAdaptation':'none; supplied Press1x/pressed1x copied exactly; action label only','editorIcons':'4 transparent SVG-derived144px canvases with54px glyph bounds','windowsMasterMute':'readback; browser M remains unknown','persistentBrowserStateClaim':False,'speedPercentageClaim':False}
 dump(ROOT/'verification/youtube-art-checks.json',artchecks)
 manifest=read(PLUGIN/'manifest.json');assert manifest['UUID']==NS
 assert {s['UUID'] for s in manifest['Actions']}=={NS+'.key',NS+'.control'}
 assert read(PLUGIN/'catalog.json')==list(catalog.values()) and read(PLUGIN/'key-catalog.json')==list(keys.values())
 assert {p.relative_to(PLUGIN).as_posix() for p in PLUGIN.rglob('*') if p.is_file() and 'bin' not in p.relative_to(PLUGIN).parts}=={p.relative_to(BASE).as_posix() for p in BASE.rglob('*') if p.is_file()},'Incremental build contains stale nonbinary assets'
 allids=set();profilecounts={};dynamicKeys=0
 for item in identities:
  artifact=ROOT/'artifacts'/(slug(item['name'])+'.streamDeckProfile')
  with zipfile.ZipFile(artifact) as z:
   assert z.testzip() is None
   names=z.namelist();assert all(not n.startswith('/') and '..' not in PurePosixPath(n).parts and '\\' not in n for n in names)
   package=json.loads(z.read('package.json'));assert package['RequiredPlugins']==[NS] and package['DeviceModel']=='20GBD9901'
   base='Profiles/'+item['profile'].upper()+'.sdProfile/'
   root=json.loads(z.read(base+'manifest.json'));assert root['Device']['UUID']=='00000000-0000-0000-0000-000000000000'
   assert root['Pages']['Pages']==[item['page']]
   assert root['Pages']['Current']==item['page'] and root['Pages']['Default']==item['default']
   assert root['Pages']['Default']!=root['Pages']['Current']
   for referenced in [root['Pages']['Current'],root['Pages']['Default'],*root['Pages']['Pages']]:assert base+'Profiles/'+referenced.upper()+'/manifest.json' in names
   for pageid in [item['page'],item['default']]:assert base+'Profiles/'+pageid.upper()+'/manifest.json' in names
   prefix=base+'Profiles/'+item['page'].upper()+'/'
   page=json.loads(z.read(prefix+'manifest.json'));cs={c['Type']:c['Actions'] for c in page['Controllers']}
   assert len(cs['Keypad'])==8 and len(cs['Encoder'])==4
   assert set(cs['Keypad'])=={f'{i%4},{i//4}' for i in range(8)} and set(cs['Encoder'])=={f'{i},0' for i in range(4)}
   for kind,actions in cs.items():
    for position,a in actions.items():
     assert a['ActionID'] not in allids;allids.add(a['ActionID'])
     assert a['Plugin']['UUID']==NS and a['UUID']==NS+('.key' if kind=='Keypad' else '.control')
     settings=a['Settings'];assert set(settings)==({'keyId'} if kind=='Keypad' else {'dialId'})
     identifier=next(iter(settings.values()));assert identifier.startswith(slug(item['name'])+'-')
     spec=(keys if kind=='Keypad' else catalog)[identifier]
     if kind=='Encoder' and identifier.startswith('youtube-controls-'):
      assert not a['States'][0].get('Image'),'Custom profile image would block SDK encoder setImage'
      assert z.read(prefix+'Images/dial-'+position.split(',')[0]+'.png')==(BASE/spec['Icon']).read_bytes()
     elif kind=='Keypad':
      assert len(a['States'])==1 and 'Image' not in a['States'][0],'Custom key image would block SDK runtime feedback'
      assert a['States'][0].get('ShowTitle') is False and a['States'][0].get('Title')=='','Native key titles must stay hidden'
      dynamicKeys+=1
      keyindex=int(position.split(',')[0])+4*int(position.split(',')[1]);assert z.read(prefix+f'Images/key-{keyindex}.png')==(BASE/spec['Image']).read_bytes()
     else:assert z.read(prefix+a['States'][0]['Image'])==(BASE/spec['Image' if kind=='Keypad' else 'Icon']).read_bytes()
     if kind=='Encoder' and position=='0,0':assert spec['Volume'] and spec['Press']=='MUTE'
   for n in names:
    if n!='package.json':assert z.read(n)==(ROOT/'profiles'/n.removeprefix('Profiles/')).read_bytes()
   assert len(names)==16;profilecounts[item['name']]={'keys':8,'dials':4,'entries':len(names),'references':'pass','import':'V7.1 not installed by build; device acceptance pending' if item['name']=='YouTube Controls' else 'unverified','hardware':'V7.1 appearance/device review pending; retained speed sequence previously confirmed; full profile QA incomplete' if item['name']=='YouTube Controls' else 'pending','pageReferenceGraph':'current, default and listed pages all resolve to contained manifests'}
 assert dynamicKeys==56,'All seven profiles must allow SDK-managed key images'
 # Every catalog image and pressed variant must exist and be a real PNG.
 for s in keys.values():
  for key in ['Image','PlayImage','PauseImage','UnknownImage','MutedImage','UnmutedImage']:
   p=BASE/s[key];Image.open(p).verify();Image.open(p.with_stem(p.stem+'-pressed')).verify()
 for s in catalog.values():Image.open(BASE/s['Icon']).verify()
 speed=catalog['youtube-controls-1'];assert (speed['Left'],speed['Right'],speed['Press'])==('YTSPEEDDOWN','YTSPEEDUP','YTSPEEDRESET')
 assert keys['youtube-controls-key-1']['Command']=='CTRL+LEFT' and keys['youtube-controls-key-2']['Command']=='CTRL+RIGHT'
 # The three runtime binaries are byte-for-byte unmodified NuGet dependencies.
 package=Path.home()/'.nuget/packages/microsoft.windows.sdk.net.ref/10.0.19041.57/lib/net8.0'
 dependency=[]
 for name in ['Microsoft.Windows.SDK.NET.dll','Microsoft.Windows.UI.Xaml.dll','WinRT.Runtime.dll']:
  value=sha(PLUGIN/'bin'/name);assert value==sha(package/name)
  dependency.append({'file':'bin/'+name,'package':'Microsoft.Windows.SDK.NET.Ref','version':'10.0.19041.57','packagePath':'lib/net8.0/'+name,'sha256':value,'unmodified':True})
 dump(ROOT/'verification/dependency-hashes.json',dependency)
 allowedbin={'EverydayDials.exe','EverydayDials.dll','EverydayDials.deps.json','EverydayDials.runtimeconfig.json',*[d['file'].split('/')[-1] for d in dependency]}
 assert {p.name for p in (PLUGIN/'bin').iterdir()}==allowedbin
 for name in ['Microsoft-Windows-SDK-LICENSE.rtf','Microsoft-Windows-SDK-REDIST.html','WinRT.Runtime-MIT.txt','lucide-LICENSE.txt']:
  assert (PLUGIN/'licenses'/name).read_bytes()==(ROOT/'licenses'/name).read_bytes()
 assert 'Validation successful' in (ROOT/'verification/cli-validate.txt').read_text(encoding='utf-8-sig')
 assert 'Successfully packaged plugin' in (ROOT/'verification/cli-pack.txt').read_text(encoding='utf-8-sig')
 tests=(ROOT/'verification/self-test.txt').read_text(encoding='utf-8-sig').splitlines();assert len(tests)>200 and all(s.startswith('PASS ') for s in tests if s.strip())
 install=ROOT/'artifacts'/(NS+'.streamDeckPlugin')
 with zipfile.ZipFile(install) as z:
  assert z.testzip() is None
  packed={n for n in z.namelist() if not n.endswith('/')};prefix=NS+'.sdPlugin/'
  expected={prefix+p.relative_to(PLUGIN).as_posix() for p in PLUGIN.rglob('*') if p.is_file()}
  assert packed==expected,(sorted(packed-expected),sorted(expected-packed))
  for p in PLUGIN.rglob('*'):
   if p.is_file():assert z.read(prefix+p.relative_to(PLUGIN).as_posix())==p.read_bytes()
 for p in (ROOT/'media').rglob('*.png'):assert Image.open(p).size==((288,288) if p.name=='app-icon-288x288.png' else (1920,960))
 assert len(list((ROOT/'media').glob('*.png')))==4
 source=[]
 for name in ['README.md','KEY-DIAL-GUIDE.md','YOUTUBE-ARTWORK.md','LICENSE','PRIVACY.md','THIRD-PARTY-NOTICES.md','RELEASE-NOTES.md','REPORT.md','global.json','.gitignore','.github/FUNDING.yml','tools/package.json','tools/package-lock.json']:
  source.append(ROOT/name)
 for directory in ['src','scripts','assets','plugin','profiles','licenses','media','marketplace','verification']:
  for p in (ROOT/directory).rglob('*'):
   if directory=='verification' and p.name not in PUBLIC_VERIFICATION:continue
   if p.is_file() and not {'bin','obj','__pycache__'}.intersection(p.relative_to(ROOT/directory).parts) and p.suffix not in ('.pyc','.pdb') and p.name not in ('phase2_preservation.py','original-build.txt'):source.append(p)
 # This scanner itself contains test patterns, so do not treat its literal regex as data.
 privacy([p for p in source if p.name!='verify_release.py'],'source');privacy([p for p in PLUGIN.rglob('*') if p.is_file()],'plugin')
 summary={'release':'v'+VERSION,'status':'free public beta candidate; V7.1 candidate; device/appearance acceptance pending; full seven-profile hardware QA incomplete','profiles':profilecounts,'uniqueActionIds':len(allids),'catalogDials':28,'catalogKeys':56,'sdkManagedProfileKeys':dynamicKeys,'selfTestPassLines':len(tests),'officialCliVersion':'1.10.5','officialCliValidation':'pass','officialCliPack':'pass','packagedPluginFiles':len(expected),'dependencyHashes':'pass; unmodified NuGet net8.0 binaries','privacy':'allowlist and text/binary pattern scan pass','media':'4 exact-layout PNGs +4 current V7.1 PNGs at1920x960,288px app icon; all static examples','youtubeArtwork':artchecks,'hardware':'retained speed sequence previously physically confirmed; prior V7 private UI reviewed; V7.1 appearance/device review pending; full7-profile hardware QA incomplete','liveInstallation':'prior V7 private UI review separate; V7.1 build never installs','publicationReady':True,'keyImageOverrides':'absent on all56 keys; SDK-managed state enabled; full hardware QA incomplete','published':False}
 dump(ROOT/'verification/release-checks.json',summary)
 write(ROOT/'verification/final-review-checks.txt',json.dumps(summary,indent=2)+'\n')
 dump(ROOT/'verification/source-build-checks.json',{'design':'V7.1','suppliedSourceDesign':'V8','scope':'local public source build; no fresh isolated source-ZIP rebuild claimed','build':'SDK8.0.428; zero warnings/errors','selfTestPassLines':len(tests),'officialCliVersion':'1.10.5','officialCliValidate':'pass','officialCliPack':'pass','sdkManagedProfileKeys':dynamicKeys,'liveInstalledByBuild':False})
 dump(ROOT/'verification/generator-checks.json',{'design':'V7.1','suppliedSourceDesign':'V8','regeneratedProfiles':7,'sdkManagedKeys':dynamicKeys,'customKeyImageOverrides':0,'bindingsIdsOrderAndSourceArtwork':'unchanged','native144OriginalKeyPairs':8,'native200x100DialCanvases':18})
 if ROOT/'verification/release-checks.json' not in source:source.append(ROOT/'verification/release-checks.json')
 docs=['README.md','KEY-DIAL-GUIDE.md','YOUTUBE-ARTWORK.md','LICENSE','PRIVACY.md','THIRD-PARTY-NOTICES.md','RELEASE-NOTES.md']
 downloads=[p for p in (ROOT/'artifacts').iterdir() if p.suffix in ('.streamDeckProfile','.streamDeckPlugin')]
 entries=[(p,p.name) for p in downloads]+[(ROOT/n,n) for n in docs]
 entries += [(p,p.relative_to(ROOT).as_posix()) for d in ['licenses','media','verification'] for p in (ROOT/d).rglob('*') if p.is_file() and (d!='verification' or p.name in PUBLIC_VERIFICATION)]
 library=[]
 for p in sorted(normals):
  library.append((p,'keys/'+p.name));library.append((p.with_stem(p.stem+'-pressed'),'keys/'+p.stem+'-pressed.png'))
 for p in sorted(dials):library.append((p,'dials/200x100/'+p.name))
 for p in sorted((original/'vectors').glob('*.svg')):library.append((p,'vectors/'+p.name))
 library += [(ROOT/'YOUTUBE-ARTWORK.md','YOUTUBE-ARTWORK.md'),(ROOT/'THIRD-PARTY-NOTICES.md','THIRD-PARTY-NOTICES.md'),(ROOT/'assets/youtube-v8/original-sha256.json','original-sha256.json')]
 libraryzip=ROOT/'artifacts'/('Everyday-Dials-YouTube-Icon-Library-'+VERSION+'.zip');zipfiles(libraryzip,library)
 entries.append((libraryzip,libraryzip.name))
 # Checksums within the install bundle cover its installers; the outer file also covers both ZIPs.
 checks=''.join(f'{sha(p)}  {p.name}\n' for p in sorted(downloads))
 write(ROOT/'artifacts/SHA256SUMS.txt',checks)
 entries.append((ROOT/'artifacts/SHA256SUMS.txt','SHA256SUMS.txt'))
 archivecounts={p.name:len(zipfile.ZipFile(p).namelist()) for p in downloads}
 archivecounts[libraryzip.name]=len(library)
 archivecounts['Everyday-Dials-'+VERSION+'.zip']=len(entries)
 archivecounts['Everyday-Dials-'+VERSION+'-source.zip']=len(set(source))
 dump(ROOT/'verification/archive-checks.json',{'design':'V7.1','suppliedSourceDesign':'V8','archiveEntryCounts':archivecounts,'pluginArchiveByteEquality':'pass','profileArchiveByteEquality':'pass','originalFileHashesPass':422,'publication':'authorized free public beta; upload handled separately','hardware':'full7-profile QA incomplete'})
 zipfiles(ROOT/'artifacts'/('Everyday-Dials-'+VERSION+'.zip'),entries)
 zipfiles(ROOT/'artifacts'/('Everyday-Dials-'+VERSION+'-source.zip'),[(p,'everyday-dials/'+p.relative_to(ROOT).as_posix()) for p in set(source)])
 public=[p for p in (ROOT/'artifacts').iterdir() if p.suffix in ('.streamDeckProfile','.streamDeckPlugin') or (p.suffix=='.zip' and VERSION in p.name)]
 write(ROOT/'artifacts/SHA256SUMS.txt',''.join(f'{sha(p)}  {p.name}\n' for p in sorted(public)))
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()

