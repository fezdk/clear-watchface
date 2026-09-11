# Version 0.1.0 validation

- Android APK build and lint passed: no errors and one Gradle update reminder.
- WFF 2 XML passed the official Google/Samsung validator.
- Google's Memory Footprint Evaluator passed: approximately 1.52 MB in both
  modes, below the 10 MB ambient and 100 MB active limits, using
  `--apply-v1-offload-limitations --estimate-optimization`.
- All nine functional tests passed. They cover empty/full arcs and values
  exceeding the goal, missing step goals, partially missing forecasts, cold
  temperatures and temperature changes within the forecast period,
  precipitation in each of the four hours, supported WFF functions, AOD
  shifting throughout a day, resource references, and an APK without runtime code.
- `check_aod.py`: maximum estimated lit-pixel coverage of 3.371%, with 08:38
  as the most demanding time. System indicators are not included.
- Installed in a separate Wear OS API 37 emulator with a round 454 × 454 display.
- Active mode checked with system data without weather and with example data:
  10:38, 6,400 / 10,000 steps, 78% battery, 16° now, and a 15–17° forecast with rain.
- AOD checked on the final production package after normal screen timeout:
  outlined time and battery visible, active graphics hidden, and system status
  `isAmbient=true`. Two captures across a minute change showed the battery
  indicator moving one pixel to the right: bounding box (310,110)–(391,123)
  became (311,110)–(392,123). See `aod-device.png` and `aod-next-minute.png`.
  Direct `KEYCODE_SLEEP` after repeated installations did not produce reliable
  ambient transitions in the emulator. Use normal timeout to reproduce.

Reports and the delivery APK were saved locally in `output/` and are excluded
from version control. Screenshots in this directory are actual emulator
captures. `active-example.png` uses a separate fixture package with example
data; AOD captures of the production package use the emulator's time.
The small dot at the bottom is a system indicator, not part of the watch face.

Further physical-watch checks are needed for brightness and readability in
different lighting, system pixel shifting and hardware offload, battery use
over time, the step goal's relationship to Samsung Health, and weather for the
current location and its updates. No long-term burn-in or battery-consumption
measurements have been performed.

## Version 0.2.1 update

The AOD battery was dimmed from #E0E0E0 to #A0A0A0. A direct XML comparison
with the installed 0.2.0-preview1 confirmed that only the battery icon and
percentage colors changed. Build, lint, and all ten tests passed. Installed
on the physical watch and verified as versionCode 3 / versionName 0.2.1.

The conservative AOD estimate for the updated layout is 4.638% maximum
lit-pixel coverage, including a fully lit 32 × 20 battery area and a thicker
3-pixel time outline. See the [layout review](../design/README.md).
