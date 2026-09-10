# GREED PIT — App Store release gate

This file separates verified implementation evidence from external/manual release work. A green browser build alone is not an App Store release.

## Current release candidate

- Store-facing version target: `1.0.0`
- Internal game version: `0.20.13`
- Canonical game SHA-256: `652b45741d3329191e4fc02cca156615ead4343ad615d1dfe36215b67c644aba`
- Candidate bundle ID: `com.ghostysudo.greedpit` (provisional until registered with Apple)
- Platform focus for first submission: iPhone / portrait gameplay
- Runtime wrapper: Capacitor 8.x

## Verified before native release hardening

- 0.20.13 canonical source reconstructs and packages successfully.
- Generated JavaScript passes syntax validation.
- Packaged browser candidate passes automated smoke/self-tests.
- GitHub Pages candidate deploys successfully.
- A prior Capacitor bootstrap compiled both Android debug and an unsigned iOS simulator app with Xcode 26.6; its final repository push failed only because `main` advanced during the job.
- Native preparation strips the PWA service worker and browser manifest and packages local audio assets.

## Native release CI gate

The native workflow must pass all of these on the current `0.20.13` source before this section can be considered verified:

- Capacitor sync creates or updates the iOS project.
- Native `www/index.html` is derived from the exact expected canonical SHA.
- Native bundle contains audio, active-run recovery, performance candidate markers, and in-app Privacy access.
- Xcode major version is 26 or newer.
- Unsigned iOS Simulator Debug build succeeds.
- Unsigned iOS Device Release build for `generic/platform=iOS` succeeds.
- Generated `ios/`, `www/`, and lockfile state are committed to `main` without a stale-head push race.

## App Store product-page prep

Prepared:

- Public Privacy Policy: `https://ghosty-sudo.github.io/greed-pit/privacy.html`
- Public Support page: `https://ghosty-sudo.github.io/greed-pit/support.html`
- App Store copy/metadata draft: `release/app-store/metadata.md`
- No-account / no-ad / no-analytics release direction.

Still required before submission:

- Production-quality app icon and launch branding replacing Capacitor defaults.
- App-owned `PrivacyInfo.xcprivacy` validated in the final app target and final privacy report reviewed.
- Final iPhone device-family/orientation settings verified in the generated Xcode project.
- Final marketing version/build number verified.
- App Store screenshots captured from the actual iPhone build at accepted dimensions.
- App privacy questionnaire completed from final binary behavior and third-party SDK manifests.
- Age-rating questionnaire completed.
- Accessibility declarations based on actual tested support, not assumptions.
- Pricing and availability selected.

## Physical-device release gate

Must be tested on a real iPhone before App Review submission:

- Install and cold launch.
- First-run tutorial and skip flow.
- Drag movement across screen edges and safe areas.
- Audio starts after user interaction and respects Audio On/Off across relaunches.
- Incoming interruption / background / foreground behavior.
- Active run checkpoints, force-close recovery, and Continue Saved Run.
- Portrait lock/orientation behavior.
- Notch/Dynamic Island/home-indicator safe-area layout.
- At least one 5+ minute run through the first Cash Out / Go Deeper decision.
- Sustained performance as enemy/projectile counts rise; no progressive lag regression.
- Device temperature/battery behavior is acceptable for sustained play.
- Death, retry, cash-out, home, pause/resume, and manual end-run paths.
- Fresh install and app-update persistence behavior.

## Apple-account blockers

These steps require the user’s Apple Developer/App Store Connect account, signing identity, or explicit account action and cannot be truthfully marked complete from repository CI alone:

- Active Apple Developer Program membership.
- Register the final bundle identifier.
- Create the App Store Connect app record.
- Create/use distribution signing credentials and provisioning.
- Produce a signed archive intended for App Store distribution.
- Upload the build to App Store Connect/TestFlight.
- Complete agreements, tax/banking, content rights, encryption/export-compliance, age rating, privacy, pricing, and availability fields as applicable.
- Test the uploaded build through TestFlight.
- Select the build and submit it to App Review.

## Definition of release-ready

GREED PIT is release-ready only after the current candidate passes native Release CI, the final visual/privacy metadata is present, a signed TestFlight build is installed and passes the physical-device gate, and App Store Connect has no unresolved submission blockers.
