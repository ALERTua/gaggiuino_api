[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)
[![Made in Ukraine](https://img.shields.io/badge/made_in-Ukraine-ffd700.svg?labelColor=0057b7)](https://stand-with-ukraine.pp.ua)
[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/badges/StandWithUkraine.svg)](https://stand-with-ukraine.pp.ua)
[![Russian Warship Go Fuck Yourself](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/badges/RussianWarship.svg)](https://stand-with-ukraine.pp.ua)

Gaggiuino REST API Wrapper for Python
---------------------------
- Repository: https://github.com/ALERTua/gaggiuino_api
- Changelog: https://github.com/ALERTua/gaggiuino_api/releases
- PyPi: https://pypi.org/project/gaggiuino_api/
- Home Assistant HACS Integration: https://github.com/ALERTua/hass-gaggiuino
- Gaggiuino REST API Documentation: https://github.com/GAGGIUINO/gaggiuino.github.io/tree/main/docs/rest-api

`gaggiuino_api` is an async Python client for the REST API of the firmware of a [Gaggiuino](https://gaggiuino.github.io/) espresso machine. It uses `aiohttp` and typed models.

The client covers the live status, the saved profiles, the shot history, the settings, the maintenance history, the firmware update and the health check. Each failure raises an exception. No method returns `None` for a failure.

## Requirements

- Python 3.14.2 or newer.
- A Gaggiuino machine on your network. The default address is `http://gaggiuino.local`.
- Firmware `c929939` or newer. Get it from the [release `main-c929939`](https://github.com/Zer0-bit/gaggiuino/releases/tag/main-c929939).

One version of this library supports one iteration of the REST API of the firmware. It does not support each firmware. Version 1.0 supports the iteration of firmware `c929939`. When the firmware author changes the REST API, a new version of the library follows. That version names the newer firmware and requires it. Pin an exact version of the library in an application that must keep working with one firmware. The Home Assistant integration [hass-gaggiuino](https://github.com/ALERTua/hass-gaggiuino) does this.

## Install

```bash
pip install gaggiuino_api
```

## Quick start

```python
import asyncio

from gaggiuino_api import GaggiuinoClient


async def main():
    async with GaggiuinoClient("http://gaggiuino.local") as machine:
        status = await machine.status()
        print(
            f"{status.profile_name}: {status.temperature:.1f} C, {status.pressure:.1f} bar"
        )


asyncio.run(main())
```

Output:

```text
Morning blend: 23.1 C, 0.1 bar
```

Use the client as an async context manager. You can also call `await machine.connect()` and `await machine.close()` yourself. The client keeps no state. Each call asks the machine.

## Examples

### Status

`status()` returns a `Status` with 46 fields. A few of them are `temperature`, `pressure`, `weight`, `operation_mode`, `brew_active`, `profile_id` and `profile_name`. See the `Status` class for the full list.

```python
status = await machine.status()
print(status.operation_mode, status.brew_active, status.weight)
```

Output:

```text
HOME False 0.0
```

### Profiles

```python
profiles = await machine.profiles.list()
for summary in profiles:
    print(summary.id, summary.name, summary.selected)

profile = await machine.profiles.get(profiles[0].id)
for phase in profile.phases:
    print(phase.type, phase.target)
```

Output:

```text
7 Morning blend False
12 Flush True
FLOW PhaseTarget(start=None, end=0.0, curve=<CurveType.LINEAR: 'LINEAR'>, time=None, volume=None)
```

`profiles.list()` returns `ProfileSummary` objects with `id`, `name` and `selected`. Only `profiles.get()` returns the phases. Each of these methods takes an id or a model that has an id:

```python
await machine.profiles.select(7)

created = await machine.profiles.create(profile)
print(created.id, created.name)

await machine.profiles.delete(created.id)
```

`profiles.create()` always saves a new profile with a new id and does not select it.

Warning about the delete: firmware `c929939` answers HTTP 200 to a delete of an id that it does not have. In a test, such a request removed another saved profile. So `profiles.delete()` reads the list of the profiles first. For an id that the list does not have, it raises `GaggiuinoNotFoundError` and sends no delete request. A `profiles.select()` of a missing profile raises `GaggiuinoResponseError` with status 500, because the machine does not answer 404 there.

### Shots

```python
latest_id = await machine.shots.latest_id()
shot = await machine.shots.get(latest_id)
print(shot.id, shot.duration / 10, "s", shot.profile.name)
print(max(shot.datapoints.pressure) / 10, "bar at peak")
```

Output:

```text
580 74.1 s Morning blend
9.3 bar at peak
```

The `duration` and each datapoint value are integers scaled by 10. To delete the data of a shot, call `await machine.shots.delete(latest_id)`. This cannot be undone.

### Settings

```python
settings = await machine.settings.get()
print(settings.display.lcd_brightness)

boiler = await machine.settings.boiler.get()
print(boiler.steam_set_point)

versions = await machine.settings.versions()
print(versions.core_version)
```

Output:

```text
61
125
c929939
```

The groups are `boiler`, `system`, `led`, `scales`, `display` and `theme`. Each group has `get()`, `update()` and `update_from()`:

```python
await machine.settings.boiler.update(steam_set_point=130)

boiler = await machine.settings.boiler.get()
await machine.settings.boiler.update_from(boiler)
```

An update reads the whole group from the machine, changes only the fields that you name, and sends the whole group back. Keys that the library does not know stay as they are. A name that the group model does not have raises `TypeError` before any request. The group `webUi` is read-only inside `settings.get()`. See [UNSUPPORTED.md](UNSUPPORTED.md).

### Maintenance

```python
maintenance = await machine.maintenance()
print(maintenance.shots_since_descale, maintenance.shots_since_backflush)
```

Output:

```text
11 11
```

### Firmware

```python
progress = await machine.firmware.progress()
print(progress.status, progress.type, progress.progress)
```

Output:

```text
IDLE C_FW 0
```

`await machine.firmware.update()` starts an update of the firmware and returns at once. It sends no body. The machine restarts during the update. The call starts a real update, so use it with care.

### Health

```python
print(await machine.healthy())
```

Output:

```text
True
```

`healthy()` raises `GaggiuinoConnectionError` or `GaggiuinoConnectionTimeoutError` when the machine does not answer. Catch these two errors to poll a machine through a restart.

### Errors

`GaggiuinoError` is the base class of each error that the library raises.

| Exception | When |
|---|---|
| `GaggiuinoConnectionError` | The connection to the machine failed. |
| `GaggiuinoConnectionTimeoutError` | The machine did not answer in time. |
| `GaggiuinoResponseError` | The machine answered with an HTTP error status. It has `status` and `body`. |
| `GaggiuinoNotFoundError` | A subclass of `GaggiuinoResponseError` for HTTP 404. |
| `GaggiuinoCommandError` | The machine answered with `"success": false`. |
| `GaggiuinoResponseFormatError` | The answer does not have the expected format. |

```python
from gaggiuino_api import (
    GaggiuinoClient,
    GaggiuinoConnectionError,
    GaggiuinoNotFoundError,
    GaggiuinoResponseError,
)

try:
    async with GaggiuinoClient("http://gaggiuino.local") as machine:
        await machine.shots.get(999999)
except GaggiuinoNotFoundError as err:
    print("No such shot:", err.status)
except GaggiuinoResponseError as err:
    print("The machine answered", err.status)
except GaggiuinoConnectionError:
    print("The machine is not reachable")
```

Output:

```text
No such shot: 404
```

### Shared session and timeout

Give your own `aiohttp` session to share it with the rest of your application. The client does not close a session that you give. The `timeout` is in seconds, or an `aiohttp.ClientTimeout`. The default is 5 seconds.

```python
import aiohttp

async with aiohttp.ClientSession() as session:
    machine = GaggiuinoClient("http://gaggiuino.local", session=session, timeout=10)
    print(await machine.healthy())
    print((await machine.status()).core_version)
```

Output:

```text
True
c929939
```

## More documents

- [MIGRATION.md](MIGRATION.md) lists each name that changed since version 0.x.
- [UNSUPPORTED.md](UNSUPPORTED.md) lists the features that the library leaves out on purpose.
- [docs/firmware-undocumented-fields.md](docs/firmware-undocumented-fields.md) lists the keys that the firmware sends and the upstream documentation does not describe.
- [docs/firmware-ambiguous-fields.md](docs/firmware-ambiguous-fields.md) lists the keys with an unclear meaning and the differences between the documentation and the machine.

## Tests

Run the unit tests:

```bash
uv run pytest test
```

The end-to-end tests need a real machine. They are deselected by default. Set `GAGGIUINO_BASE_URL` if the machine is not at `http://gaggiuino.local`.

```bash
uv run pytest -m e2e test/e2e
```

These tests write only the `led` and `display` settings groups. They delete only the profile copy that they created. They never send a delete for an id that the machine does not have. They never call `firmware.update()` and never delete a shot.
