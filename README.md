# GREED PIT

**Current playtest build:** 0.20.6 — Know Your Problems

GREED PIT is a mobile-first portrait survival game built around escalating enemy pressure, GREED contracts, movement, and the decision to cash out or push deeper.

**Play the current GitHub Pages build:** https://ghosty-sudo.github.io/greed-pit/

## 0.20.6 highlights
- Added a dedicated **BAD IDEAS** Home Screen catalog. Unlocked Bad Ideas show their full effect and max stacks; locked cards remain gray, show their name and unlock requirement, and hide the effect until discovered.
- Scrap unlocks now happen inside the BAD IDEAS catalog instead of through the old generic Home Screen unlock button. Existing `meta.unlocked` saves remain compatible.
- **CURRENT BUILD is now tappable** from level-up and Pause. Tapping an owned upgrade opens a detail panel showing current stacks, live stat information, the cap, and how many stacks remain.
- Level-up cards now show `STACKS current / max` before selection.
- Every normal upgrade now has an explicit useful stack cap. Once an upgrade is maxed—or its underlying stat reaches the hard cap through another effect—it leaves the normal level-up roll pool so completed cards stop crowding out unfinished builds.
- Removed the old overflow-conversion behavior from capped normal upgrades such as Vacuum, movement, attack speed, and projectiles. GREED contracts remain separate risk/reward effects.
- Vacuum remains capped at 190, projectiles at 8, attack speed at 12/s, movement at 700 px/s, and crit at 78%.
- The drag-anywhere control behavior is unchanged, but the on-screen joystick indicator is smaller and more transparent so it blocks less of the arena.
- 0.20.5 PIT ZONES, earlier enemy HP pressure, steeper XP curve, and 0.20.4 safety/performance hardening remain intact.

Canonical source SHA-256: `173343fe17857c06cfd1f4713a1b15176a2c37ab6b936ae66d9ddbb43a33d1fe`.

The canonical release source is `index.html`. `sw.js` and `manifest.webmanifest` support browser/PWA deployment.

## GitHub Pages layout
GitHub Pages deploys a tiny `index.html` shell that imports `loader-0206.js`. The loader fetches `gp0206.01.b64` through `gp0206.05.b64`, decodes and concatenates their gzip bytes, verifies the 0.20.6 build marker, and then opens the exact canonical HTML. The service worker pre-caches this complete runtime set for repeat/offline-safe loading after installation.
