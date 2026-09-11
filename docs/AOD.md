# AOD and burn-in mitigation

AOD contains only the time and battery indicator on a black background, with
no arcs, weather, date, seconds, or continuous animation. The time font uses
black fill and a gray outline (#E0E0E0) that is 2.2 layout units wide.
The battery icon fills in proportion to the battery percentage and occupies
a small area. Since 0.2.1, the icon and percentage use the dimmer #A0A0A0,
while the time outline retains #E0E0E0. The watch's own ambient dimming is
applied in addition to these colors. Readability and actual brightness need
to be assessed on the physical watch.

The entire AOD group, including the colon, battery icon, and percentage, shifts
at each minute change. It cycles through 25 positions on a 5 × 5 grid, from
−2 to +2 layout units on both axes. Layout units scale from a 450 × 450 watch
face to the display. Only hour and minute data sources are used, so movement
does not require second ticks. Additional system shifting may apply; the
content has clearance from the screen edge. No system protection is disabled.

Automated checks cover all 1,440 times of day and 101 battery levels.
The pixel estimate uses a thicker 3-pixel outline and counts all lit pixels
without discounting gray colors or system dimming. This is a conservative
font-based estimate, not Samsung's official On Pixel Ratio (OPR) analysis or
a measurement of physical panel wear. See the
[validation report](VALIDATION.md) for results.

Pixel shifting, fewer lit pixels, and low intensity reduce risk. They do not
guarantee protection from OLED burn-in during long-term AOD use.

Primary sources checked on September 11, 2026:

- [Android: ambient mode](https://developer.android.com/training/wearables/wff/ambient)
- [WFF text outline reference](https://developer.android.com/reference/wear-os/wff/group/part/text/decoration/outline)
- [Samsung Watch Face Studio FAQ](https://developer.samsung.com/watch-face-studio/faq.html)
- [Samsung always-on design guide](https://developer.samsung.com/watch-face-studio/user-guide/always-on.html)

Samsung describes system shifting on some devices and recommends no more than
15% lit-pixel coverage. The specific Galaxy Watch9 system behavior has not yet
been measured.
