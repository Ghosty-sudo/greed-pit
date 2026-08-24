# GREED PIT

**Current playtest build:** 0.20.4 — Pressure Curve

GREED PIT is a mobile-first portrait survival game built around escalating enemy pressure, GREED contracts, and the decision to cash out or push deeper.

**Play the current GitHub Pages build:** https://ghosty-sudo.github.io/greed-pit/

## 0.20.4 highlights
- Enemy HP scales with both time alive and kills.
- Spawn pressure ramps harder as the run progresses and the player clears quickly.
- Vacuum starts lower and caps at 190, so movement remains necessary.
- GREED contract offers are fixed per level-up to prevent free reroll fishing.
- BAD INVESTMENT XP scaling is capped to prevent runaway level queues.
- XP orbs merge above the on-screen cap instead of losing XP.
- High-end damage and deep-run scaling have safety caps.
- Particle load was reduced for mobile performance.

The canonical release source is `index.html`. `sw.js` and `manifest.webmanifest` support the browser/PWA deployment, and `GREED_PIT_BROWSER_GAME.zip` packages the current release files.
