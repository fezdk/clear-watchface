# Layout review: 0.2.0-preview1

The layout was installed as 0.2.0-preview1. The current version is 0.2.1,
which further dims the AOD battery icon and percentage to #A0A0A0.
The HTML pages and image preserve the original before/after review; the
preview's surrounding text is in English, while the watch-face labels and
archived screenshot retain their original Danish text.

Open `comparison.html` for a self-contained before/after view. The battery
slider changes the percentage, arc, and new icon. `comparison.png` shows 78%.

The preview is rendered from WFF XML, the bundled fonts, and the same icons.
It illustrates layout and does not simulate a specific display's AOD dimming.
`before.xml` preserves the layout from the installed version 0.1.0.

| Change | Before | Updated layout |
| --- | --- | --- |
| Battery icon | Empty outline | Proportional fill, including AOD |
| Lower arcs | Empty tracks | Hidden until data is available |
| Step text size | 13 | 17 |
| Active battery percentage size | 16 | 20 |
| Date size | 20 | 23 |
| Forecast heading size | 15 | 18 |
| Forecast temperature size | 20 | 26 |
| Forecast text size | 14 | 18 |
| AOD outline color | #808080 | #E0E0E0 |
| AOD outline width | 1.4 | 2.2 |
| AOD battery percentage size | 17 | 20 |

Sizes are WFF layout units, scaled to the display.
Pixel shifting and the black background are preserved.
The conservative AOD estimate is at most 4.638% lit-pixel coverage, including
a fully lit 32 × 20 battery area and a thicker 3-pixel outline. This is not a
burn-in guarantee.

XML validation, Android build, lint, and all ten functional tests passed.
The layout has been tried on the physical watch, and the user confirmed
improved AOD readability.

Generate a preview of the current source with `python3 tools/layout_preview.py`.
This refreshes both HTML files using the current watch-face XML; it does not
recreate the archived screenshot or the exact historical 0.2.0 preview.
Coverage estimate: `aod-coverage-preview.json`. Build and test logs are kept
locally only.
