# GREED PIT

**Current playtest build:** 0.20.7 — Visual Update

**Play:** https://ghosty-sudo.github.io/greed-pit/

## 0.20.7
- Approved generated GREED PIT character art is now used in live gameplay for Player, Chaser, Brute, Collector, and Tax Collector.
- Characters turn between front / 3-4 / side / back views. Player facing follows movement; enemies face their chase direction.
- Elite and Debt enemies retain orange/gold aura cues for readability.
- Existing player skins now tint the aura around the new player model.
- Joystick indicator is smaller and more transparent.
- The post-level-8 XP growth term is **100x stronger** than 0.20.6, preserving quick early levels but sharply slowing mass-level chains once a build starts clearing quickly.
- Bad Ideas, Current Build inspection, PIT ZONES, GREED contracts, extraction Cycles, and prior hardening remain.

Canonical source SHA-256: `f3263073afe3f8b03cee80eaa340b669e2de9505307d085d450dfb139bced07c`.

The generated character atlas is embedded directly inside the canonical game payload so the live build does not depend on separate image-file requests.

## GitHub Pages layout
The live `index.html` is a tiny shell that imports `loader-0207.js`. The loader reconstructs the exact embedded-atlas 0.20.7 gameplay source from `gp0207.01.b64` through `gp0207.06.b64`.
