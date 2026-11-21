# Key and dial guide

Positions are left to right: keys 1–4 on the top row, 5–8 on the bottom row; dials 1–4 beneath the touchscreen. Turn counterclockwise (CCW) or clockwise (CW). Dial push and touchscreen tap perform the same action. The table is generated from the shipped profile settings and catalogs.

Master volume dials work independently of the foreground app. Other controls require the named app in the foreground, with the player or intended pane focused. Media keys use an exact Windows session when available, otherwise a guarded app-local fallback. Keyboard input is never a guarantee that the app accepted the action.

## Chrome Daily

Target executable: `chrome.exe`.

| Key | Label | Command | Behavior |
| --- | --- | --- | --- |
| 1 | TAB / SEARCH | `CTRL+SHIFT+A` | Guarded shortcut |
| 2 | NEW / TAB | `CTRL+T` | Guarded shortcut |
| 3 | REOPEN / TAB | `CTRL+SHIFT+T` | Guarded shortcut |
| 4 | DOWNLOADS | `CTRL+J` | Guarded shortcut |
| 5 | ADDRESS / SEARCH | `CTRL+L` | Guarded shortcut |
| 6 | FIND ON / PAGE | `CTRL+F` | Guarded shortcut |
| 7 | BOOKMARK | `CTRL+D` | Guarded shortcut |
| 8 | YOUTUBE | `OPENYOUTUBE` | Fixed YouTube URL in standard Chrome; permitted from another foreground app |

| Dial | Function | CCW | CW | Push / tap |
| --- | --- | --- | --- | --- |
| 1 | MASTER VOLUME | Volume down (`VOLDOWN`) | Volume up (`VOLUP`) | Mute (`MUTE`) |
| 2 | TABS | Previous tab (`CTRL+SHIFT+TAB`) | Next tab (`CTRL+TAB`) | Tab search (`CTRL+SHIFT+A`) |
| 3 | ZOOM | Zoom out (`CTRL+SUBTRACT`) | Zoom in (`CTRL+ADD`) | 100% zoom (`CTRL+0`) |
| 4 | FIND RESULTS | Previous result (`SHIFT+F3`) | Next result (`F3`) | Find (`CTRL+F`) |

## Stremio Cinema

Target executable: `stremio-shell-ng.exe`.

| Key | Label | Command | Behavior |
| --- | --- | --- | --- |
| 1 | BACK | `BACKSPACE` | Guarded shortcut |
| 2 | PLAY / / PAUSE | `PLAY` | Reliable next-action icon only when a matching session exists; otherwise neutral; fallback `SPACE` |
| 3 | FULL / SCREEN | `F` | Guarded shortcut |
| 4 | SUBTITLE / MENU | `S` | Guarded shortcut |
| 5 | HOME | `1` | Guarded shortcut |
| 6 | DISCOVER | `2` | Guarded shortcut |
| 7 | LIBRARY | `3` | Guarded shortcut |
| 8 | SEARCH | `0` | Guarded shortcut |

| Dial | Function | CCW | CW | Push / tap |
| --- | --- | --- | --- | --- |
| 1 | MASTER VOLUME | Volume down (`VOLDOWN`) | Volume up (`VOLUP`) | Mute (`MUTE`) |
| 2 | SHORT SEEK | Seek back (`SHIFT+LEFT`) | Seek forward (`SHIFT+RIGHT`) | Play / pause (`SPACE`) |
| 3 | SUB DELAY 100ms | Delay -100ms (`G`) | Delay +100ms (`H`) | Play / pause (`SPACE`) |
| 4 | SUB SIZE | Smaller (`MINUS`) | Larger (`EQUAL`) | Play / pause (`SPACE`) |

Seek, subtitle delay and subtitle-size bindings depend on Stremio version/player focus. Reliable playback state is not promised; neutral feedback is expected when unavailable.

## Spotify Media

Target executable: `Spotify.exe`.

| Key | Label | Command | Behavior |
| --- | --- | --- | --- |
| 1 | PREVIOUS / TRACK | `PREV` | Session command or guarded local fallback; fallback `CTRL+LEFT` |
| 2 | PLAY / / PAUSE | `PLAY` | Reliable next-action icon only when a matching session exists; otherwise neutral; fallback `SPACE` |
| 3 | NEXT / TRACK | `NEXT` | Session command or guarded local fallback; fallback `CTRL+RIGHT` |
| 4 | MASTER / MUTE | `MUTE` | Next mute/unmute operation from Windows audio state when available; key still app guarded |
| 5 | SEARCH / MUSIC | `CTRL+L` | Guarded shortcut |
| 6 | VOLUME / DOWN | `VOLDOWN` | Guarded shortcut |
| 7 | VOLUME / UP | `VOLUP` | Guarded shortcut |
| 8 | QUEUE | `ALT+SHIFT+Q` | Guarded shortcut |

| Dial | Function | CCW | CW | Push / tap |
| --- | --- | --- | --- | --- |
| 1 | MASTER VOLUME | Volume down (`VOLDOWN`) | Volume up (`VOLUP`) | Mute (`MUTE`) |
| 2 | TRACKS | Previous track (`PREV`) | Next track (`NEXT`) | Play / pause (`PLAY`) |
| 3 | FOCUS | Previous focus (`SHIFT+TAB`) | Next focus (`TAB`) | Activate (`ENTER`) |
| 4 | SCROLL | Scroll up (`SCROLLUP`) | Scroll down (`SCROLLDOWN`) | Queue (`ALT+SHIFT+Q`) |

Place the pointer over the desired Spotify pane for scroll. Focus push sends Enter and can activate the currently focused item. A unique matching Windows media session can provide a reliable next Play/Pause operation; absent or ambiguous sessions stay neutral.

## Telegram Daily

Target executable: `Telegram.exe`.

| Key | Label | Command | Behavior |
| --- | --- | --- | --- |
| 1 | PREVIOUS / CHAT | `CTRL+PGUP` | Guarded shortcut |
| 2 | SEARCH / CHAT | `CTRL+F` | Guarded shortcut |
| 3 | NEXT / CHAT | `CTRL+PGDOWN` | Guarded shortcut |
| 4 | BACK / / CANCEL | `ESC` | Guarded shortcut |
| 5 | CONTACTS | `CTRL+J` | Guarded shortcut |
| 6 | SAVED / MESSAGES | `CTRL+0` | Guarded shortcut |
| 7 | ALL / CHATS | `CTRL+1` | Guarded shortcut |
| 8 | PREVIOUS / FOLDER | `CTRL+SHIFT+UP` | Guarded shortcut |

| Dial | Function | CCW | CW | Push / tap |
| --- | --- | --- | --- | --- |
| 1 | MASTER VOLUME | Volume down (`VOLDOWN`) | Volume up (`VOLUP`) | Mute (`MUTE`) |
| 2 | CHATS | Previous chat (`CTRL+PGUP`) | Next chat (`CTRL+PGDOWN`) | Find (`CTRL+F`) |
| 3 | FOLDERS | Previous folder (`CTRL+SHIFT+UP`) | Next folder (`CTRL+SHIFT+DOWN`) | All chats (`CTRL+1`) |
| 4 | HISTORY | Page up (`PGUP`) | Page down (`PGDOWN`) | Back (`ESC`) |

## WhatsApp Daily

Target executable: `WhatsApp.Root.exe`.

| Key | Label | Command | Behavior |
| --- | --- | --- | --- |
| 1 | PREVIOUS / CHAT | `CTRL+BRACKETLEFT` | Guarded shortcut |
| 2 | SEARCH / CHAT | `CTRL+SHIFT+F` | Guarded shortcut |
| 3 | NEXT / CHAT | `CTRL+BRACKETRIGHT` | Guarded shortcut |
| 4 | CLOSE / CHAT | `ESC` | Guarded shortcut |
| 5 | GLOBAL / SEARCH | `CTRL+ALT+SLASH` | Guarded shortcut |
| 6 | NEW / CHAT | `CTRL+ALT+N` | Guarded shortcut |
| 7 | EMOJI | `CTRL+ALT+E` | Guarded shortcut |
| 8 | GIF / PANEL | `CTRL+ALT+G` | Guarded shortcut |

| Dial | Function | CCW | CW | Push / tap |
| --- | --- | --- | --- | --- |
| 1 | MASTER VOLUME | Volume down (`VOLDOWN`) | Volume up (`VOLUP`) | Mute (`MUTE`) |
| 2 | CHATS | Previous chat (`CTRL+BRACKETLEFT`) | Next chat (`CTRL+BRACKETRIGHT`) | Search chat (`CTRL+SHIFT+F`) |
| 3 | VOICE SPEED | Speed down (`SHIFT+COMMA`) | Speed up (`SHIFT+PERIOD`) | Back (`ESC`) |
| 4 | FOCUS | Previous focus (`SHIFT+TAB`) | Next focus (`TAB`) | Back (`ESC`) |

## Bambu Studio Prep

Target executable: `bambu-studio.exe`.

| Key | Label | Command | Behavior |
| --- | --- | --- | --- |
| 1 | IMPORT / MODEL | `CTRL+I` | Guarded shortcut |
| 2 | SAVE / PROJECT | `CTRL+S` | Guarded shortcut |
| 3 | SLICE / PLATE | `CTRL+R` | Guarded shortcut |
| 4 | FIT / VIEW | `Z` | Guarded shortcut |
| 5 | MOVE | `M` | Guarded shortcut |
| 6 | ROTATE | `R` | Guarded shortcut |
| 7 | SCALE | `S` | Guarded shortcut |
| 8 | DEFAULT / VIEW | `CTRL+0` | Guarded shortcut |

| Dial | Function | CCW | CW | Push / tap |
| --- | --- | --- | --- | --- |
| 1 | MASTER VOLUME | Volume down (`VOLDOWN`) | Volume up (`VOLUP`) | Mute (`MUTE`) |
| 2 | LEFT / RIGHT | Left view (`CTRL+5`) | Right view (`CTRL+6`) | Default (`CTRL+0`) |
| 3 | TOP / BOTTOM | Top view (`CTRL+1`) | Bottom view (`CTRL+2`) | Isometric (`CTRL+7`) |
| 4 | FRONT / BACK | Front view (`CTRL+3`) | Back view (`CTRL+4`) | Fit view (`Z`) |

Preparation/view shortcuts only. Slice may take time; there is no completion/status readback, printing command, printer identity or printer configuration.

## YouTube Controls

Target executable: `chrome.exe`.

| Key | Label | Command | Behavior |
| --- | --- | --- | --- |
| 1 | PREVIOUS / CHAPTER | `CTRL+LEFT` | Guarded shortcut |
| 2 | PLAY / / PAUSE | `PLAY` | Reliable next-action icon only when a matching session exists; otherwise neutral; fallback `K` |
| 3 | NEXT / CHAPTER | `CTRL+RIGHT` | Guarded shortcut |
| 4 | MUTE | `M` | Guarded shortcut |
| 5 | CAPTIONS | `C` | Guarded shortcut |
| 6 | FULL / SCREEN | `F` | Guarded shortcut |
| 7 | MINI / PLAYER | `I` | Guarded shortcut |
| 8 | THEATER / MODE | `T` | Guarded shortcut |

| Dial | Function | CCW | CW | Push / tap |
| --- | --- | --- | --- | --- |
| 1 | MASTER VOLUME | Volume down (`VOLDOWN`) | Volume up (`VOLUP`) | Mute (`MUTE`) |
| 2 | SEEK 10s | Back 10s (`J`) | Forward 10s (`L`) | Play / pause (`K`) |
| 3 | SPEED | Speed down (`YTSPEEDDOWN`) | Speed up (`YTSPEEDUP`) | Reset to 1x (`YTSPEEDRESET`) |
| 4 | FRAME STEP | Previous frame (`COMMA`) | Next frame (`PERIOD`) | Play / pause (`K`) |

Previous/next chapter sends Ctrl+Left / Ctrl+Right. The video must contain chapters. `YTSPEEDDOWN` and `YTSPEEDUP` send Shift+OEM comma/period; reset sends 32 slower packets then three faster packets, with no play/pause key. Frame stepping requires a paused video. Master volume is Windows output volume, not YouTube video volume. Select the YouTube profile manually.

## Interpreting feedback

The volume percentage is actual Windows master output readback. Other dial labels show the last shortcut sent and its intended operation; they do not read application state. Play/Pause remains neutral when the provider cannot reliably identify the session. Pressed artwork is a momentary acknowledgement. A yellow alert means the guard, input API or fixed website launch failed.

Commands such as `VOLDOWN`, `YTSPEEDRESET`, `SCROLLUP` and `OPENYOUTUBE` are internal allowlisted operations, not text typed into an app. The README lists executable, focus, keyboard-layout and installation limits.
