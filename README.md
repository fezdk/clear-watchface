# Clear Watchface

A standalone Watch Face Format 2 watch face for Samsung Galaxy Watch9,
with a clear active display and a minimal always-on display (AOD).
The package contains resources only, with no runtime app code or companion app.

**Status:** Version 0.2.1 is installed on the physical watch, with its installed
version verified. The AOD battery icon and percentage are dimmed; the time
brightness and pixel shifting are preserved. See the
[before/after preview](design/comparison-v2.html) for the earlier layout changes.
The watch face has also been tested in a Wear OS emulator.

## Design and data

- Active display: 24-hour time without seconds, weekday and date, current
  weather, and a forecast summary for the next four hours.
- Four arcs with icons and values placed inside them: steps at the upper left,
  battery at the upper right. The two lower arcs remain hidden until data is
  assigned to them.
- AOD: dimmed outlined digits and a small battery icon with proportional fill
  and a percentage at the upper right.
- The system's local time zone is used automatically. Date text follows system
  localization; other watch-face labels are currently in Danish.
- Steps, step goal, battery, and weather come from WFF system data sources.
  They are not assumed to match any particular Samsung Health or weather app.
- When the step goal is unavailable, only the step count is shown, never `0 / 0`.
- Missing weather or forecast data is indicated explicitly. The forecast
  requires all four hours and shows the lowest and highest temperatures across
  hours +1 through +4. Its text reports thunderstorms, sleet, snow, or rain,
  in that priority order. Otherwise it reports no precipitation forecast
  (currently displayed as “Ingen nedbør meldt”). The APK has no hardcoded
  weather data.
- Data quality, refresh rate, and availability for the current location depend
  on the watch's WFF weather provider and require verification on the physical
  watch.

## Build and validate

Requires Java 17+, Android SDK platform 36, and access to Gradle dependencies
for the first build. Set `sdk.dir=/path/to/Android/Sdk` in `local.properties`,
or set `ANDROID_HOME`. The minimum Android API level is 35.

```sh
./gradlew :watchface:assembleDebug :watchface:lintDebug
python3 tools/test_watchface.py
python3 tools/check_aod.py
```

The official WFF XML validator runs automatically before each build.
The Python tests are development tools and are not packaged in the watch face.
`check_aod.py` requires Pillow and estimates lit-pixel coverage conservatively.

APK: `watchface/build/outputs/apk/debug/watchface-debug.apk`.
This is a debug-signed test build; no store release has been published.

## Install on a watch

Enable developer options and wireless debugging on the watch. Pair and connect
using the Android SDK's `adb` and the ports displayed by the watch. Pairing and
connection usually use different ports:

```sh
adb pair WATCH_IP:PAIRING_PORT
adb connect WATCH_IP:DEBUG_PORT
adb -s WATCH_IP:DEBUG_PORT install -r watchface/build/outputs/apk/debug/watchface-debug.apk
```

Select **Clear Watchface** in the watch-face picker. Enable Always On Display
on the watch to try AOD. Version 0.2.1 is installed on the physical watch;
readability and data behavior are being evaluated by the user.

## Editing

`tools/generate.py` is the source for the layout, expressions, and small drawn
icons. After editing it, run `python3 tools/generate.py`, then build and test.
The XML file `watchface/src/main/res/raw/watchface.xml` and generated icons are
included, so a normal Android build does not require Python.
Bundled DejaVu fonts provide consistent geometry in active and ambient modes.

`python3 tools/make_fixture.py /tmp/clear-fixture --scenario rain` creates a
separate project with example data and package name
`dk.nezar.clearwatchface.fixture`. Available scenarios: rain, dry, snow, storm,
missing, partial. It does not modify the actual watch face. Fixture packages
are labeled **Clear · TESTDATA** and are not intended for everyday use.
Screenshots in `docs/` are from the emulator: `active-example.png` uses example
data, while `aod-device.png` shows the production package with the emulator's
time and battery level. Screenshots retain the watch face's Danish labels.

See [AOD and burn-in](docs/AOD.md) and [validation](docs/VALIDATION.md).

Local SDK settings, build outputs, logs, and signing keys are excluded from
version control. Gradle uses the local debug key for test builds.

## License

Original project code and documentation are licensed under the
[MIT License](LICENSE).
Bundled third-party components retain their own licenses: see
[DejaVu fonts](licenses/DejaVu.txt),
[WFF validator](licenses/WFF-validator.txt), and dependency notices in the JARs.
