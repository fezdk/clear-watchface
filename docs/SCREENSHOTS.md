# README screenshot capture

Captured on October 22, 2026, from a newly created, isolated Wear OS API 37
emulator using the `wearos_large_round` profile (454 × 454, 320 dpi) and
`system-images;android-37.0;android-wear-signed;x86_64` with KVM acceleration.
These are native `adb screencap` captures, not browser mockups. The PNGs are
published unchanged; no brightness adjustment or retouching was applied.

Both images show the current layout, including the red–yellow–green active
arcs, in the separate `dk.nezar.clearwatchface.fixture` package. The fixture
uses 10:38, Friday September 11, 6,400 / 10,000 steps, 78% battery, 16° current
weather, and a rainy 15–17° forecast. These are synthetic values, including
the displayed date. The production package still uses system data sources.
The screenshot fixture freezes time, so these images do not test pixel shifting.

The active capture shows the normal interactive state. The AOD capture was
taken 18 seconds after waking the display, with a 10-second screen timeout;
`dumpsys power` confirmed `mWakefulness=Dozing`. System dimming remains visible.
The small bottom dot is an emulator system indicator. These captures do not
measure physical-watch brightness, battery use, or OLED wear.

## Reproduction

Use a separate emulator with the installed Wear OS image above. Replace
`emulator-5582` with its exact serial; never run these setup commands against
a personal watch. Build requirements are listed in the main README.

```sh
python3 tools/make_fixture.py /tmp/clear-readme-fixture --scenario rain
(cd /tmp/clear-readme-fixture && ./gradlew :watchface:assembleDebug)
adb -s emulator-5582 install -r /tmp/clear-readme-fixture/watchface/build/outputs/apk/debug/watchface-debug.apk
adb -s emulator-5582 shell am broadcast -a com.google.android.wearable.app.DEBUG_SURFACE --es operation set-watchface --es watchFaceId dk.nezar.clearwatchface.fixture
adb -s emulator-5582 shell settings put global ambient_enabled 1
adb -s emulator-5582 shell dumpsys battery unplug
adb -s emulator-5582 shell settings put system screen_off_timeout 10000
adb -s emulator-5582 shell input keyevent KEYCODE_HOME
adb -s emulator-5582 shell input keyevent KEYCODE_WAKEUP
sleep 2
adb -s emulator-5582 exec-out screencap -p > screenshot-active.png
sleep 16
adb -s emulator-5582 exec-out screencap -p > screenshot-aod.png
adb -s emulator-5582 shell dumpsys power
```

The debug broadcast is an emulator/system debugging interface; availability
may vary between system images. This procedure does not require modifying
production XML to force ambient mode.

## Validation and artifact hashes

- Production APK: official WFF 2 XML validation, Android build, and lint passed.
- All 11 functional tests passed, including the progress color crossfade test.
- Screenshot fixture: WFF 2 validation and Android build passed.
- Both APKs passed signature and ZIP alignment checks; package IDs were verified.
- Both screenshots were visually inspected for the expected state and layout.
- No physical device was changed during this capture.

SHA-256:

| Artifact | SHA-256 |
| --- | --- |
| Production APK | `d67707179c46693abf3c06e38b3f49c34103151333c05985953897618f5f2003` |
| Screenshot fixture APK | `a31645d60747a27ecbcbd36d396fb4bbd47c6a9d9e01824428200b7b26e4ae4a` |
| `screenshot-active.png` | `594a149894047fad703d8bdf7d0131e271d9127c688955630e622fa51aa1ba31` |
| `screenshot-aod.png` | `507424b44b97bc2bf191ba7c72f8dcba74038da756e10e81add76500aa7dca55` |
