# Clear Watchface

**Status:** 0.2.1 er installeret og versionskontrolleret på uret.
AOD-batteriets ikon og procent er dæmpet; tidens lysstyrke og pixel shifting er bevaret.
Se [før/efter](design/comparison-v2.html) for layoutændringerne.

Selvstændig urskive i Watch Face Format 2. Første version til afprøvning på
Samsung Galaxy Watch9; implementeret og afprøvet i Wear OS-emulator.
Pakken er ressourcebaseret og indeholder ingen appkode eller ledsager-app.

## Design og data

- Aktiv: 24-timers ur uden sekunder, ugedag og dato, aktuelt vejr og et interval
  for de næste fire timer.
- Fire buer med ikoner/tal samlet inden for buerne: skridt øverst til venstre,
  batteri øverst til højre. De to nederste er skjult, indtil der er valgt data til dem.
- AOD: dæmpede konturtal og et lille konturbatteri med procent øverst til højre.
- Systemets lokale tidszone bruges automatisk. Datotekst afhænger af systemets lokalisering; de øvrige labels er danske.
- Skridt/mål, batteri og vejr hentes via WFF-systemdatakilder. Vi antager ikke,
  at de nødvendigvis matcher en bestemt Samsung Health- eller vejrapp.
- Manglende skridtmål viser kun antal skridt; aldrig `0 / 0`.
- Manglende vejr/prognose vises tydeligt. Prognosen kræver alle fire timer.
  Intervallet er laveste/højeste temperatur i timerne +1 til +4. Teksten angiver
  varslet torden, slud, sne eller regn i perioden, med den rækkefølge som prioritet.
  Uden disse vises “Ingen nedbør meldt”. Der er ingen hardkodet vejrdata i APK'en.
- Datakvalitet, opdateringshastighed og tilgængelighed for aktuel lokation
  afhænger af urets WFF-vejrleverandør. Skal afprøves på det fysiske ur.

## Byg og kontroller

Kræver Java 17+, Android SDK platform 36 og adgang til Gradle-afhængigheder ved
første build. `local.properties` skal indeholde `sdk.dir=/sti/til/Android/Sdk`,
eller `ANDROID_HOME` skal være sat. Minimum Android API er 35.

```sh
./gradlew :watchface:assembleDebug :watchface:lintDebug
python3 tools/test_watchface.py
python3 tools/check_aod.py
```

Den officielle WFF XML-validator kører automatisk før hvert build.
Python-tests er udviklerværktøjer og pakkes ikke ind i urskiven.
`check_aod.py` kræver Pillow og laver et konservativt estimat af lysende pixels.

APK: `watchface/build/outputs/apk/debug/watchface-debug.apk`.
Dette er en debug-signeret testudgave; der er ikke publiceret noget i en butik.

## Installation på et ur

Aktivér udviklerindstillinger og trådløs debugging på uret. Par og forbind fra
Android SDK's `adb`; brug de porte, uret selv viser (parring og forbindelse har
normalt forskellige porte):

```sh
adb pair UR_IP:PARRINGSPORT
adb connect UR_IP:DEBUGPORT
adb -s UR_IP:DEBUGPORT install -r watchface/build/outputs/apk/debug/watchface-debug.apk
```

Vælg derefter **Clear Watchface** i urets urskivevælger. Aktivér Always On Display
på uret for at afprøve AOD. Version 0.2.1 er installeret på det fysiske ur; læselighed og data afprøves af brugeren.

## Redigering

`tools/generate.py` er kilden til layout, udtryk og de små tegnede ikoner.
Efter en ændring: `python3 tools/generate.py`, derefter byg og test igen.
XML-filen `watchface/src/main/res/raw/watchface.xml` og de genererede ikoner er
inkluderet, så almindeligt Android-build ikke kræver Python.
Bundtede DejaVu-fonte giver ens geometri mellem aktiv og ambient visning.
Licenser findes i `licenses/`.

`tools/make_fixture.py /tmp/clear-fixture --scenario rain` opretter et separat
projekt med eksempeldata og pakkenavnet `dk.nezar.clearwatchface.fixture`.
Scenarier: rain, dry, snow, storm, missing, partial. Det ændrer ikke den rigtige
urskive. Testpakker er mærket **Clear · TESTDATA** og skal ikke bruges som ur.
Skærmbilleder i `docs/` er fra emulatoren; `active-example.png` bruger eksempeldata,
mens `aod-device.png` viser produktionspakken med emulatorens tid og batteri.

Se [AOD og burn-in](docs/AOD.md) og [validering](docs/VALIDATION.md).

Lokale SDK-indstillinger, buildresultater, logs og signeringsnøgler er ikke
versionsstyret. Gradle bruger den lokale debug-nøgle ved testbuild.
