[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)
[![Made in Ukraine](https://img.shields.io/badge/made_in-Ukraine-ffd700.svg?labelColor=0057b7)](https://stand-with-ukraine.pp.ua)
[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/badges/StandWithUkraine.svg)](https://stand-with-ukraine.pp.ua)
[![Russian Warship Go Fuck Yourself](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/badges/RussianWarship.svg)](https://stand-with-ukraine.pp.ua)

Gaggiuino REST API Wrapper for Python
---------------------------
Repository: https://github.com/ALERTua/gaggiuino_api
PyPi: https://pypi.org/project/gaggiuino_api/

The Gaggiuino REST API Wrapper is a Python library that provides a simple and efficient way to interact with [Gaggiuino-enabled](https://gaggiuino.github.io/) espresso machines.
This asynchronous client allows users to manage coffee profiles, retrieve shot data, and control their Gaggiuino-modified espresso machines through a REST API interface.

The library offers comprehensive profile management capabilities, including retrieving and selecting brewing profiles,
accessing historical shot data, and handling machine communication with built-in error handling and connection management.
It leverages modern Python features and async/await patterns to provide non-blocking operations, making it suitable for integration into larger applications or automation systems.

## Usage Instructions
### Prerequisites
- Python 3.13 or higher
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
        print(f"Phase Type: {phase.type.type}")
        print(f"Restriction: {phase.restriction}")
```

#### Retrieving Shot Data

```python
from gaggiuino_api import GaggiuinoAPI


async def analyze_shot():
  async with GaggiuinoAPI() as client:
    shot = await client.get_shot(1)

    # Access shot metrics
    print(f"Shot ID: {shot.id}")
    print(f"Duration: {shot.duration}ms")
    print(f"Timestamp: {shot.timestamp}")

    # Access datapoints
    pressure_points = shot.datapoints.pressure
    flow_points = shot.datapoints.pumpFlow
    temperature_points = shot.datapoints.temperature
```

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
