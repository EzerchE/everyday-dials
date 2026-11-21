# YouTube V7 artwork and Windows shortcut guide

The supplied V7 library includes **28 labeled key icons with normal/pressed pairs (56 PNGs)** and **16 native 200×100 dial PNGs** in normal/left/right/pressed sets. The optional library also includes the clean SVG symbols. The included profile assigns eight keys and four dials. Other app profiles keep their existing artwork, catalogs, layout and timing.

## Included profile

Keys, top row: Previous Chapter (Ctrl+Left), Play/Pause (K), Next Chapter (Ctrl+Right), Mute (M). Bottom row: Captions (C), Full Screen (F), Mini Player (I), Theater Mode (T). Chapters/captions require available content. Focus the video and leave text fields first. Existing private key order is preserved; these public positions come from the shipped profile manifest.

Dials, left to right: **Windows master output volume** (2 percentage points per detent; mute push/tap), seek 10 seconds (J/L; K push/tap), speed (explicit Shift+OEM comma/period; bounded 1× reset push/tap), frame step (comma/period while paused; K push/tap). Speed reset is the creator-confirmed shortcut sequence, not a playback-rate query. The supplied design note's unassigned-speed-push suggestion does not change that accepted action.

## Feedback

Each YouTube encoder has exactly one `[0,0,200,100]` pixmap using the supplied native V7 PNGs. No layered title, tiny prose, bar, percentage or rate claim is added. Runtime image changes are cached. The speed-pressed PNG has one documented adaptation: the supplied dash is replaced with **Reset**, an action label. All other normal/left/right/pressed dial PNGs are selected byte for byte.

Physical turn direction returns neutral about 140 ms after the last tick, per visible context, even when a foreground guard blocks dispatch. This visual acknowledgement does not imply the player accepted a command. Production wakes at 20 ms for pending YouTube expiry; idle audio/media and all generic feedback keep the 750 ms polling cadence. Dial-down shows pressed feedback while held; release dispatches once. Turning while held cancels the release action. Touch tap sends one command and briefly shows pressed art.

Key feedback uses exact supplied labeled 144×144 normal/pressed pairs without additional borders, effects or native headings. The pressed image exists only while held; release restores neutral immediately, without the generic 350 ms flash. Very short taps may make that momentary state difficult to see. Play/Pause, browser mute, captions, fullscreen, theater and mini-player remain neutral because the plugin cannot identify the exact browser session. It never infers persistent state from its own keypress. No browser integration or permission was added.

Only actual **Windows master output mute** can select `dial-volume-muted` states. It does not describe YouTube's M-controlled mute. The software editor encoder symbols use the supplied SVG strokes in a transparent 144×144 image with a consistent 54 px optical box; there are no extra borders, labels or ornaments. The Stream Deck application's own gray frame is host-owned.

All 56 public profile keys omit custom `States.Image` overrides so the SDK can show normal, held and available media/mute feedback. YouTube encoder actions also omit the override. Included `Images/key-N.png` and dial images remain available for previews. Reliable playback state depends on the Windows provider; full seven-profile device acceptance remains incomplete. Native Hotkey State 2 does not automatically implement held-press feedback.

## Optional icon references

These are Windows browser shortcuts for manual customization, not extra assigned actions. Focus conditions and availability matter. The main [YouTube keyboard help](https://support.google.com/youtube/answer/7631406?hl=en) documents the standard controls; the live player's Keyboard shortcuts dialog was also checked for Theater Mode and caption font sizes on 2026-11-21.

| Icon filenames (omit .png / -pressed.png) | Windows shortcut | Condition |
| --- | --- | --- |
| play-pause | K | Player focused |
| fullscreen / mini-player / theater | F / I / T | Player mode support |
| mute / captions | M / C | Captions available for C |
| prev-chapter-alt / next-chapter-alt | Ctrl+Left / Ctrl+Right | Chapters available |
| prev-chapter / prev-video | Shift+P | Previous **video**, playlist only |
| next-chapter / next-video | Shift+N | Next video; suggested video outside playlists |
| rewind-10 / forward-10 | J / L | Player focused |
| rewind-5 / forward-5 | Left / Right | Seek bar focused |
| volume-up / volume-down | Up / Down | Seek bar focused; YouTube player volume |
| speed-up / speed-down | > / < | Player rate shortcuts |
| frame-back / frame-forward | comma / period | Video paused |
| restart / jump-end | Home / End | Seek bar focused; 0 also restarts |
| caption-size-up / caption-size-down | + / - | Captions available; listed by player; not hardware verified |
| search / shortcuts | / / ? | Leave text fields; ? is Shift+/ on common layouts |

The generic `prev-chapter`/`next-chapter` filenames are ambiguous; their supplied labels are Previous/Next. Use the explicit `-alt` icons for chapter controls, as the included profile does. The `=` caption-size alternative is unverified and is not recommended here. No macOS setup is supplied, and there is no blanket Ctrl-to-Cmd replacement rule.

## Files and provenance

`assets/youtube-v7/originals/` preserves all 422 supplied files byte for byte, including reference PNGs, SVGs, notes and source, with `original-sha256.json`. All 420 V6 originals remain archived with their hashes. Supplied code is not executed and supplied notes are reference data; they do not authorize new actions, permissions or guessed state. `verification/youtube-art-checks.json` compares assigned key bytes to these originals and validates native canvas dimensions. `youtube-v7-key-sha256.json` supplies staged self-test byte expectations.

`assets/lovable-youtube-v4/` remains archival source only. Its dense strip/marketing, uncorrected instructions and state claims are not current installation guidance. Current `media/youtube-library/` contains honest 1920×960 static V7 examples, not Marketplace-approved assets or hardware screenshots. AI assisted implementation, documentation and image composition; the supplied archive contains no separate third-party license. See the third-party notices.
