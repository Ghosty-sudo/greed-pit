# GREED PIT

**Current playtest build:** 0.20.10 — Release Candidate

Content remains frozen. This patch continues release polish from 0.20.9 without adding gameplay systems.

## 0.20.10
- Keeps the verified 0.20.9 attack-speed timing correction and the 0.20.8 sprite/anchor/facing foundation.
- Replaces flat colored-circle thumbnails in the SKINS menu with the same cached player sprite system used in gameplay, so cosmetic previews now match the actual character presentation.
- Fixes the stale title-screen footer that still identified the build as Prototype 0.20.6.
- Feedback reports now identify build 0.20.10.
- No new enemies, mechanics, monetization, or balance changes.

## Validation
Canonical source size: 74485 bytes  
Canonical SHA-256: `2878c02aa0da57390d8d4355b9a9c1e6fc150d14aae479b660c2592998eb022a`

Validation target: JavaScript syntax, built-in self-tests, 390×844 mobile smoke test, skin-menu render, 180-enemy stress test, and exact loader reconstruction/hash verification.

## GitHub Pages deployment
Deploy version-specific payload chunks plus `loader-0210.js`, then update `sw.js`, `manifest.webmanifest`, and `README.md`. Switch the tiny `index.html` shell last. Base64 chunk files are plain text and should be sent through Jarvis as **Body Text**.
