# Layoutforslag 0.2.0-preview1

Layoutet blev installeret som 0.2.0-preview1. Den aktuelle version er 0.2.1,
hvor AOD-batteriets ikon og procent er dæmpet yderligere til #A0A0A0.
HTML og billeder dokumenterer den oprindelige før/efter-gennemgang.

Åbn `comparison.html` for en selvstændig før/efter-visning. Batteriskyderen
ændrer procent, bue og det nye ikon. `comparison.png` viser 78 %.

Visningen gengives fra WFF-XML, de bundtede fonte og de samme ikoner.
Den er et layoutpreview og simulerer ikke en bestemt skærms AOD-dæmpning.
`before.xml` fastholder layoutet fra den installerede 0.1.0.

| Ændring | Før | Forslag |
| --- | --- | --- |
| Batteriikon | Tom kontur | Proportionalt fyld, også i AOD |
| Nederste buer | Tomme spor | Skjult, indtil der er data |
| Skridt | 13 | 17 |
| Aktiv batteriprocent | 16 | 20 |
| Dato | 20 | 23 |
| Prognoseoverskrift | 15 | 18 |
| Prognosetemperatur | 20 | 26 |
| Prognosetekst | 14 | 18 |
| AOD-konturfarve | #808080 | #E0E0E0 |
| AOD-konturbredde | 1,4 | 2,2 |
| AOD batteriprocent | 17 | 20 |

Størrelser er WFF-layoutenheder, som skaleres til skærmen.
Pixel shifting og sort baggrund er bevaret.
Konservativt AOD-estimat: højst 4,638 % lysende pixels, inkl. et helt fyldt
32 × 20 batterifelt og en tykkere 3-pixel-kontur. Ikke en burn-in-garanti.

XML-validering, Android-build og lint består. Alle 10 funktionstests består.
Layoutet er afprøvet på det fysiske ur; brugeren har bekræftet bedre AOD-læselighed.

Reproducer preview: `python3 tools/layout_preview.py`.
Dækningsestimat: `aod-coverage-preview.json`. Build- og testlogs gemmes kun lokalt.
