# GREED PIT

**Current playtest build:** 0.20.8 — Release Polish

**Play:** https://ghosty-sudo.github.io/greed-pit/

## 0.20.8
Content is frozen for this polish phase. This build focuses on making the existing game feel release-ready rather than adding new systems.

- Replaces the 0.20.7 cropped concept-art atlas with a clean transparent sprite system pre-rendered at startup.
- Player, Chaser, Brute, Collector, Tax Collector, and Debt enemies now use consistent ground anchors and scale.
- Four-direction facing uses hysteresis and short crossfades so diagonal movement no longer flickers between poses.
- Characters use four-frame movement loops plus slower idle animation for an animated feel without expensive per-frame vector drawing.
- Player skins now color sprite accents/eyes and a faint ground glow instead of placing a hard ring around the player.
- Elite and Debt readability no longer relies on a circular background sticker; silhouettes, palette, size, and HP bars carry the distinction.
- Shadows, hit feedback, XP orbs, bullets, and health pickups received lightweight presentation polish.
- Existing gameplay, GREED contracts, BAD IDEAS, Cycle economy, difficulty hardening, and the 0.20.7 late-XP scaling are preserved.

Canonical source SHA-256: `ad5a334fa83d0406aa81ad390acae74b85ce73d2e1a4c53e885e82775d43d329`.

## Deployment
The live `index.html` is a tiny shell that imports `loader-0208.js`. The loader fetches five version-specific Base64 text chunks, `gp0208.01.b64` through `gp0208.05.b64`, decodes them into one gzip byte stream, and reconstructs the exact canonical game with the browser's gzip `DecompressionStream`. Jarvis must write these `.b64` files using **Payload Mode: Body Text** so their Base64 text is preserved exactly.
