# WFF schema validator

`wff-validator.jar` is a local build of the official Google/Samsung validator.
Source: https://github.com/google/watchface
Pinned commit: `b6cdda0acd3e4c5d0be5624fcdc01209380029d1`
SHA-256: `2946eba94b84247a868f84a58aaa7efeaa1d68dd3b9d0bc904a1fc6b745bcf75`

Built from `third_party/wff/specification/validator` using Java 17 and Gradle
8.14.3, with its documented Maven Central dependencies. The upstream root
buildscript was reduced to Maven Central repositories to avoid loading an
unneeded Android plugin; the validator Java sources and schemas are unchanged.
Upstream license: `licenses/WFF-validator.txt`; dependency notices remain in JAR.

Rebuild:

```sh
git clone https://github.com/google/watchface.git
git -C watchface checkout b6cdda0acd3e4c5d0be5624fcdc01209380029d1
cd watchface/third_party/wff
./gradlew :specification:validator:executable-jar
```

The result is `specification/validator/build/libs/wff-validator.jar`.
The byte hash may differ between builds (timestamps and Gradle version).

The schema validator does not fully validate expression function support.
`test_watchface.py` and the actual Wear OS renderer checks cover that gap.
