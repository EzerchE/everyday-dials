"""Current V7.1 images; supplied V4 marketing remains archival source only."""
from pathlib import Path
import shutil
from render_youtube import preview
ROOT=Path(__file__).resolve().parents[1]
def main():
    out=ROOT/'media/youtube-library';out.mkdir(parents=True,exist_ok=True)
    for name,title in [('thumbnail-1920x960.png','YouTube V7.1 — eight keys, four minimal dials'),('gallery-1-all-icons.png','V7.1 assigned profile — neutral key and dial examples'),('gallery-2-pressed-feedback.png','V7.1 momentary feedback — held keys and dial push'),('gallery-3-dial-artwork.png','V7.1 native canvases — normal, direction and press')]:preview(ROOT/'plugin/com.ezerche.everydaydials.sdPlugin',out/name,title)
    shutil.copyfile(ROOT/'assets/youtube-v8/originals/keys/labeled/288/play-pause.png',out/'app-icon-288x288.png')
    print('Rendered four current V7.1 1920x960 static galleries; no obsolete V4 bars/text used.')
if __name__=='__main__':main()
