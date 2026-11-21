# Third-party notices

The root MIT license covers the original Everyday Dials code, profile configuration and original neutral artwork composition. It does not relicense third-party files, app trademarks, Microsoft software or the .NET runtime.

The creator supplied the current YouTube V7.1 PNGs/SVGs for this free release. All original bytes and provenance hashes are retained in `assets/youtube-v8/`; the supplied archive contains no separate upstream license. This notice does not assert a new upstream license or trademark permission for those assets. Runtime keys and native dial canvases use the supplied PNGs; all selected native key/dial bytes, including the supplied 1x labels, are used unchanged. Transparent encoder symbols are rendered from supplied SVGs. V4 assets in `assets/lovable-youtube-v4/` are archival source only and are not current marketing or setup instructions. Current galleries are labeled static V7.1 examples.

| Component | Shipped use | License / evidence |
| --- | --- | --- |
| Lucide icons and Feather-derived icons | Neutral semantic SVG glyphs and composed PNGs; no extracted app logos | Full ISC and Feather MIT notices in `licenses/lucide-LICENSE.txt`; [Lucide license](https://github.com/lucide-icons/lucide/blob/main/LICENSE) |
| Microsoft.Windows.SDK.NET.dll | Windows Runtime projection, unmodified from Microsoft.Windows.SDK.NET.Ref 10.0.19041.57, lib/net8.0 | Full [Windows SDK terms](https://go.microsoft.com/fwlink/?LinkId=822052) in `licenses/Microsoft-Windows-SDK-LICENSE.rtf`; [SDK redistributable list](https://learn.microsoft.com/en-us/legal/windows-sdk/redist), saved in `licenses/Microsoft-Windows-SDK-REDIST.html` |
| Microsoft.Windows.UI.Xaml.dll | Included unmodified by the same framework-dependent SDK runtime dependency set | Same SDK terms and explicitly listed net8.0 redistributable above; retained to match generated dependency metadata |
| WinRT.Runtime.dll | WinRT runtime interop, unmodified from the same package | Same SDK redistributable permission; full upstream MIT license in `licenses/WinRT.Runtime-MIT.txt`, from [CsWinRT](https://github.com/microsoft/CsWinRT/blob/master/LICENSE) |

`verification/dependency-hashes.json` records SHA-256 hashes and confirms the three shipped DLLs match the installed NuGet package's net8.0 files. The official SDK list permits those listed files to be distributed unmodified with a program to call WinRT APIs. No Windows SDK installer or unrelated SDK tools are shipped. The recipient installs .NET 8 separately under Microsoft's terms.

The official `@elgato/cli` 1.10.5 and its transitive npm dependencies are development tools only, installed locally from the lockfile. They are not bundled into the plugin, download bundle or source ZIP. Python, Pillow, ImageMagick and Segoe UI are build tools/system fonts, not redistributed font or tool files. The checked-in glyph sources and generated assets suffice for a normal source build without regenerating artwork.

Chrome, YouTube, Stremio, Spotify, Telegram, WhatsApp, Bambu Studio, Microsoft, Windows, Stream Deck and Elgato names belong to their respective owners. Names identify intended compatibility only. This is an independent community project with no endorsement, affiliation or blanket trademark license.
