# Ambiguous fields and differences from the documentation

These keys come in the answers of firmware `c929939`, and their meaning is not clear. This page also lists the places where the upstream REST documentation and the machine differ. The questions are for the firmware author. The firmware source is not public, so the answers of the machine are the only source.

## Keys in a model as a raw value

The `Status` model keeps these two keys as they come. Its docstring says that the meaning is not documented.

| Endpoint | Key | Open question |
|---|---|---|
| `GET /api/system/status` | `readinessState` | What does each value mean? Seen: `1` during the warmup and `3` after it. |
| `GET /api/system/status` | `brewSwitchActive` | How does it differ from `brewSwitchState` and from `brewActive`? |

## Keys that no model has

A settings update still sends each of these keys back unchanged, because it sends the whole group that it read from the machine.

| Endpoint | Keys | Open question |
|---|---|---|
| `GET /api/settings/boiler` | `dualBoilerStagger` | What does the stagger do? |
| `GET /api/settings/system` | `pumpSpecValid`, `pumpSpec` (16 integers) | What are the meaning and the unit of each element? |
| `GET /api/settings/display` | `homeTileLeftTop`, `homeTileLeftBottom`, `homeTileRightTop`, `homeTileLeftTopGroup`, `homeTileLeftBottomGroup`, `homeTileRightTopGroup`, `homeLayout` | What are the values of each tile, and what is the format of the layout? |
| `GET /api/settings` | `webUi.configured`, `webUi.themeId`, `webUi.dashboardLayout`, `webUi.dashboardFontSize` | They hold the state of the web interface. Are they a part of the public API? |
| `GET /api/settings` | The group `webUi` as a whole | `GET /api/settings/webUi` answers 404. Does a POST exist? |
| `GET /api/firmware/progress` | The object `migration` with 20 keys | Is it a part of the public API? |

## Differences between the documentation and the machine

- `display.simpleUI` is in the documentation, and the machine does not send it. The machine sends `modernUI`.
- The documentation shows string booleans, for example `"brewDeltaState": "true"`. The machine sends JSON booleans in each settings group. `GET /api/profiles/all` sends `selected` as a string.
- The documentation names only the 5 energy keys of the status. The status has 46 keys, and the 10 older keys are strings.
- The documentation gives no response shape for `GET /api/system/status` (a list with one object), `GET /api/profiles/all`, `GET /api/shots/latest` (a list with one object) and `GET /api/shots/<id>`.
- The documentation does not name the body of `POST /api/shots` and of `POST /api/firmware/update-all`. Version 0.x of the library sent `{"version": "latest"}` to the second one. Version 1.0 sends no body.
- The documentation does not give the HTTP status of `{"success": false}`.
- A missing shot or profile returns 404 with `text/plain`. The documentation does not name this.
- The WebSocket document has the phase type `MANUAL`, and the REST documentation shows only `PRESSURE`. The REST documentation gives no list of the values of `type` and `curve`.
- `operationMode` has 8 values in the MQTT document and 10 in the WebSocket document (`PUMP_CALIBRATION` and `POWER_OFF` are the two more). Which values can the REST status return?
- The unit of `duration` of a shot is not documented. A value of 741 belongs to a shot of about 74 seconds, so the unit is tenths of a second by measurement.

## Measured on firmware `c929939`

- A `DELETE /api/profile-select/<id>` of an id that does not exist answers 200 `OK`. In a test, it removed another saved profile. So `profiles.delete()` checks the list of the profiles first.
- A select of a missing profile answers 500, not 404.
- `POST /api/profile` accepts `3.0` for `3`. It does not select the new profile.
- A settings POST answers `{"success": true}`.
