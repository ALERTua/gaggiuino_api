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
- Gaggiuino REST API Documentation: https://gaggiuino.github.io/rest-api/rest-api.md

The [Gaggiuino REST API](https://gaggiuino.github.io/#/rest-api/rest-api) Wrapper is a Python library that provides a simple and efficient way to interact with [Gaggiuino-enabled](https://gaggiuino.github.io/) espresso machines.
This asynchronous client allows users to manage coffee profiles, retrieve shot data, and control their Gaggiuino-modified espresso machines through a REST API interface.

The library covers profiles (list, select, export, delete), shot history (retrieve, delete), live system status,
all machine settings (boiler, system, LED, scales, display, theme — read and update), maintenance history,
firmware updates, and health checks — with built-in error handling and connection management.
It leverages modern Python features and async/await patterns to provide non-blocking operations, making it suitable for integration into larger applications or automation systems.

## Usage Instructions
### Prerequisites
- Python 3.11 or higher
- A running Gaggiuino-enabled espresso machine
- Network access to the Gaggiuino device (default: http://gaggiuino.local:80)

### Installation
```bash
pip install gaggiuino_api
```

### Quick Start

```python
import asyncio
from gaggiuino_api import GaggiuinoAPI


async def main():
    async with GaggiuinoAPI() as client:
        # Get the status
        status = await client.get_status()
        print(f"Status: {status}")

        # Get all available profiles
        profiles = await client.get_profiles()

        # Select a profile by ID
        await client.select_profile(profiles[0])

        # Get shot data
        shot = await client.get_shot(1)
        print(f"Shot duration: {shot.duration}ms")


if __name__ == "__main__":
    asyncio.run(main())
```

### More Detailed Examples
#### Working with Profiles

```python
from gaggiuino_api import GaggiuinoAPI


async def profile_management():
    async with GaggiuinoAPI(base_url="http://custom.gaggiuino.local") as client:
        # Get all profiles
        profiles = await client.get_profiles()

        # Print profile details
        for profile in profiles:
            print(f"Profile: {profile.name} (ID: {profile.id})")
            print(f"Water Temperature: {profile.waterTemperature}°C")

            # Print phases
            for phase in profile.phases:
                print(f"Phase Type: {phase.type}")
                print(f"Restriction: {phase.restriction}")
```

#### Retrieving Shot Data

```python
from gaggiuino_api import GaggiuinoAPI


async def analyze_shot():
    async with GaggiuinoAPI() as client:
        latest_shot_id_result = await client.get_latest_shot_id()
        latest_shot_id = latest_shot_id_result.lastShotId
        shot = await client.get_shot(latest_shot_id)

        # Access shot metrics
        print(f"Latest Shot ID: {latest_shot_id}")
        print(f"Duration: {shot.duration}ms")
        print(f"Timestamp: {shot.timestamp}")

        # Access datapoints
        pressure_points = shot.datapoints.pressure
        flow_points = shot.datapoints.pumpFlow
        temperature_points = shot.datapoints.temperature
```

#### Machine Settings

```python
from dataclasses import replace

from gaggiuino_api import GaggiuinoAPI


async def tune_boiler():
    async with GaggiuinoAPI() as client:
        # All settings at once...
        settings = await client.get_settings()
        print(f"LCD brightness: {settings.display.lcdBrightness}")

        # ...or per category, with a read-modify-update roundtrip
        boiler = await client.get_boiler_settings()
        await client.update_boiler_settings(replace(boiler, steamSetPoint=150))
```

#### Maintenance History

```python
from gaggiuino_api import GaggiuinoAPI


async def service_status():
    async with GaggiuinoAPI() as client:
        maintenance = await client.get_maintenance()
        print(f"Shots since descale: {maintenance.shotsSinceDescale}")
        print(f"Shots since backflush: {maintenance.shotsSinceBackflush}")
```

### Intentionally Skipped Endpoints

The wrapper covers all endpoints of the [official REST API documentation](https://gaggiuino.github.io/rest-api/rest-api.md) except these, skipped on purpose:

| Endpoint | Reason |
|---|---|
| `POST /api/shots` | Machine-internal: the firmware itself streams shot data to storage during extraction. The body format is undocumented, and writing shots from a client risks corrupting the shot history. |
| `POST /api/profile` | Profile import (REST equivalent of the web UI's Import button). Skipped for now; may be added on demand — open an issue if you need it. |

### Troubleshooting
#### Connection Issues
- Problem: Unable to connect to Gaggiuino device
  ```python
  from gaggiuino_api import GaggiuinoAPI, GaggiuinoConnectionError


  async def main():
      try:
          async with GaggiuinoAPI() as client:
              profiles = await client.get_profiles()
      except GaggiuinoConnectionError:
          print("Check if Gaggiuino is powered on and connected to network")
          print("Verify the device is accessible at gaggiuino.local")
  ```

#### Endpoint Not Found
- Problem: API endpoint returns 404
  ```python
  from gaggiuino_api import GaggiuinoAPI, GaggiuinoEndpointNotFoundError


  async def main():
      try:
          async with GaggiuinoAPI() as client:
              shot = await client.get_shot(999)
      except GaggiuinoEndpointNotFoundError:
          print("Shot ID not found - verify the shot exists")
  ```

## Data Flow
The Gaggiuino API wrapper manages communication between your Python application and the Gaggiuino-enabled espresso machine through HTTP requests.

```ascii
[Python App] <-> [GaggiuinoAPI] <-> [HTTP/REST] <-> [Gaggiuino Device]
     |              |                                      |
     |              |                                      |
     +--- Profiles  +---- HTTP Requests ------------------- Machine Control
     |              |                                      |
     +--- Shot Data +---- Response Parsing --------------- Sensor Data
```

Key component interactions:
- GaggiuinoAPI class handles all HTTP communication using aiohttp
- Async context manager ensures proper connection handling and resource cleanup
- JSON responses are automatically parsed into typed data models
- Error handling provides specific exceptions for common failure modes
- Connection management includes automatic session creation and cleanup
- All API operations are asynchronous for non-blocking operation


I have no idea what this readme is about. It's all ChatGPT.
