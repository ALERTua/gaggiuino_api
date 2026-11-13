# Test fixtures

These JSON files are responses of a real Gaggiuino machine. Each file is the body of one GET request of the REST API. No other kind of request was sent.

- Firmware of the capture: core version `c929939` (the `coreVersion` field of `settings_versions.json`).
- The private values are replaced by neutral values, under these keys at any depth: `machineName`, `sprofilerToken`, `visualizerToken`, `mqttHost`, `mqttUsername`, `mqttPassword` and `btScalesPinnedMac`. A value keeps its JSON type.
- `shot.json` keeps only the first 20 samples of each array of `datapoints`. All arrays have the same length.
- No other value is changed. A number that the machine sent as a string is still a string.
- `profile.json` is the profile with the most phases. If several profiles have the same count, it is the one with the lowest id.

Load a file in a test with `load_fixture("<name>")` from `test/fixture_loader.py`.
