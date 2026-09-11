# Validering af version 0.1.0

- Android APK-build og lint bestået (0 fejl; én opdateringspåmindelse om Gradle).
- WFF 2 XML valideret med Googles/Samsungs officielle validator.
- Googles Memory Footprint Evaluator: bestået, ca. 1,52 MB i begge tilstande,
  under 10 MB ambient / 100 MB aktiv,
  `--apply-v1-offload-limitations --estimate-optimization`.
- Alle 9 funktionstests bestået. De kontrollerer tomme/fulde buer og værdier over mål, manglende
  skridtmål, delvist manglende prognose, kulde og temperaturudsving midt i
  perioden, nedbør i hver af de fire timer, tilladte WFF-funktioner,
  AOD-forskydning gennem et døgn, ressourcehenvisninger og APK uden runtime-kode.
- `check_aod.py`: maksimum 3,371 % lysende pixels i det konservative estimat,
  med det mest krævende klokkeslæt 08:38. Systemindikatorer er ikke medregnet.
- Installeret i en separat Wear OS API 37-emulator, rund skærm 454 × 454.
- Aktiv tilstand kontrolleret med systemdata uden vejr, og med eksempeldata:
  10:38, 6.400 / 10.000 skridt, 78 % batteri, 16° nu, 15–17° og regn i perioden.
- AOD kontrolleret på den endelige produktionspakke efter normal skærmtimeout:
  konturtid og batteri synlige, aktiv grafik skjult; systemstatus `isAmbient=true`.
  To optagelser over et minutskift viste batteriindikatoren flyttet én pixel
  mod højre: bounding box (310,110)–(391,123) til (311,110)–(392,123).
  Se `aod-device.png` og `aod-next-minute.png`.
  Direkte `KEYCODE_SLEEP` efter gentagne installationer gav ikke pålidelige
  ambient-overgange i emulatoren. Brug normal timeout til reproduktion.

Rapporter og leveringsfil blev gemt lokalt i `output/` og er ikke versionsstyret. Skærmbilleder i denne mappe er
faktiske emulatoroptagelser. `active-example.png` bruger en separat testpakke
med eksempeldata; AOD-optagelser af produktionspakken bruger emulatorens tid.
Den lille prik nederst er en systemindikator og ikke en del af urskiven.

Udestår på det fysiske ur: lysstyrke/læselighed i forskelligt lys, systemets
pixel shifting og hardware-offload, batteriforbrug over tid, skridtmålets
sammenhæng med Samsung Health samt vejr for aktuel lokation og opdateringer.
Der er ikke gennemført langtidsmåling af burn-in eller batteriforbrug.

## Opdatering 0.2.1

AOD-batteri dæmpet fra #E0E0E0 til #A0A0A0. Direkte XML-sammenligning med
den installerede 0.2.0-preview1 bekræfter, at kun batteriikonets og procentens
farver er ændret. Build, lint og alle 10 tests består. Installeret på det
fysiske ur og verificeret som versionCode 3 / versionName 0.2.1.
