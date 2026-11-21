# Public beta release verification

Everyday Dials v0.1.0-beta.1 is a free Windows Stream Deck+ community beta with V7 YouTube artwork. The artwork version does not change the numeric plugin version. The creator accepted the V7 appearance and the private YouTube installation was reviewed in Stream Deck. Limited YouTube speed controls have physical confirmation; full seven-profile hardware QA remains incomplete.

All 56 public key actions omit profile image overrides so SDK-managed normal, pressed and available media/mute feedback can appear. The generator and verifier enforce this for every profile. IDs, commands, ordering, source images and runtime behavior remain unchanged. Unknown player state remains neutral; only actual Windows master mute selects YouTube's muted dial canvas.

Release checks cover the .NET8 build, 350 isolated assertions, official Elgato CLI 1.10.5 validation/packing, all profile/page references, source and archive hashes, exact V7 key bytes/native dial dimensions, dependency redistribution hashes and privacy allowlists. All 422 V7 originals and 420 archived V6 originals retain provenance hashes. Supplied code is not executed.

The beta documents app/focus/keyboard-layout limits, the bounded shortcut-based 1x reset, manual profile selection, no bundled Easy Link or mapping, and no Marketplace approval. Source and release assets are prepared for publication by the reviewer; the build never installs into live settings or publishes. Optional Buy Me a Coffee support does not gate use.
