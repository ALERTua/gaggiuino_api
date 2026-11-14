# Undocumented fields that the library supports

These keys come in the answers of firmware `c929939`. The upstream REST documentation does not describe them. Their meaning is clear, so the library supports them. Each key has a field in a model.

Such a field is optional in its model (its type ends with `| None`), unless the table says that it is required. A model leaves out an optional field when its value is `None`, so a write never sends a key that the machine did not send.

The upstream documentation is in the folder [docs/rest-api](https://github.com/GAGGIUINO/gaggiuino.github.io/tree/main/docs/rest-api) of the repository `GAGGIUINO/gaggiuino.github.io`.

| Endpoint | Key | Model field | Why the meaning is clear |
|---|---|---|---|
| `GET /api/system/status` | `upTime` | `Status.up_time` (required) | Version 0.x of the library had it. The name tells the meaning. |
| `GET /api/system/status` | `profileId` | `Status.profile_id` (required) | The same as above. |
| `GET /api/system/status` | `profileName` | `Status.profile_name` (required) | The same as above. |
| `GET /api/system/status` | `brewSwitchState` | `Status.brew_switch_state` (required) | The same as above. |
| `GET /api/system/status` | `steamSwitchState` | `Status.steam_switch_state` (required) | The same as above. |
| `GET /api/system/status` | `boilerTemperature` | `Status.boiler_temperature` | It has the same value as `temperature`, as a number. |
| `GET /api/system/status` | `steamForgottenOn` | `Status.steam_forgotten_on` | The WebSocket document describes `isSteamForgottenON` in `SystemStateDto`. |
| `GET /api/system/status` | `pcbV2` | `Status.pcb_v2` | The WebSocket document describes `pcbV2` in `SystemStateDto`. |
| `GET /api/system/status` | `debugLoggingEnabled` | `Status.debug_logging_enabled` | The WebSocket document describes `debugLoggingEnabled` in `SystemStateDto`. |
| `GET /api/system/status` | `warmupElapsedSeconds` | `Status.warmup_elapsed_seconds` | The name gives the meaning and the unit. |
| `GET /api/system/status` | `warmupRemainingSeconds` | `Status.warmup_remaining_seconds` | The name gives the meaning and the unit. |
| `GET /api/profiles/all` | `selected` | `ProfileSummary.selected` (required) | It marks the selected profile. The machine sends the string `"true"` or `"false"`, and the library gives a `bool`. |
| `GET /api/shots/latest` | `lastShotId` | `LatestShot.last_shot_id` (required) | Version 0.x of the library had it. |
| `GET /api/shots/<id>` | `id`, `timestamp`, `duration`, `profile` | `Shot.id`, `Shot.timestamp`, `Shot.duration`, `Shot.profile` (required) | Version 0.x of the library had them. |
| `GET /api/shots/<id>` | `datapoints.*` (10 arrays) | `ShotDatapoints.*` (required) | Version 0.x of the library had them. The WebSocket document gives the datapoints as integers scaled by 10. |
| `GET /api/shots/<id>` | `datapoints.phaseIndex` | `ShotDatapoints.phase_index` | It is the index of the profile phase of each sample. |
| `GET /api/settings/boiler` | `dualBoilerEnabled` | `BoilerSettings.dual_boiler_enabled` | It is a switch of the dual boiler mode. |
| `GET /api/settings/system` | `machineName` | `SystemSettings.machine_name` | It is the same name as in the status and in the MQTT document. |
| `GET /api/settings/system` | `minShotDurationSeconds` | `SystemSettings.min_shot_duration_seconds` | The name gives the meaning and the unit. |
| `GET /api/settings/system` | `autoFlushDurationSeconds` | `SystemSettings.auto_flush_duration_seconds` | The name gives the meaning and the unit. |
| `GET /api/settings/display` | `modernUI` | `DisplaySettings.modern_ui` | It is a switch of the style of the user interface. |
| `GET /api/settings` | `webUi.brewHeaterWatts` | `WebUiSettings.brew_heater_watts` | It is the rated power of the brew heater. It is an input of the energy monitor. |
| `GET /api/settings` | `webUi.steamHeaterWatts` | `WebUiSettings.steam_heater_watts` | It is the rated power of the steam heater. |
| `GET /api/settings` | `webUi.pumpWatts` | `WebUiSettings.pump_watts` | It is the rated power of the pump. |
| `GET /api/settings` | `webUi.idleWatts` | `WebUiSettings.idle_watts` | It is the power of the idle machine. |
| `GET /api/profile/<id>` | The optional keys of a phase, a target, the stop conditions and the recipe that the WebSocket document gives in `ProfileDto` | The optional fields of `Phase`, `PhaseTarget`, `PhaseStopConditions`, `GlobalStopConditions` and `Recipe` | The firmware leaves out a key that has a zero value, so these fields are optional. |

Each key that is not in this table is described in the REST documentation, or it has the same name and meaning in the MQTT document. Such a key is a required field. The keys of [firmware-ambiguous-fields.md](firmware-ambiguous-fields.md) are the exception: their meaning is not clear.
