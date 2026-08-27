# GREED PIT

**Current playtest build:** 0.20.5 — Pit Fights Back

GREED PIT is a mobile-first portrait survival game built around escalating enemy pressure, GREED contracts, movement, and the decision to cash out or push deeper.

**Play the current GitHub Pages build:** https://ghosty-sudo.github.io/greed-pit/

## 0.20.5 highlights
- Added telegraphed **PIT ZONES** beginning after the opening minute. A zone snapshots the player's area, glows for about 1.65 seconds, then erupts. Staying inside costs meaningful HP; moving out avoids all zone damage.
- Hazard waves intensify from one zone to multiple simultaneous zones as the run gets deeper, with a protected cadence floor so warnings remain readable.
- Enemy HP now ramps sooner from both time alive and enemies killed, specifically targeting the 2–5 minute section that was becoming too easy.
- XP requirements now rise more sharply as level increases, while the first few levels remain quick enough to establish a build.
- Vacuum remains capped at 190 so XP collection still requires movement.
- 0.20.4 safeguards remain: GREED offer caching, BAD INVESTMENT XP cap, XP-orb merging, damage/deep-run limits, level/Cycle sequencing protection, and the 600-particle mobile ceiling.
- The page now explicitly links its web manifest and registers the versioned network-first service worker.

The canonical release source is `index.html`. `sw.js` and `manifest.webmanifest` support browser/PWA deployment, and `GREED_PIT_BROWSER_GAME.zip` packages the current release files.
