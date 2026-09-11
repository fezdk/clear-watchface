# AOD og forebyggelse af burn-in

AOD indeholder kun tiden og batteriindikatoren. Sort baggrund, ingen buer,
vejr, dato, sekundvisning eller kontinuerlig animation. Tidsfonten har sort
fyld og en 2,2 enheder bred grå kontur (#E0E0E0). Batteriikonet fyldes proportionalt efter batteriprocenten; fladen er lille.
Fra 0.2.1 er ikon og procent dæmpet til #A0A0A0, mens tidskonturen beholder #E0E0E0. Urets egen ambient-dæmpning kommer oveni farven.
Læselighed og den faktiske lysstyrke skal indstilles ud fra det fysiske ur.

Hele AOD-gruppen (også kolon, batteriikon og procent) forskydes ved minutskift.
Den gennemløber 25 positioner i et 5 × 5 gitter, fra −2 til +2 layoutenheder
på begge akser. En layoutenhed skaleres fra en 450 × 450 urskive til skærmen.
Der anvendes kun time/minut-datakilder, så bevægelsen ikke kræver sekundticks.
Systemets eventuelle ekstra forskydning kan forekomme oveni; indholdet har
luft til skærmkanten. Der er ikke slået nogen systembeskyttelse fra.

Automatiske kontroller gennemløber alle 1.440 klokkeslæt og 101 batteriniveauer.
Pixelestimatet bruger en tykkere 3-pixel-kontur og tæller alle lysende pixels,
uden at give rabat for grå farve eller systemets dæmpning. Det er et
konservativt fontbaseret estimat, ikke Samsungs officielle OPR-analyse eller
en måling af fysisk panelslid. Se valideringsrapporten for resultatet.

Pixel shifting, få lysende pixels og lav intensitet reducerer risikoen.
De giver ingen garanti mod OLED burn-in ved langvarig AOD-brug.

Primærkilder kontrolleret 11. september 2026:

- https://developer.android.com/training/wearables/wff/ambient
- https://developer.android.com/reference/wear-os/wff/group/part/text/decoration/outline
- https://developer.samsung.com/watch-face-studio/faq.html
- https://developer.samsung.com/watch-face-studio/user-guide/always-on.html

Samsung beskriver systemforskydning på nogle enheder og anbefaler højst 15 %
pixelbrug. Den konkrete Galaxy Watch9-adfærd er endnu ikke målt.
