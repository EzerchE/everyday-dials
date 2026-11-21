# V7.1 visual verification

Inspected native 144px normal/pressed keys and native 200x100 normal/left/right/pressed dial canvases from the supplied V8 archive, presented as V7.1. The thin upper highlight is removed. Speed normal/direction artwork includes Press: 1x and pressed artwork includes 1x; these identify the existing bounded reset action, never current-rate readback. Every selected native PNG, including muted variants, equals its supplied bytes. No Reset repaint, frame, glow or runtime overlay is added.

Fresh English hero, galleries and app icon use the current V7.1 assets. Native and enlarged private previews and a GIF retain the user's actual key order. These are static/generated asset examples, not hardware screenshots or new device validation. Full seven-profile hardware QA remains incomplete.

All 56 public keys retain SDK-managed state images. Runtime-critical code, bindings, IDs, order, generic layout and non-YouTube artwork remain unchanged; only public action Plugin.Version metadata moves to 0.1.1.0. Profile import requires Stream Deck 7.1.0 or later; the plugin's 6.5 minimum is separate. Windows 11 is the previously tested OS; Windows 10 is a technical runtime target without separate hardware validation.
