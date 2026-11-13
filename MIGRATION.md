# Migration from 0.x to 1.0

Version 1.0 renames the client, its methods, the models and some exceptions. It also changes how errors and field names work. This page lists each change. Version 1.0 needs Python 3.14.2 or newer and firmware `c929939` or newer.

## Names

| 0.x | 1.0 |
|---|---|
| `GaggiuinoAPI` | `GaggiuinoClient` |
| `gaggiuino_api.api.GaggiuinoClient`, the HTTP base class of 0.x, which the package did not export | Removed. The `GaggiuinoClient` of 1.0 is the old `GaggiuinoAPI`. |
| `GaggiuinoAPI.disconnect()` | `GaggiuinoClient.close()` |
| `GaggiuinoAPI.profile` (property) | Removed. Use `status.profile_id` and `status.profile_name`. |
| `get()`, `post()`, `delete()` of the client | Removed. |
| `get_status()` | `status()` |
| `get_profiles()` | `profiles.list()`, returns `list[ProfileSummary]` |
| `get_profile(id)` | `profiles.get(id)`, returns `Profile` |
| `select_profile(x)` | `profiles.select(x)` |
| `delete_profile(x)` | `profiles.delete(x)` |
| (none) | `profiles.create(profile)`, returns `ProfileCreated` with `id` and `name` |
| `get_shot(id)` | `shots.get(id)` |
| `get_latest_shot_id()`, returned `GaggiuinoLatestShotResult` | `shots.latest_id()`, returns `int` |
| `delete_shot(x)` | `shots.delete(x)` |
| `get_maintenance()` | `maintenance()` |
| `update_firmware(version)` | `firmware.update()`. It has no argument and sends no request body. |
| `get_firmware_progress()`, returned a `dict` | `firmware.progress()`, returns `FirmwareProgress` |
| `get_health()` | Removed. Use `healthy()`. |
| `healthy()` | `healthy()`. A connection error now raises. |
| `get_settings()` | `settings.get()` |
| `get_<group>_settings()` | `settings.<group>.get()` |
| `update_<group>_settings(...)` | `settings.<group>.update(**changes)` or `settings.<group>.update_from(model)` |
| `get_versions()` | `settings.versions()` |

The `<group>` is one of `boiler`, `system`, `led`, `scales`, `display` and `theme`.

### Models

Each model class loses the `Gaggiuino` prefix.

| 0.x | 1.0 |
|---|---|
| `GaggiuinoStatus` | `Status` |
| `GaggiuinoProfile` | `Profile` for a full profile, `ProfileSummary` for an entry of the list |
| `GaggiuinoProfilePhase` | `Phase` |
| `GaggiuinoProfilePhaseTarget` | `PhaseTarget` |
| `GaggiuinoProfilePhaseStopCondition` | `PhaseStopConditions` |
| `GaggiuinoProfileType` | Removed. Use the enum `PhaseType`. |
| `GaggiuinoShot` | `Shot` |
| `GaggiuinoShotDataPoints` | `ShotDatapoints` |
| `GaggiuinoLatestShotResult` | `LatestShot` |
| `GaggiuinoMaintenance` | `Maintenance` |
| `GaggiuinoSettings` | `Settings` |
| `Gaggiuino<Group>Settings` | `<Group>Settings`, for example `GaggiuinoBoilerSettings` becomes `BoilerSettings` |
| `GaggiuinoLedColor` | `LedColor` |
| `GaggiuinoTofSettings` | `TofSettings` |
| `GaggiuinoVersions` | `Versions` |

New models are `FirmwareProgress`, `GlobalStopConditions`, `Health`, `ProfileCreated`, `Recipe` and `WebUiSettings`.

### Exceptions

| 0.x | 1.0 |
|---|---|
| `GaggiuinoEndpointNotFoundError` | `GaggiuinoNotFoundError`. It is now a subclass of `GaggiuinoResponseError`. |
| (none) | `GaggiuinoCommandError`, for an answer with `"success": false` |
| (none) | `GaggiuinoResponseFormatError`, for an answer in an unexpected format |
| `GaggiuinoError`, `GaggiuinoConnectionError`, `GaggiuinoConnectionTimeoutError`, `GaggiuinoResponseError` | Same names. |

### Enums

Version 1.0 adds the enums `OperationMode`, `PhaseType`, `CurveType`, `ReleaseChannel`, `FirmwareStatus` and `FirmwareType`. A field that the library only reads gets `UNKNOWN` for a value that the library does not know. A field that goes back to the machine keeps an unknown value as the raw value.

## Fields

Each field is now snake_case. The firmware name is kept as an alias, so the library still reads and writes the firmware name. The rule is `upTime` becomes `up_time`, `profileId` becomes `profile_id` and `R` becomes `r`.

Other changes:

- `from_dict()` becomes `Model.from_api()`.
- `to_api_dict()` becomes `to_api()`.

A field of one word does not change. The table lists each 0.x field whose name changes.

| Model | Changes |
|---|---|
| `Status` | `upTime` → `up_time`, `profileId` → `profile_id`, `profileName` → `profile_name`, `targetTemperature` → `target_temperature`, `waterLevel` → `water_level`, `brewSwitchState` → `brew_switch_state`, `steamSwitchState` → `steam_switch_state` |
| `Profile` | `globalStopConditions` → `global_stop_conditions`, `waterTemperature` → `water_temperature` |
| `Phase` | `stopConditions` → `stop_conditions` |
| `PhaseStopConditions` | `pressureAbove` → `pressure_above` |
| `ShotDatapoints` | `pumpFlow` → `pump_flow`, `shotWeight` → `shot_weight`, `targetPressure` → `target_pressure`, `targetPumpFlow` → `target_pump_flow`, `targetTemperature` → `target_temperature`, `timeInShot` → `time_in_shot`, `waterPumped` → `water_pumped`, `weightFlow` → `weight_flow` |
| `LatestShot` | `lastShotId` → `last_shot_id` |
| `BoilerSettings` | `steamSetPoint` → `steam_set_point`, `offsetTemp` → `offset_temp`, `mainDivider` → `main_divider`, `brewDivider` → `brew_divider`, `brewDeltaState` → `brew_delta_state`, `dreamSteamState` → `dream_steam_state`, `startupHeatDelta` → `startup_heat_delta` |
| `SystemSettings` | `pumpFlowAtZero` → `pump_flow_at_zero`, `timezoneOffsetMinutes` → `timezone_offset_minutes`, `sprofilerToken` → `sprofiler_token`, `visualizerToken` → `visualizer_token`, `servicesState` → `services_state`, `wifiEnabled` → `wifi_enabled`, `releaseChannel` → `release_channel`, `momentarySwitches` → `momentary_switches`, `ungroupHomeTiles` → `ungroup_home_tiles`, `alternativeFlush` → `alternative_flush`, `mqttEnabled` → `mqtt_enabled`, `mqttHost` → `mqtt_host`, `mqttPort` → `mqtt_port`, `mqttUsername` → `mqtt_username`, `mqttPassword` → `mqtt_password`, `mqttTopicPrefix` → `mqtt_topic_prefix` |
| `LedColor` | `R` → `r`, `G` → `g`, `B` → `b` |
| `ScalesSettings` | `forcePredictive` → `force_predictive`, `hwScalesEnabled` → `hw_scales_enabled`, `hwScalesF1` → `hw_scales_f1`, `hwScalesF2` → `hw_scales_f2`, `btScalesEnabled` → `bt_scales_enabled`, `btScalesAutoConnect` → `bt_scales_auto_connect`, `btScalesPinnedMac` → `bt_scales_pinned_mac` |
| `DisplaySettings` | `lcdBrightness` → `lcd_brightness`, `lcdDarkMode` → `lcd_dark_mode`, `lcdSleep` → `lcd_sleep`, `lcdGoHome` → `lcd_go_home`, `lcdCloseOnBrewOff` → `lcd_close_on_brew_off`, `simpleUI` → `simple_ui` |
| `ThemeSettings` | `colourPrimary` → `colour_primary`, `colourSecondary` → `colour_secondary` |
| `Versions` | `coreVersion` → `core_version`, `frontVersion` → `front_version`, `staticVersion` → `static_version` |
| `Maintenance` | `lastDescaleTimestamp` → `last_descale_timestamp`, `shotsSinceDescale` → `shots_since_descale`, `lastBackflushTimestamp` → `last_backflush_timestamp`, `shotsSinceBackflush` → `shots_since_backflush` |

The field `selected` of a profile moved to `ProfileSummary`. A `Profile` has no `selected` field.

## Behavior changes

- A method raises an exception where 0.x returned `None` or `False`. No method returns `None` for a failure.
- `selected` of a profile is a real `bool`. Version 0.x kept the string `"false"`, which is true in a condition.
- The client caches no state.
- Importing the package has no side effect. The change of the Windows event loop policy is gone.
- The package needs Python 3.14.2 or newer.
- A settings update reads the whole group, changes the named fields and sends the whole group back.
- `profiles.delete()` raises `GaggiuinoNotFoundError` without a delete request for an id that the list of the machine does not have. See the README for the reason.
- `profiles.select()` and `profiles.delete()` raise `TypeError` for a `bool`, because a `bool` is not an id.
- `GaggiuinoCommandError` has the attribute `status`, the HTTP status of the answer.
- A settings `update()` takes a model, not a `dict`, for a nested field. For example, `led.update(color=LedColor(r=255, g=0, b=0))`. A `dict` raises `TypeError`.
