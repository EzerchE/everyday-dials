from pathlib import Path
import io, json, math, os, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cairosvg

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent if HERE.name == 'source' else HERE / 'handoff'
ROOT.mkdir(parents=True, exist_ok=True)
VECTORS = ROOT / 'vectors'

T = {
    'canvas': '#0B0D10', 'surfaceTop': '#30343B', 'surfaceMid': '#191C21',
    'surfaceBottom': '#090B0E', 'foreground': '#F5F7FA', 'muted': '#A8B0BA',
    'faint': '#69727D', 'accent': '#FF5058', 'activeForeground': '#FF7A80',
    'border': '#FFFFFF24', 'sheet': '#15181C', 'card': '#101317'
}
REGULAR = '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
BOLD = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
SYMBOL = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def font(size, bold=False, symbol=False):
    return ImageFont.truetype(SYMBOL if symbol else BOLD if bold else REGULAR, size)

def center(draw, text, x, y, size, color, bold=False, symbol=False):
    draw.text((x, y), text, font=font(size, bold, symbol), fill=color, anchor='mm')

def fit_center(draw, text, x, y, size, max_width, color, bold=False):
    while size > 12 and draw.textlength(text, font=font(size, bold)) > max_width:
        size -= 1
    center(draw, text, x, y, size, color, bold)

def hexrgb(value):
    value = value.lstrip('#')
    return tuple(int(value[i:i+2], 16) for i in (0, 2, 4))

def save(im, rel):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)

def svg_icon(name, size, color):
    data = (VECTORS / f'{name}.svg').read_text().replace('#F3F5F7', color).replace('#F5F7FA', color)
    return Image.open(io.BytesIO(cairosvg.svg2png(
        bytestring=data.encode(), output_width=size, output_height=size
    ))).convert('RGBA')

def vertical_surface(size, kind='normal', direction=None, dial=False):
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w]
    t = (yy / max(1, h - 1)) ** 0.82
    top = np.array(hexrgb(T['surfaceTop']), dtype=float)
    mid = np.array(hexrgb(T['surfaceMid']), dtype=float)
    bottom = np.array(hexrgb(T['surfaceBottom']), dtype=float)
    split = 0.46
    upper = np.minimum(t / split, 1.0)[..., None]
    lower = np.maximum((t - split) / (1 - split), 0.0)[..., None]
    rgb = top * (1 - upper) + mid * upper
    rgb = rgb * (1 - lower) + bottom * lower
    # Broad, restrained top light gives depth without a glossy or neon look.
    radial = np.exp(-(((xx - w * .50) / (w * .72)) ** 2 + ((yy + h * .10) / (h * .60)) ** 2) * 2.0)
    rgb += radial[..., None] * np.array([8.0, 8.5, 9.5])
    if kind in ('pressed', 'active'):
        strength = 1.0 if kind == 'pressed' else .52
        tint = np.array([34.0, 4.0, 9.0]) * strength
        rgb += tint * (0.30 + radial[..., None] * .70)
    if direction:
        cx = w * (.05 if direction == 'left' else .95)
        side = np.exp(-(((xx - cx) / (w * .48)) ** 2 + ((yy - h * .52) / (h * .90)) ** 2) * 2.2)
        rgb += side[..., None] * np.array([30.0, 3.0, 8.0])
    rgb = np.clip(rgb, 0, 255).astype('uint8')
    im = Image.fromarray(rgb, 'RGB').convert('RGBA')
    if dial:
        # Each 200x100 encoder slot has its own quiet, rounded surface.
        mask = Image.new('L', size, 0)
        md = ImageDraw.Draw(mask)
        md.rounded_rectangle((5, 5, w - 6, h - 6), radius=26, fill=255)
        canvas = Image.new('RGBA', size, hexrgb(T['canvas']) + (255,))
        canvas.paste(im, (0, 0), mask)
        im = canvas
    return im

def rounded_glow(im, box, radius, color, width, blur, alpha):
    layer = Image.new('RGBA', im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle(box, radius=radius, outline=hexrgb(color) + (alpha,), width=width)
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(im, layer)

def key_surface(pressed=False, active=False):
    kind = 'pressed' if pressed else 'active' if active else 'normal'
    im = vertical_surface((288, 288), kind)
    d = ImageDraw.Draw(im)
    box = (14, 14, 273, 273)
    if pressed:
        im = rounded_glow(im, box, 36, T['accent'], 7, 9, 105)
        d = ImageDraw.Draw(im)
        d.rounded_rectangle(box, radius=36, outline=T['accent'], width=3)
        d.rounded_rectangle((20, 20, 267, 267), radius=31, outline='#6A3B41', width=1)
        # Short accent dash: a second, readable held-press cue.
        d.rounded_rectangle((116, 248, 172, 252), radius=2, fill=T['accent'])
    else:
        d.rounded_rectangle(box, radius=36, outline='#454A52' if not active else '#654047', width=2)
    return im

LABELS = {
    'play-pause': 'Play / Pause', 'fullscreen': 'Full Screen', 'captions': 'Captions',
    'mute': 'Mute', 'prev-chapter': 'Previous', 'next-chapter': 'Next',
    'prev-chapter-alt': 'Prev Chapter', 'next-chapter-alt': 'Next Chapter',
    'prev-video': 'Prev Video', 'next-video': 'Next Video', 'mini-player': 'Mini Player',
    'theater': 'Theater', 'frame-back': 'Frame −1', 'frame-forward': 'Frame +1',
    'restart': 'Restart', 'jump-end': 'Jump to End', 'caption-size-up': 'Caption +',
    'caption-size-down': 'Caption −', 'search': 'Search', 'shortcuts': 'Shortcuts',
    'volume-up': 'Volume +', 'volume-down': 'Volume −', 'speed-up': 'Speed +',
    'speed-down': 'Speed −', 'rewind-10': 'Back 10s', 'forward-10': 'Forward 10s',
    'rewind-5': 'Back 5s', 'forward-5': 'Forward 5s'
}

def make_key(name, pressed=False, labeled=True):
    im = key_surface(pressed=pressed)
    d = ImageDraw.Draw(im)
    size = (112 if labeled else 140) - (6 if pressed else 0)
    ic = svg_icon(name, size, '#FFF8F8' if pressed else T['foreground'])
    cy = (105 if labeled else 144) + (3 if pressed else 0)
    im.alpha_composite(ic, ((288 - size) // 2, round(cy - size / 2)))
    if labeled:
        fit_center(d, LABELS[name], 144, 207, 25, 238, T['foreground'])
    return im.convert('RGB')

STATES = {
    'playback-playing': {'icon': 'pause', 'label': 'Pause', 'status': 'Playing', 'active': True, 'action': 'K'},
    'playback-paused': {'icon': 'play', 'label': 'Play', 'status': 'Paused', 'active': False, 'action': 'K'},
    'captions-on': {'icon': 'captions', 'label': 'Captions', 'status': 'On', 'active': True, 'action': 'C'},
    'captions-off': {'icon': 'captions', 'label': 'Captions', 'status': 'Off', 'active': False, 'action': 'C'},
    'mute-on': {'icon': 'mute', 'label': 'Unmute', 'status': 'Muted', 'active': True, 'action': 'M'},
    'mute-off': {'icon': 'unmute', 'label': 'Mute', 'status': 'Sound On', 'active': False, 'action': 'M'},
    'fullscreen-on': {'icon': 'fullscreen', 'label': 'Full Screen', 'status': 'On', 'active': True, 'action': 'F'},
    'fullscreen-off': {'icon': 'fullscreen', 'label': 'Full Screen', 'status': 'Off', 'active': False, 'action': 'F'},
    'theater-on': {'icon': 'theater', 'label': 'Theater', 'status': 'On', 'active': True, 'action': 'T'},
    'theater-off': {'icon': 'theater', 'label': 'Theater', 'status': 'Off', 'active': False, 'action': 'T'},
    'mini-player-on': {'icon': 'mini-player', 'label': 'Mini Player', 'status': 'On', 'active': True, 'action': 'I'},
    'mini-player-off': {'icon': 'mini-player', 'label': 'Mini Player', 'status': 'Off', 'active': False, 'action': 'I'}
}

def make_state_key(name, pressed=False, labeled=True):
    cfg = STATES[name]
    im = key_surface(pressed=pressed, active=cfg['active'])
    d = ImageDraw.Draw(im)
    size = (108 if labeled else 140) - (6 if pressed else 0)
    ic = svg_icon(cfg['icon'], size, '#FFF8F8' if pressed else T['foreground'])
    cy = (98 if labeled else 140) + (3 if pressed else 0)
    im.alpha_composite(ic, ((288 - size) // 2, round(cy - size / 2)))
    # Persistent state dot remains stable during momentary press feedback.
    dot = (246, 29, 260, 43)
    d.ellipse(dot, fill=T['accent'] if cfg['active'] else None,
              outline=T['accent'] if cfg['active'] else T['faint'], width=2)
    if labeled:
        fit_center(d, cfg['label'], 144, 183, 24, 232, T['foreground'])
        center(d, cfg['status'], 144, 224, 20,
               T['activeForeground'] if cfg['active'] else T['muted'])
    return im.convert('RGB')

DIALS = {
    'volume': {'title': 'Volume', 'left': '−', 'right': '+', 'push': 'Mute'},
    'seek': {'title': 'Seek', 'left': '−10s', 'right': '+10s', 'push': 'Play / Pause'},
    'speed': {'title': 'Speed', 'left': '−', 'right': '+', 'push': '1x'},
    'frame': {'title': 'Frame', 'left': '−1', 'right': '+1', 'push': 'Play / Pause'}
}

def dial_surface(state='normal'):
    direction = state if state in ('left', 'right') else None
    im = vertical_surface((400, 200), 'pressed' if state == 'pressed' else 'normal', direction, dial=True)
    d = ImageDraw.Draw(im)
    box = (10, 10, 389, 189)
    if state == 'pressed':
        im = rounded_glow(im, box, 24, T['accent'], 6, 8, 95)
        d = ImageDraw.Draw(im)
        d.rounded_rectangle(box, radius=24, outline=T['accent'], width=3)
    else:
        d.rounded_rectangle(box, radius=24, outline='#42474E', width=2)
    return im

def chevron(draw, x, y, direction, color):
    pts = [(x + (8 if direction == 'left' else -8), y - 13), (x, y), (x + (8 if direction == 'left' else -8), y + 13)]
    draw.line(pts, fill=color, width=4, joint='curve')

def make_dial(name, state='normal'):
    cfg = DIALS[name]
    im = dial_surface(state)
    d = ImageDraw.Draw(im)
    center(d, cfg['title'], 200, 39, 23, T['muted'])
    if state == 'pressed':
        fit_center(d, cfg['push'] or '—', 200, 101, 35, 320, T['foreground'])
        d.rounded_rectangle((174, 132, 226, 136), radius=2, fill=T['accent'])
    else:
        left_color = T['accent'] if state == 'left' else T['foreground'] if state == 'normal' else T['faint']
        right_color = T['accent'] if state == 'right' else T['foreground'] if state == 'normal' else T['faint']
        center(d, cfg['left'], 123, 102, 37, left_color, symbol=True)
        center(d, '/', 200, 102, 28, T['faint'])
        center(d, cfg['right'], 277, 102, 37, right_color, symbol=True)
        if state in ('left', 'right'):
            x = 50 if state == 'left' else 350
            chevron(d, x, 101, state, T['accent'])
            if state == 'left':
                d.rounded_rectangle((92, 133, 154, 137), radius=2, fill=T['accent'])
            else:
                d.rounded_rectangle((246, 133, 308, 137), radius=2, fill=T['accent'])
    if cfg['push']:
        center(d, 'Press: ' + cfg['push'], 200, 166, 20, T['muted'])
    return im.convert('RGB')

DIAL_STATES = {
    'volume-muted': ('Volume', 'Muted', 'Unmute', True),
    'volume-unmuted': ('Volume', 'Sound On', 'Mute', False),
    'seek-playing': ('Seek', 'Playing', 'Pause', True),
    'seek-paused': ('Seek', 'Paused', 'Play', False)
}

def make_state_dial(name, pressed=False):
    title, status, push, active = DIAL_STATES[name]
    im = dial_surface('pressed' if pressed else 'normal')
    if active and not pressed:
        # Active dial state uses the same restrained warm surface as active keys.
        overlay = vertical_surface((400, 200), 'active', dial=True)
        im = Image.blend(im, overlay, .58)
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((10, 10, 389, 189), radius=24, outline='#654047', width=2)
    d = ImageDraw.Draw(im)
    center(d, title, 200, 39, 23, T['muted'])
    center(d, status, 200, 101, 35, T['activeForeground'] if active else T['foreground'])
    center(d, 'Press: ' + push, 200, 166, 20, T['muted'])
    return im.convert('RGB')

def rounded_paste(base, tile, xy, radius):
    mask = Image.new('L', tile.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, tile.width - 1, tile.height - 1), radius=radius, fill=255)
    base.paste(tile, xy, mask)

# Export all artwork at 2x and native resolution.
for name in LABELS:
    for pressed in (False, True):
        suffix = '-pressed' if pressed else ''
        for variant in ('labeled', 'icon-only'):
            im = make_key(name, pressed, variant == 'labeled')
            save(im, Path('keys') / variant / '288' / f'{name}{suffix}.png')
            save(im.resize((144, 144), Image.Resampling.LANCZOS), Path('keys') / variant / '144' / f'{name}{suffix}.png')
for name in STATES:
    for pressed in (False, True):
        suffix = '-pressed' if pressed else ''
        for variant in ('labeled', 'icon-only'):
            im = make_state_key(name, pressed, variant == 'labeled')
            for size in (288, 144):
                save(im.resize((size, size), Image.Resampling.LANCZOS), Path('states') / variant / str(size) / f'{name}{suffix}.png')
for name in DIALS:
    for state in ('normal', 'left', 'right', 'pressed'):
        suffix = '' if state == 'normal' else '-' + state
        im = make_dial(name, state)
        save(im, Path('dials/400x200') / f'dial-{name}{suffix}.png')
        save(im.resize((200, 100), Image.Resampling.LANCZOS), Path('dials/200x100') / f'dial-{name}{suffix}.png')
for name in DIAL_STATES:
    for pressed in (False, True):
        suffix = '-pressed' if pressed else ''
        im = make_state_dial(name, pressed)
        for size, folder in (((400, 200), '400x200'), ((200, 100), '200x100')):
            save(im.resize(size, Image.Resampling.LANCZOS), Path('dials/states') / folder / f'dial-{name}{suffix}.png')

(ROOT / 'state-map.json').write_text(json.dumps(STATES, indent=2))
(ROOT / 'design-tokens.json').write_text(json.dumps(T, indent=2))
layout = {'$schema': 'https://schemas.elgato.com/streamdeck/plugins/layout.json', 'id': 'RefinedVideoFeedback',
          'items': [{'key': 'canvas', 'type': 'pixmap', 'rect': [0, 0, 200, 100], 'value': '../dials/200x100/dial-volume.png'}]}
(ROOT / 'layout').mkdir(exist_ok=True)
(ROOT / 'layout/encoder-canvas.json').write_text(json.dumps(layout, indent=2))

# Reference 01: polished target layout with the exact assets the developer should place.
im = Image.new('RGB', (1600, 1100), T['sheet'])
d = ImageDraw.Draw(im)
center(d, 'VIDEO CONTROLS', 800, 55, 29, T['muted'], bold=True)
center(d, 'Refined feedback system  /  V8', 800, 100, 25, T['foreground'])
order = ['prev-chapter-alt', 'play-pause', 'next-chapter-alt', 'mute', 'captions', 'fullscreen', 'mini-player', 'theater']
for i, name in enumerate(order):
    x = 272 + (i % 4) * 272
    y = 150 + (i // 4) * 242
    rounded_paste(im, make_key(name).resize((208, 208), Image.Resampling.LANCZOS), (x, y), 27)
for i, name in enumerate(DIALS):
    rounded_paste(im, make_dial(name).resize((256, 128), Image.Resampling.LANCZOS), (272 + i * 264, 666), 16)
for i, name in enumerate(DIALS):
    x = 400 + i * 264
    d.ellipse((x - 62, 832, x + 62, 956), fill=T['card'], outline='#343940', width=2)
    ic = svg_icon('dial-' + name, 58, T['foreground'])
    im.paste(ic, (x - 29, 849), ic)
    center(d, DIALS[name]['title'], x, 991, 21, T['muted'])
center(d, 'English labels  •  consistent 24 px icon grid  •  no unverified live values', 800, 1053, 19, T['muted'])
save(im, 'reference/01-target-layout.png')

# Reference 02: normal and held press for the eight primary keys.
im = Image.new('RGB', (1600, 900), T['sheet'])
d = ImageDraw.Draw(im)
center(d, 'KEY FEEDBACK', 800, 45, 27, T['muted'], bold=True)
center(d, 'Normal state remains quiet; held press adds an inset frame, short accent dash and 5% icon compression.', 800, 86, 21, T['muted'])
for row, name in enumerate(order[:4]):
    y = 135 + row * 175
    center(d, LABELS[name], 245, y + 72, 24, T['foreground'])
    for col, pressed in enumerate((False, True)):
        tile = make_key(name, pressed).resize((144, 144), Image.Resampling.LANCZOS)
        rounded_paste(im, tile, (520 + col * 405, y), 18)
        center(d, 'Pressed' if pressed else 'Normal', 592 + col * 405, y + 158, 17, T['muted'])
center(d, 'Use the same geometry on every key; do not add another border or glow in the plugin.', 800, 870, 19, T['muted'])
save(im, 'reference/02-key-feedback.png')

# Reference 03: all dial states, with values retained during turn feedback.
im = Image.new('RGB', (1680, 1080), T['sheet'])
d = ImageDraw.Draw(im)
center(d, 'DIAL FEEDBACK', 840, 42, 27, T['muted'], bold=True)
for row, name in enumerate(DIALS):
    for col, state in enumerate(('normal', 'left', 'right', 'pressed')):
        x, y = 20 + col * 415, 90 + row * 240
        rounded_paste(im, make_dial(name, state), (x, y), 20)
        center(d, f'{DIALS[name]["title"]}  /  {state}', x + 200, y + 218, 17, T['muted'])
save(im, 'reference/03-dial-feedback.png')

# Reference 04: persistent states and their held-press versions.
im = Image.new('RGB', (1500, 1650), T['sheet'])
d = ImageDraw.Draw(im)
center(d, 'PERSISTENT STATES', 750, 42, 27, T['muted'], bold=True)
center(d, 'Status remains visible during press; red communicates confirmation, not decoration.', 750, 80, 20, T['muted'])
names = list(STATES)
for row in range(6):
    for col, (idx, pressed) in enumerate(((row * 2, False), (row * 2 + 1, False), (row * 2, True), (row * 2 + 1, True))):
        name = names[idx]
        x, y = 35 + col * 368, 120 + row * 248
        rounded_paste(im, make_state_key(name, pressed).resize((200, 200), Image.Resampling.LANCZOS), (x, y), 25)
        center(d, name + (' / press' if pressed else ''), x + 100, y + 222, 15, T['muted'])
save(im, 'reference/04-persistent-states.png')

# Reference 05: every general action, normal and pressed, at a reviewable size.
for variant in ('labeled', 'icon-only'):
    im = Image.new('RGB', (1600, 1940), T['sheet'])
    d = ImageDraw.Draw(im)
    center(d, f'ALL ACTIONS  /  {variant}', 800, 40, 27, T['muted'], bold=True)
    for i, name in enumerate(LABELS):
        col, row = i % 4, i // 4
        x, y = 24 + col * 398, 85 + row * 258
        for j, pressed in enumerate((False, True)):
            tile = make_key(name, pressed, variant == 'labeled').resize((174, 174), Image.Resampling.LANCZOS)
            rounded_paste(im, tile, (x + j * 188, y), 21)
        center(d, name, x + 180, y + 202, 17, T['muted'])
    save(im, f'reference/05-all-actions-{variant}.png')

# Reference 06: exact native pixels; this exposes any legibility problem honestly.
im = Image.new('RGB', (800, 100), T['canvas'])
for i, name in enumerate(DIALS):
    im.paste(make_dial(name).resize((200, 100), Image.Resampling.LANCZOS), (i * 200, 0))
save(im, 'reference/06-native-touch-strip.png')
im = Image.new('RGB', (1152, 288), T['sheet'])
for i, name in enumerate(order):
    im.paste(make_key(name).resize((144, 144), Image.Resampling.LANCZOS), ((i % 4) * 288, (i // 4) * 144))
    im.paste(make_key(name, True).resize((144, 144), Image.Resampling.LANCZOS), ((i % 4) * 288 + 144, (i // 4) * 144))
save(im, 'reference/07-native-key-feedback.png')

# Reference 08: persistent dial states.
im = Image.new('RGB', (850, 1060), T['sheet'])
d = ImageDraw.Draw(im)
center(d, 'DIAL STATUS', 425, 40, 25, T['muted'], bold=True)
for row, name in enumerate(DIAL_STATES):
    for col, pressed in enumerate((False, True)):
        x, y = 15 + col * 415, 80 + row * 240
        rounded_paste(im, make_state_dial(name, pressed), (x, y), 20)
        center(d, name + (' / press' if pressed else ''), x + 200, y + 216, 16, T['muted'])
save(im, 'reference/08-dial-persistent-states.png')

print('V8 PNG exports:', len(list(ROOT.rglob('*.png'))))
print('V8 SVG sources:', len(list(ROOT.rglob('*.svg'))))
