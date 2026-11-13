# gaggiuino_api memory index

The index that follows comes from `.claude/memory/MEMORY.md`, and each link is relative to that folder. The repository is public, so this memory holds no personal data and no value of one computer.

- Each change goes into `main` through a pull request from its own branch. Only a commit of the type `chore` goes directly into `main`.
- A version of the library supports one iteration of the REST API of the firmware, not each firmware. The README names the minimum firmware of that iteration and gives the link to its release. A model does not make a field optional for an older firmware. When the author of the firmware changes the REST API, a new version of the library follows the change, names the newer firmware and requires it.
- The test machine answers at `http://gaggiuino.local/`. Before work that needs it, make sure that it answers: `curl -sS -m 8 http://gaggiuino.local/api/health`. If it does not answer, stop and ask the user to turn it on. The end-to-end tests use this address by default, through `DEFAULT_BASE_URL` in `src/gaggiuino_api/const.py`.
- The main user of the library is the Home Assistant integration `ALERTua/hass-gaggiuino`, of the same owner. Its `custom_components/gaggiuino/manifest.json` pins an exact version, for example `gaggiuino_api==0.1.14`. So a release of the library gets to Home Assistant users only after a change of that pin. Before a change of a public name or type, search that repository for each use.
- The plan of a piece of work lives in `plans/<topic>/`, for example `plans/status-schema/`. git ignores `plans/`.
- [Python version](python-version.md) — `requires-python` follows the newest Home Assistant Core release. The CI matrix, the minimum Home Assistant of hass-gaggiuino
- [Upstream API documentation](upstream-api.md) — the source of the API documentation, the fields of an endpoint, a field of a newer firmware, the WebSocket and MQTT documents
