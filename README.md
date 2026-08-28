# GREED PIT

**Current playtest build:** 0.20.5 — Pit Fights Back

GREED PIT is a mobile-first portrait survival game built around escalating enemy pressure, GREED contracts, movement, and the decision to cash out or push deeper.

**Play:** https://ghosty-sudo.github.io/greed-pit/

## 0.20.5
- Telegraphed PIT ZONES begin after the opening portion of the run. Move out before they erupt or take a meaningful HP hit.
- Hazard waves escalate from one zone to several simultaneous zones as the run continues.
- Enemy HP pressure ramps earlier from both time alive and enemies killed.
- XP requirements rise more sharply with level so late upgrades do not arrive nearly as quickly as early upgrades.
- Vacuum remains capped at 190 so collecting XP still requires movement.
- 0.20.4 hardening remains: GREED offer caching, BAD INVESTMENT XP cap, XP-orb merging, numeric safety limits, and mobile particle caps.

## GitHub Pages layout
The canonical human-readable 0.20.5 source is stored with the GREED PIT project artifacts. GitHub Pages uses `index.html` + `loader.js` + `game.01.b64` through `game.13.b64`. The chunk files concatenate to the Base64 representation of the gzip-compressed canonical HTML; the loader reconstructs and decompresses it in-browser before starting the game.

The old repository browser ZIP is removed during this release so an outdated package cannot be mistaken for the current build. The complete 0.20.5 browser release remains stored with the canonical project artifacts.
