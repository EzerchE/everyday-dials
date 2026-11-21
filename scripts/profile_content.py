"""English profile content; native key sequences are independent of artwork."""
from copy import deepcopy

APPS = dict.fromkeys(['Chrome Daily','Stremio Cinema','Spotify Media','Telegram Daily','WhatsApp Daily','Bambu Studio Prep','YouTube Controls'])
COLORS = dict(zip(APPS, ['#8ab4f8', '#a78bfa', '#1ed760', '#35b6ed', '#25d366', '#00ae42', '#ff4545']))
BRANDS = dict(zip(APPS, ['chrome', 'stremio', 'spotify', 'telegram', 'whatsapp', 'bambu', 'youtube']))

YOUTUBE = {
    'name': 'YouTube',
    'keys': [
        ('PLAY /\nPAUSE', 'play', 'K'), ('PREVIOUS\nCHAPTER', 'skip-back', 'CTRL+LEFT'),
        ('NEXT\nCHAPTER', 'skip-forward', 'CTRL+RIGHT'), ('FULL\nSCREEN', 'maximize', 'F'),
        ('MUTE', 'volume-x', 'M'), ('CAPTIONS', 'captions', 'C'),
        ('MINI\nPLAYER', 'picture-in-picture-2', 'I'), ('BACK TO\nCHROME', 'arrow-left', '@parent'),
    ],
    'dials': [
        ('SEEK 10s\nPress: play', 'J', 'L', 'K'),
        ('SPEED\nPress: 1x', 'YTSPEEDDOWN', 'YTSPEEDUP', 'YTSPEEDRESET'),
        ('VIDEO VOLUME\nPress: mute', 'DOWN', 'UP', 'M'),
        ('FRAME STEP\nPause first', 'COMMA', 'PERIOD', 'K'),
    ],
}
PROFILES = {
    'Chrome Daily': {
        'keys': [
            ('TAB\nSEARCH', 'panels-top-left', 'CTRL+SHIFT+A'), ('NEW\nTAB', 'plus', 'CTRL+T'),
            ('REOPEN\nTAB', 'rotate-ccw', 'CTRL+SHIFT+T'), ('DOWNLOADS', 'download', 'CTRL+J'),
            ('ADDRESS\nSEARCH', 'search', 'CTRL+L'), ('FIND ON\nPAGE', 'text-search', 'CTRL+F'),
            ('BOOKMARK', 'bookmark', 'CTRL+D'), ('YOUTUBE', 'play', '@youtube'),
        ],
        'dials': [
            ('TABS\nPress: search', 'CTRL+SHIFT+TAB', 'CTRL+TAB', 'CTRL+SHIFT+A'),
            ('ZOOM\nPress: 100%', 'CTRL+SUBTRACT', 'CTRL+ADD', 'CTRL+0'),
            ('FIND RESULTS\nPress: find', 'SHIFT+F3', 'F3', 'CTRL+F'),
            ('MASTER VOLUME\nPress: mute', 'VOLDOWN', 'VOLUP', 'MUTE'),
        ],
        'child': deepcopy(YOUTUBE),
    },
    'Stremio Cinema': {
        'keys': [
            ('PLAY /\nPAUSE', 'play', 'SPACE'), ('FULL\nSCREEN', 'maximize', 'F'),
            ('BACK', 'arrow-left', 'BACKSPACE'), ('SEARCH', 'search', '0'),
            ('HOME', 'house', '1'), ('DISCOVER', 'compass', '2'),
            ('LIBRARY', 'library', '3'), ('SUBTITLE\nMENU', 'captions', 'S'),
        ],
        'dials': [
            ('SHORT SEEK\nPress: play', 'SHIFT+LEFT', 'SHIFT+RIGHT', 'SPACE'),
            ('PLAYER VOLUME\nPress: master mute', 'DOWN', 'UP', 'MUTE'),
            ('SUB DELAY 100ms\nPress: play', 'G', 'H', 'SPACE'),
            ('SUB SIZE\nPress: play', 'MINUS', 'EQUAL', 'SPACE'),
        ],
    },
    'Spotify Media': {
        'keys': [
            ('PLAY /\nPAUSE', 'play', 'PLAY'), ('PREVIOUS\nTRACK', 'skip-back', 'PREV'),
            ('NEXT\nTRACK', 'skip-forward', 'NEXT'), ('MASTER\nMUTE', 'volume-x', 'MUTE'),
            ('VOLUME\nDOWN', 'volume-1', 'VOLDOWN'), ('VOLUME\nUP', 'volume-2', 'VOLUP'),
            ('STOP', 'square', 'STOP'), ('SEARCH\nMUSIC', 'search', 'CTRL+L'),
        ],
        'dials': [
            ('MASTER VOLUME\nPress: mute', 'VOLDOWN', 'VOLUP', 'MUTE'),
            ('TRACKS\nPress: play', 'PREV', 'NEXT', 'PLAY'),
            ('FOCUS\nPress: activate', 'SHIFT+TAB', 'TAB', 'ENTER'),
            ('PAGE SCROLL\nPress: queue', 'PGUP', 'PGDOWN', 'ALT+SHIFT+Q'),
        ],
    },
    'Telegram Daily': {
        'keys': [
            ('SEARCH\nCHAT', 'text-search', 'CTRL+F'), ('CONTACTS', 'contact', 'CTRL+J'),
            ('SAVED\nMESSAGES', 'bookmark-check', 'CTRL+0'), ('ALL\nCHATS', 'messages-square', 'CTRL+1'),
            ('PREVIOUS\nCHAT', 'arrow-up', 'CTRL+PGUP'), ('NEXT\nCHAT', 'arrow-down', 'CTRL+PGDOWN'),
            ('PREVIOUS\nFOLDER', 'folder-up', 'CTRL+SHIFT+UP'), ('BACK /\nCANCEL', 'arrow-left', 'ESC'),
        ],
        'dials': [
            ('CHATS\nPress: search', 'CTRL+PGUP', 'CTRL+PGDOWN', 'CTRL+F'),
            ('FOLDERS\nPress: all', 'CTRL+SHIFT+UP', 'CTRL+SHIFT+DOWN', 'CTRL+1'),
            ('HISTORY\nPress: back', 'PGUP', 'PGDOWN', 'ESC'),
            ('MASTER VOLUME\nPress: mute', 'VOLDOWN', 'VOLUP', 'MUTE'),
        ],
    },
    'WhatsApp Daily': {
        'keys': [
            ('GLOBAL\nSEARCH', 'search', 'CTRL+ALT+SLASH'), ('SEARCH\nCHAT', 'text-search', 'CTRL+SHIFT+F'),
            ('NEW\nCHAT', 'message-circle-plus', 'CTRL+ALT+N'), ('CLOSE\nCHAT', 'arrow-left', 'ESC'),
            ('PREVIOUS\nCHAT', 'arrow-up', 'CTRL+BRACKETLEFT'), ('NEXT\nCHAT', 'arrow-down', 'CTRL+BRACKETRIGHT'),
            ('EMOJI', 'smile', 'CTRL+ALT+E'), ('GIF\nPANEL', 'image', 'CTRL+ALT+G'),
        ],
        'dials': [
            ('CHATS\nPress: search', 'CTRL+BRACKETLEFT', 'CTRL+BRACKETRIGHT', 'CTRL+SHIFT+F'),
            ('VOICE SPEED\nSelected message', 'SHIFT+COMMA', 'SHIFT+PERIOD', 'ESC'),
            ('FOCUS\nPress: back', 'SHIFT+TAB', 'TAB', 'ESC'),
            ('MASTER VOLUME\nPress: mute', 'VOLDOWN', 'VOLUP', 'MUTE'),
        ],
    },
    'Bambu Studio Prep': {
        'keys': [
            ('IMPORT\nMODEL', 'import', 'CTRL+I'), ('SAVE\nPROJECT', 'save', 'CTRL+S'),
            ('SLICE\nPLATE', 'layers', 'CTRL+R'), ('FIT\nVIEW', 'scan', 'Z'),
            ('MOVE', 'move', 'M'), ('ROTATE', 'rotate-3d', 'R'),
            ('SCALE', 'scaling', 'S'), ('DEFAULT\nVIEW', 'box', 'CTRL+0'),
        ],
        'dials': [
            ('LEFT / RIGHT\nPress: default', 'CTRL+5', 'CTRL+6', 'CTRL+0'),
            ('TOP / BOTTOM\nPress: isometric', 'CTRL+1', 'CTRL+2', 'CTRL+7'),
            ('FRONT / BACK\nPress: fit', 'CTRL+3', 'CTRL+4', 'Z'),
            ('MASTER VOLUME\nPress: mute', 'VOLDOWN', 'VOLUP', 'MUTE'),
        ],
    },
}
PROFILES['YouTube Controls'] = deepcopy(YOUTUBE)
PROFILES['YouTube Controls']['name'] = 'YouTube Controls'
PROFILES['YouTube Controls']['keys'][-1] = ('THEATER\nMODE', 'clapperboard', 'T')

# Preserve semantic action IDs while moving keys to adjacent, useful positions.
KEY_ORIGINAL_INDEX = {
    'Chrome Daily': list(range(8)), 'Stremio Cinema': [2, 0, 1, 7, 4, 5, 6, 3],
    'Spotify Media': [1, 0, 2, 3, 7, 4, 5, 'queue'],
    'Telegram Daily': [4, 0, 5, 7, 1, 2, 3, 6], 'WhatsApp Daily': [4, 1, 5, 3, 0, 2, 6, 7],
    'Bambu Studio Prep': list(range(8)), 'YouTube Controls': [1, 0, 2, 4, 5, 3, 6, 7],
}
for name, order in KEY_ORIGINAL_INDEX.items():
    original = PROFILES[name]['keys']
    PROFILES[name]['keys'] = [original[index] if isinstance(index, int) else ('QUEUE', 'list-music', 'ALT+SHIFT+Q') for index in order]
PROFILES['Chrome Daily']['keys'][7] = ('YOUTUBE', 'play', 'OPENYOUTUBE')
PROFILES['Spotify Media']['dials'][2] = ('FOCUS\nPress: activate', 'SHIFT+TAB', 'TAB', 'ENTER')
PROFILES['Spotify Media']['dials'][3] = ('SCROLL\nPress: queue', 'SCROLLUP', 'SCROLLDOWN', 'ALT+SHIFT+Q')
PROFILES['Chrome Daily']['child']['keys'] = [YOUTUBE['keys'][index] for index in [1, 0, 2, 4, 5, 3, 6, 7]]

# Main function glyph and optional small semantic modifier for round encoder art.
# This metadata never changes a key, dial direction, push binding, or identifier.
ENCODER_ART = {
    'Chrome Daily': [('panels-top-left', None), ('zoom-in', None), ('text-search', None), ('volume-2', None)],
    'Stremio Cinema': [('move-horizontal', None), ('volume-2', None), ('captions', 'clock'), ('captions', 'size')],
    'Spotify Media': [('volume-2', None), ('skip-forward', 'previous'), ('focus', None), ('move-vertical', None)],
    'Telegram Daily': [('messages-square', None), ('folders', None), ('rotate-ccw', 'clock'), ('volume-2', None)],
    'WhatsApp Daily': [('messages-square', None), ('gauge', 'voice'), ('focus', None), ('volume-2', None)],
    'Bambu Studio Prep': [('axis-3d', 'X'), ('axis-3d', 'Z'), ('axis-3d', 'Y'), ('volume-2', None)],
    'YouTube Controls': [('move-horizontal', None), ('gauge', None), ('volume-2', None), ('film', None)],
}

# Leftmost is the actual Windows master output volume. Values are original semantic
# indices, so moving a dial never changes its catalog ID or ActionID.
DIAL_ORIGINAL_INDEX = {
    'Chrome Daily': [3,0,1,2], 'Stremio Cinema': [1,0,2,3], 'Spotify Media': [0,1,2,3],
    'Telegram Daily': [3,0,1,2], 'WhatsApp Daily': [3,0,1,2], 'Bambu Studio Prep': [3,0,1,2],
    'YouTube Controls': [2,0,1,3],
}
PROFILES['Stremio Cinema']['dials'][1] = ('MASTER VOLUME\nPress: mute', 'VOLDOWN', 'VOLUP', 'MUTE')
PROFILES['YouTube Controls']['dials'][2] = ('MASTER VOLUME\nPress: mute', 'VOLDOWN', 'VOLUP', 'MUTE')
for name, order in DIAL_ORIGINAL_INDEX.items():
    old_dials=PROFILES[name]['dials'];old_art=ENCODER_ART[name]
    PROFILES[name]['dials']=[old_dials[index] for index in order]
    ENCODER_ART[name]=[old_art[index] for index in order]
PROFILES['Chrome Daily']['child']['dials']=deepcopy(PROFILES['YouTube Controls']['dials'])

# Public profiles have one independent page each; no URL pairing is included.
PROFILES['Chrome Daily'].pop('child', None)
