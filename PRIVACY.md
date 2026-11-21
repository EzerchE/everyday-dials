# Privacy

The plugin connects to the local Stream Deck WebSocket endpoint supplied at launch. It has no analytics, remote service, account, update checker or telemetry in its runtime code. It does not save activity logs or personal settings. Stream Deck, .NET, the operating system, downloaded apps and development tools have their own separate behavior and policies.

For guarded shortcut delivery it reads the foreground process name and, for Spotify scrolling, the process beneath the pointer. It reads the Windows default output audio endpoint's volume/mute status. Windows media-session source identity and playback status are used to choose safe app-specific media operations and state feedback. The runtime does not read media titles, browsing history, page URLs, messages, contacts, files or printer configuration.

The fixed YouTube launcher opens `https://www.youtube.com/` in the standard Chrome installation. This is the only intentional remote website opened by a profile control. No website content is fetched by the plugin itself. Source contains optional local diagnostic command-line probes for developers; they print process/media identities or keyboard-layout facts to the caller's console and are not run automatically or included as generated diagnostic output in the release.

The public profiles use newly generated IDs and an anonymous zero device UUID. They contain no original device identity, app association paths, accounts, third-party profiles, Easy Link mappings, logs, backups or printer settings. Recipients bind imported profiles to their own device. Source package build caches and machine-specific intermediate files are excluded.
