# GREED PIT

**Active recovery baseline:** 0.20.9 — Release Candidate gameplay baseline

GREED PIT is a mobile-first portrait survival/action game targeting iOS and Android. The browser/GitHub Pages build is the current development and playtest vehicle.

## Release recovery — 2026-09-09

The repository had advanced 0.20.10 staging assets, but the root `index.html` was empty and the prior 0.20.10 canonical-source reconstruction had failed integrity validation. Do not treat 0.20.10 as a verified playable release.

`main` has been deliberately rolled back to the previously verified 0.20.9 deployment shell while keeping the 0.20.10 payload/loader artifacts intact for later forensic recovery. The rollback uses the exact historical 0.20.9 `index.html`, service worker, manifest, loader, and unchanged `gp0208.01.b64` through `gp0208.05.b64` payload blobs.

### Safety checkpoints
- Pre-recovery head: `0feab663fa3fe83f51bb598eb1262abcff796803`
- Backup branch: `backup/pre-greed-pit-recovery-2026-09-09`
- Recovery branch: `sol/greed-pit-release-recovery-2026-09-09`
- Restored public entry-point commit: `332dde7af6ddb5ecc926ca06cf17a1d831a88d16`

## Current release blockers
1. Confirm the restored 0.20.9 GitHub Pages build completes deployment and passes a real browser/mobile smoke test.
2. Recover/export a trustworthy editable canonical source before further gameplay changes.
3. Integrate the generated audio pack and validate mobile audio behavior.
4. Run the commercial mobile maturity audit: safe areas, suspend/resume, settings, accessibility basics, persistence, performance, privacy/permissions, monetization, and store UX.
5. Add an actual iOS/Android packaging pipeline. The current repository is a browser/PWA development build and does not yet contain native App Store / Google Play packaging.
6. Prepare store assets/metadata, production builds, installation testing, and submission evidence.

## 0.20.10 staging status
- `loader-0210.js` and `gp0210.01.b64` through `gp0210.05.b64` remain in the repository.
- Expected reconstructed canonical SHA-256: `2878c02aa0da57390d8d4355b9a9c1e6fc150d14aae479b660c2592998eb022a`.
- Do not switch the public entry point back to 0.20.10 until the payload reconstructs cleanly, matches that hash, and passes the intended validation suite.

## Next development sequence
**VERIFY 0.20.9 RUNTIME → RECOVER CANONICAL SOURCE → INTEGRATE AUDIO → VALIDATE 0.20.11 → MOBILE MATURITY/PACKAGING → STORE SUBMISSION PREP**
