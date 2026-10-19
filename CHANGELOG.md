# Changelog

All notable changes to this project are documented here.

## [1.0.1] - 2026-10-19

### Added
- Official vector Howest brand assets for integration icon and logo.

### Changed
- Clarified community/unofficial status in documentation.
- Integrated `howest-resto` v1.0.0+ from official PyPI release.

## [1.0.0] - 2026-10-19

### Added
- Initial release of the Howest Resto Home Assistant integration.
- Full support for all 6 Howest student restaurant campuses (Kortrijk: 't Obeetje, Plaza, The Square; Brugge: YUM, DAD, BSI).
- Config Flow with campus picker and validation.
- Options Flow with configurable update intervals and language preferences (Dutch, English, Both).
- Today's Menu sensor, Tomorrow's Menu sensor, and Weekly Menu sensor with detailed attributes.
- Native Calendar platform exposing daily lunches as all-day calendar events.
- Zero external dependencies using typed `howest-resto` Python library.
