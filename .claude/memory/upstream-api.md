---
name: upstream-api
description: "Read this file before you read the upstream API documentation, add a field or an endpoint, or compare a model with a response of the firmware."
metadata:
  type: reference
---

- The source of the API documentation is the folder `docs/rest-api` of the public repository `GAGGIUINO/gaggiuino.github.io`: https://github.com/GAGGIUINO/gaggiuino.github.io/tree/main/docs/rest-api. It holds three files: `rest-api.md`, `websocket.md` and `MQTT.md`.
- Get the raw Markdown of a file with `gh api -H "Accept: application/vnd.github.raw" repos/GAGGIUINO/gaggiuino.github.io/contents/docs/rest-api/<file>`. The site https://gaggiuino.github.io loads its text through JavaScript, so a fetch of a page gives no text.
- To see the latest changes of the documentation, run `gh api "repos/GAGGIUINO/gaggiuino.github.io/commits?path=docs/rest-api&per_page=5"`.
- The firmware source is not public. The documentation repository is the only public repository of the `GAGGIUINO` account. So the response of the test machine is the final source for a field that the documentation does not describe.
- `rest-api.md` does not list all fields of a response. For example, it names only the energy fields of `GET /api/system/status`. The other fields of that response have the same names as the payloads of the MQTT topics `<prefix>/sensors` and `<prefix>/system` in `MQTT.md`. `websocket.md` gives the same data as protobuf messages, for example `SystemStateDto`, and some of its names are different.
- Some fields of a response have no documentation, for example `readinessState`, `warmupElapsedSeconds` and `warmupRemainingSeconds` of the status. Do not guess the meaning of each value of such a field. Keep the raw value, and write the observed values in the docstring.
- `GET /api/profiles/all` gives only `id`, `name` and `selected` of each profile. The phases, the recipe and the stop conditions come only from `GET /api/profile/<id>`, and that response has no `id`.
- `GET /api/system/status` returns a list with one object. The firmware gives the older fields of that object as strings, for example `"upTime": "150"` and `"temperature": "88.839622"`. The newer fields come as JSON numbers and booleans. A float field can come as a JSON integer, for example `"pumpFlow": 0`, so convert each number with `float()` or `int()`.
