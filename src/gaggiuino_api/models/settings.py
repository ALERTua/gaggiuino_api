"""Models of the settings of the machine."""

from dataclasses import dataclass

from ..enums import ReleaseChannel
from .base import Model, api


@dataclass(frozen=True, kw_only=True)
class BoilerSettings(Model):
    """The boiler settings, from `GET /api/settings/boiler`."""

    steam_set_point: int = api("steamSetPoint")
    offset_temp: int = api("offsetTemp")
    hpwr: int = api("hpwr")
    """The heating power setting of the boiler."""
    main_divider: int = api("mainDivider")
    brew_divider: int = api("brewDivider")
    brew_delta_state: bool = api("brewDeltaState")
    dream_steam_state: bool = api("dreamSteamState")
    startup_heat_delta: int = api("startupHeatDelta")
    dual_boiler_enabled: bool | None = api("dualBoilerEnabled", default=None)
    """True when the dual boiler mode is on. The documentation does not describe the key."""


@dataclass(frozen=True, kw_only=True)
class SystemSettings(Model):
    """The system settings, from `GET /api/settings/system`."""

    pump_flow_at_zero: float = api("pumpFlowAtZero")
    """The pump calibration: the flow of the pump at zero pressure."""
    timezone_offset_minutes: int = api("timezoneOffsetMinutes")
    """The offset of the local time zone from UTC, in minutes."""
    sprofiler_token: str = api("sprofilerToken")
    """The API token of the sprofiler service."""
    visualizer_token: str = api("visualizerToken")
    """The API token of the Visualizer service."""
    services_state: bool = api("servicesState")
    wifi_enabled: bool = api("wifiEnabled")
    release_channel: ReleaseChannel | int = api("releaseChannel")
    """The release channel of the firmware updates: 0 stable, 1 test, 2 debug.

    An unknown value stays the raw integer.
    """
    momentary_switches: bool = api("momentarySwitches")
    ungroup_home_tiles: bool = api("ungroupHomeTiles")
    alternative_flush: bool = api("alternativeFlush")
    mqtt_enabled: bool = api("mqttEnabled")
    """Turns the built-in MQTT client on or off."""
    mqtt_host: str = api("mqttHost")
    """The host name or IP address of the MQTT broker. Empty means no connection."""
    mqtt_port: int = api("mqttPort")
    """The port of the MQTT broker, 1883 by default."""
    mqtt_username: str = api("mqttUsername")
    """The user name for the MQTT broker. Empty when the broker needs no login."""
    mqtt_password: str = api("mqttPassword")
    """The password for the MQTT broker. Empty when the broker needs no login."""
    mqtt_topic_prefix: str = api("mqttTopicPrefix")
    """The prefix of each MQTT topic that the machine publishes or reads."""
    machine_name: str | None = api("machineName", default=None)
    """The name of the machine. The documentation does not describe the key."""
    min_shot_duration_seconds: int | None = api("minShotDurationSeconds", default=None)
    """The minimum duration of a shot, in seconds.

    The documentation does not describe the key.
    """
    auto_flush_duration_seconds: int | None = api(
        "autoFlushDurationSeconds", default=None
    )
    """The duration of the automatic flush, in seconds.

    The documentation does not describe the key.
    """


@dataclass(frozen=True, kw_only=True)
class LedColor(Model):
    """The color of the LED, with each component from 0 to 255."""

    r: int = api("R")
    g: int = api("G")
    b: int = api("B")


@dataclass(frozen=True, kw_only=True)
class TofSettings(Model):
    """The limits of the time-of-flight sensor."""

    max: int = api("max")
    min: int = api("min")


@dataclass(frozen=True, kw_only=True)
class LedSettings(Model):
    """The LED settings, from `GET /api/settings/led`."""

    color: LedColor = api("color")
    state: bool = api("state")
    """True when the LED is on."""
    disco: bool = api("disco")
    """True when the disco mode of the LED is on."""
    tof: TofSettings = api("tof")


@dataclass(frozen=True, kw_only=True)
class ScalesSettings(Model):
    """The scales settings, from `GET /api/settings/scales`."""

    force_predictive: bool = api("forcePredictive")
    hw_scales_enabled: bool = api("hwScalesEnabled")
    """True when the hardware scales are on."""
    hw_scales_f1: int = api("hwScalesF1")
    """The first calibration factor of the hardware scales."""
    hw_scales_f2: int = api("hwScalesF2")
    """The second calibration factor of the hardware scales."""
    bt_scales_enabled: bool = api("btScalesEnabled")
    """True when the Bluetooth scales are on."""
    bt_scales_auto_connect: bool = api("btScalesAutoConnect")
    bt_scales_pinned_mac: str = api("btScalesPinnedMac")
    """The MAC address of the Bluetooth scales that the machine connects to."""


@dataclass(frozen=True, kw_only=True)
class DisplaySettings(Model):
    """The display settings, from `GET /api/settings/display`."""

    lcd_brightness: int = api("lcdBrightness")
    """The brightness of the screen, from 0 to 100."""
    lcd_dark_mode: bool = api("lcdDarkMode")
    lcd_sleep: int = api("lcdSleep")
    """The idle time before the screen sleeps, in minutes."""
    lcd_go_home: int = api("lcdGoHome")
    """The time after the end of a shot before the shot graph closes, in seconds."""
    lcd_close_on_brew_off: bool = api("lcdCloseOnBrewOff")
    simple_ui: bool | None = api("simpleUI", default=None)
    """True for the simple user interface.

    The documentation describes the key, and the firmware c929939 does not send it.
    """
    modern_ui: bool | None = api("modernUI", default=None)
    """True for the modern user interface. The documentation does not describe the key."""


@dataclass(frozen=True, kw_only=True)
class ThemeSettings(Model):
    """The theme colors, from `GET /api/settings/theme`."""

    colour_primary: int = api("colourPrimary")
    """The primary color, in the RGB565 format."""
    colour_secondary: int = api("colourSecondary")
    """The secondary color, in the RGB565 format."""


@dataclass(frozen=True, kw_only=True)
class Versions(Model):
    """The versions of the firmware parts, from `GET /api/settings/versions`.

    The endpoint is read-only.
    """

    core_version: str = api("coreVersion")
    """The version of the core firmware."""
    front_version: str = api("frontVersion")
    """The version of the frontend firmware."""
    static_version: str = api("staticVersion")
    """The version of the static web assets."""


@dataclass(frozen=True, kw_only=True)
class WebUiSettings(Model):
    """The web interface settings, the group `webUi` of `GET /api/settings`.

    The group has no endpoint of its own. The documentation does not describe the group.
    The energy estimate of the machine uses the rated power of each load.
    """

    brew_heater_watts: int | None = api("brewHeaterWatts", default=None)
    """The rated power of the brew heater, in watts."""
    steam_heater_watts: int | None = api("steamHeaterWatts", default=None)
    """The rated power of the steam heater, in watts."""
    pump_watts: int | None = api("pumpWatts", default=None)
    """The rated power of the pump, in watts."""
    idle_watts: int | None = api("idleWatts", default=None)
    """The power of the idle machine, in watts."""


@dataclass(frozen=True, kw_only=True)
class Settings(Model):
    """All settings in one answer, from `GET /api/settings`."""

    boiler: BoilerSettings = api("boiler")
    system: SystemSettings = api("system")
    led: LedSettings = api("led")
    scales: ScalesSettings = api("scales")
    display: DisplaySettings = api("display")
    theme: ThemeSettings = api("theme")
    versions: Versions = api("versions")
    web_ui: WebUiSettings | None = api("webUi", default=None)
    """The web interface settings. The documentation does not describe the group."""
