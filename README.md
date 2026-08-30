# GREED PIT

**Current playtest build:** 0.20.9 — Release Candidate

**Play:** https://ghosty-sudo.github.io/greed-pit/

## 0.20.9
Content remains frozen. This is a release-candidate polish build based on 0.20.8.

- Keeps the 0.20.8 transparent pre-rendered sprite system, consistent anchors/scaling, four-frame movement loops, idle motion, facing hysteresis/crossfades, skin accents, and combat presentation polish.
- Fixes the attack-speed timing path used by **FASTER BAD IDEAS**, **TURBO HEART**, and **BAD CREDIT**.
- Attack-speed upgrades now rescale the remaining shot cooldown immediately instead of inheriting the old slower interval.
- The firing clock stays primed when there are no enemies, so the player does not wait on a stale cooldown when a target appears.
- A bounded cadence scheduler now handles shot timing consistently through the 12 attacks/second cap and is covered by automated self-tests.
- Existing gameplay, GREED contracts, BAD IDEAS, Cycle economy, difficulty hardening, and late-XP scaling are unchanged.

Canonical source SHA-256: `ed73fd1a4e4e8cf0c442d6c89ed0864a0d38aec9bb99bf91c41c30679a60302d`.

## Deployment
The live `index.html` is a tiny shell that imports `loader-0209.js`. To minimize release risk, the 0.20.9 loader reuses the already-verified 0.20.8 payload chunks, applies a deterministic attack-speed/version patch in memory, verifies the exact 0.20.9 SHA-256, and then opens the game. No new gameplay payload chunks are required for this release candidate.
