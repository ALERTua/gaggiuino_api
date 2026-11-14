"""The model of the live status of the machine."""

from dataclasses import dataclass

from ..enums import OperationMode
from .base import Model, api


@dataclass(frozen=True, kw_only=True)
class Status(Model):
    """The live status of the machine: sensors, outputs, system state and energy use.

    It is the one object in the list that `GET /api/system/status` returns.
    A newer firmware can add keys to this object, and the model ignores them.
    """

    up_time: int = api("upTime")
    """The time since the machine started, in seconds."""
    profile_id: int = api("profileId")
    """The id of the active profile."""
    profile_name: str = api("profileName")
    """The name of the active profile."""
    target_temperature: float = api("targetTemperature")
    """The target temperature of the boiler."""
    temperature: float = api("temperature")
    """The measured temperature of the boiler."""
    pressure: float = api("pressure")
    """The measured pressure, in bar."""
    water_level: int = api("waterLevel")
    """The water level of the tank."""
    weight: float = api("weight")
    """The weight on the scales."""
    brew_switch_state: bool = api("brewSwitchState")
    """The state of the brew switch."""
    steam_switch_state: bool = api("steamSwitchState")
    """The state of the steam switch."""
    machine_name: str = api("machineName")
    """The name of the machine that the user set."""
    boiler_temperature: float | None = api("boilerTemperature", default=None)
    """The temperature of the boiler; the documentation does not describe this key.

    It has the same value as `temperature`.
    """
    pump_flow: float = api("pumpFlow")
    """The flow of the pump, in mL/s."""
    weight_flow: float = api("weightFlow")
    """The flow that the scales measure: the change of the weight per second."""
    brew_active: bool = api("brewActive")
    """True while the machine brews."""
    brew_switch_active: bool | None = api("brewSwitchActive", default=None)
    """A brew switch flag; the documentation does not describe this key.

    Its difference from `brew_switch_state` and `brew_active` is not documented.
    """
    steam_active: bool = api("steamActive")
    """True while the machine makes steam."""
    hot_water_active: bool = api("hotWaterActive")
    """True while the machine gives hot water."""
    boiler_on: bool = api("boilerOn")
    """The commanded state of the boiler relay, not a sensor reading."""
    valve_open: bool = api("valveOpen")
    """The commanded state of the brew valve, not a sensor reading."""
    steam_valve_on: bool = api("steamValveOn")
    """The commanded state of the steam valve, not a sensor reading.

    It is always false on the current boards.
    """
    valve_b_open: bool = api("valveBOpen")
    """The commanded state of the valve that routes the boiler to the group or the tank.

    It is not a sensor reading. It can be true only on the board with the core type
    `STM32U585-PCB-GSK`.
    """
    steam_boiler_relay_on: bool = api("steamBoilerRelayOn")
    """The commanded state of the steam boiler relay, not a sensor reading.

    It is always false on the current boards.
    """
    operation_mode: OperationMode = api("operationMode")
    """The operation mode; `UNKNOWN` for a value that the library does not know."""
    startup_init_finished: bool = api("startupInitFinished")
    """True when the startup of the machine is complete."""
    tof_ready: bool = api("tofReady")
    """True when the time-of-flight water level sensor is ready."""
    scales_present: bool = api("scalesPresent")
    """True when scales are connected."""
    tare_pending: bool = api("tarePending")
    """True while a tare of the scales waits to complete."""
    steam_forgotten_on: bool | None = api("steamForgottenOn", default=None)
    """A flag of the steam switch left on; the REST documentation does not describe this key."""
    core_version: str = api("coreVersion")
    """The version of the core firmware."""
    core_type: str = api("coreType")
    """The board type of the core, for example `STM32U585-PCB-GSK`."""
    pcb_v2: bool | None = api("pcbV2", default=None)
    """True when the core is built for the PCB V2 board.

    The REST documentation does not describe this key.
    """
    power_line_frequency: int = api("powerLineFrequency")
    """The frequency of the mains power, in Hz."""
    debug_logging_enabled: bool | None = api("debugLoggingEnabled", default=None)
    """True when debug logging is on; the REST documentation does not describe this key."""
    thermocouple_faulted: bool = api("thermocoupleFaulted")
    """True when the thermocouple cannot be read."""
    pressure_sensor_faulted: bool = api("pressureSensorFaulted")
    """True when the pressure sensor cannot be read."""
    thermocouple_fault_reason: str = api("thermocoupleFaultReason")
    """The cause of the thermocouple fault; empty while `thermocouple_faulted` is false."""
    pressure_sensor_fault_reason: str = api("pressureSensorFaultReason")
    """The cause of the pressure sensor fault; empty while `pressure_sensor_faulted` is false."""
    live_power_watts: int = api("livePowerWatts")
    """The estimated power that the machine uses now, in W."""
    energy_watt_hours: float = api("energyWattHours")
    """The total energy use, in Wh; the machine keeps this counter across power cycles."""
    energy_tracked_seconds: int = api("energyTrackedSeconds")
    """The total time of the energy measurement, in seconds."""
    session_energy_watt_hours: float = api("sessionEnergyWattHours")
    """The energy use since the last physical power cycle, in Wh.

    It starts at zero after a physical power cycle and is kept across a software restart.
    """
    session_energy_tracked_seconds: int = api("sessionEnergyTrackedSeconds")
    """The time of the energy measurement since the last physical power cycle, in seconds.

    It starts at zero after a physical power cycle and is kept across a software restart.
    """
    readiness_state: int | None = api("readinessState", default=None)
    """The raw readiness state; the documentation does not describe this key or its values.

    Seen: `1` during the warmup after a start, `2` while the boiler heats to a new target,
    and `3` at the target.
    """
    warmup_elapsed_seconds: int | None = api("warmupElapsedSeconds", default=None)
    """The time since the warmup started, in seconds; the documentation does not describe this key."""
    warmup_remaining_seconds: int | None = api("warmupRemainingSeconds", default=None)
    """The time left until the warmup ends, in seconds; the documentation does not describe this key."""
