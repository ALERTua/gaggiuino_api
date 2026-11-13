# Unsupported features

The library leaves out these features on purpose.

| Feature | Reason |
|---|---|
| `POST /api/shots` | The upstream documentation does not name its body, so the library cannot build a request that the machine is sure to accept. |
| The WebSocket API | It needs the `.proto` files of the firmware source. The firmware source is not public. |
| MQTT | It is a connection from the machine to a broker, with its own Home Assistant discovery. It is not a client API. |
| Writes to the `webUi` settings group | `GET /api/settings/webUi` answers 404, so the group has no endpoint of its own. It is read-only inside `settings.get()`. |
| A test of `firmware.update()` against a real machine | The method exists and sends no body. The end-to-end tests do not call it, because the call starts a real update. |

The upstream API documentation is in the folder [docs/rest-api](https://github.com/GAGGIUINO/gaggiuino.github.io/tree/main/docs/rest-api) of the repository `GAGGIUINO/gaggiuino.github.io`.
