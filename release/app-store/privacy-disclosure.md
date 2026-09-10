# GREED PIT — App Store privacy disclosure basis

This is a pre-submission evidence note, not a substitute for reviewing the final signed binary and Xcode privacy report.

## Intended App Store Connect answer

If the final signed build matches the current `0.20.13` release candidate, the intended App Privacy data-collection answer is:

> No, we do not collect data from this app.

Apple defines collection for the App Privacy label around transmitting data off-device in a way that allows the developer or third-party partners to access it beyond servicing the request in real time. The current game does not intentionally transmit gameplay, identifiers, analytics, advertising data, accounts, saved progress, or feedback to the developer.

## Current implementation evidence

The release direction intentionally contains:

- No user account or login.
- No advertising SDK.
- No analytics SDK.
- No tracking SDK.
- No location, contacts, camera, microphone, photo-library, health, or Bluetooth permission flow.
- Gameplay/progression/settings stored locally.
- Active-run recovery stored locally.
- In-game feedback reports stored locally; copying a report is an explicit user action.
- Bundled/local game audio.
- A local in-app privacy screen.
- A user-initiated external link to the public Privacy Policy.

## Final verification required

Before publishing App Privacy answers:

1. Generate the final Xcode privacy report/archive report.
2. Inspect the app target and all packaged third-party SDK privacy manifests.
3. Confirm there are no newly added network/analytics/advertising SDKs.
4. Confirm the signed build does not upload gameplay, feedback, identifiers, or diagnostics to a developer-controlled service.
5. If any final behavior differs, update both this document and App Store Connect before submission.

## Privacy policy URLs

- Public Privacy Policy: `https://ghosty-sudo.github.io/greed-pit/privacy.html`
- Support: `https://ghosty-sudo.github.io/greed-pit/support.html`

## Future-change rule

Adding analytics, ads, accounts, cloud saves, remote feedback submission, crash reporting, or other data transmission is a privacy-impacting release change and requires a fresh disclosure review before shipping.
