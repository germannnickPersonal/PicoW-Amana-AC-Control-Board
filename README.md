# PicoThermostat

A Raspberry Pi Pico W–based thermostat and HVAC controller written in MicroPython.

PicoThermostat is a personal embedded-systems project designed to directly monitor and control residential HVAC equipment using thermistor inputs, relay outputs, compressor-protection logic, persistent logging, and a lightweight browser-based interface.

The current version is focused on **air-conditioning operation**. Heating and automatic heat/cool operation are reserved for future development and are not currently enabled in the user interface.

> **⚠️ Safety Warning**
>
> This project interfaces with HVAC equipment and can potentially control compressors, fans, relays, and circuits associated with hazardous voltages and high-current equipment.
>
> **Do not connect this project to live HVAC equipment unless you understand the electrical system, appropriate isolation methods, relay/contact ratings, HVAC control requirements, and the consequences of incorrect operation.**
>
> The software and documentation are provided **as-is and without warranty**. Anyone building, modifying, installing, or operating this project assumes all associated risk. Test control logic with loads safely isolated before allowing it to operate actual HVAC equipment.

---

## Current Features

The current AC-focused implementation includes:

* Raspberry Pi Pico W / MicroPython operation
* Three thermistor temperature inputs:
  * Room / return-air temperature
  * Indoor coil temperature
  * Outdoor coil temperature
* Low- and high-speed fan control
* Compressor relay control
* Reversing-valve output reserved for future heat-pump operation
* Electric-heat outputs reserved in configuration for future development
* Configurable compressor startup delay
* Fan/compressor sequencing and fan run-on behavior
* Indoor- and outdoor-coil thermal protection
* Emergency high-temperature shutdown
* Thermistor ADC fault detection
* ±0.5 °C cooling hysteresis to reduce rapid cycling
* Celsius and Fahrenheit thermostat settings
* Thread-safe shared state between HVAC control and web-server threads
* Persistent error and compressor-cycle logging
* Browser-based log-file download
* Lightweight local HTTP thermostat interface
* Browser-side and controller-side setpoint validation
* NTP-based clock synchronization for log timestamps
* Automatic Wi-Fi/server recovery after a web-server failure

---

## Web Interface

The Pico W hosts a lightweight HTTP interface directly on the local network.

The interface displays:

* Current operating mode
* Requested temperature
* Room temperature
* Indoor coil temperature
* Outdoor coil temperature

It provides controls for:

* Operating mode
* Celsius/Fahrenheit selection
* Temperature setpoint
* Downloading available `.txt` log files from the Pico

### Supported Modes

The current web interface exposes:

* Off
* Fan Low
* Fan High
* Cool Low
* Cool High

Heating and automatic modes exist only as future-development placeholders and are not currently exposed through the active mode list or web controls.

### Setpoint Range

| Units | Minimum | Maximum |
| --- | ---: | ---: |
| Fahrenheit | 65.0 °F | 84.8 °F |
| Celsius | 18.5 °C | 28.4 °C |

The browser validates input for convenience, and incoming requests are validated again by the Pico before they are allowed to modify the requested HVAC state.

---

## Control Behavior

### Cooling Hysteresis

Cooling uses a ±0.5 °C hysteresis band around the requested temperature.

For a requested temperature `T`:

* Compressor requested **ON** above `T + 0.5 °C`
* Existing compressor state retained inside the hysteresis band
* Compressor requested **OFF** below `T - 0.5 °C`

This reduces rapid compressor cycling around a single temperature threshold.

### Compressor and Fan Sequencing

The controller does not immediately energize the compressor simply because cooling is requested. Fan state, compressor-delay state, and thermal-protection state are checked before compressor activation.

With the current default configuration:

* `COMPRESSOR_DELAY = 15000` ms
* The fan must be running before the compressor is allowed to start
* The compressor startup delay must expire before compressor activation
* After the compressor is turned off, the fan remains subject to the same delay before it can be shut down

These values are configurable in `config.py`.

### Thermal Protection

The indoor- and outdoor-coil thermistors are monitored against configured limits.

Current defaults are:

| Sensor | Low Limit | High Limit |
| --- | ---: | ---: |
| Indoor Coil | 10 °C | 54.5 °C |
| Outdoor Coil | 10 °C | 54.5 °C |

If either coil temperature moves outside its configured operating range, the controller enters a thermal-protection state and prevents compressor operation. Once both coil readings are back inside their allowed ranges, the configured thermal-recovery delay must elapse before the thermal state is cleared.

The current default thermal delay is `60000` ms (60 seconds).

### Emergency Shutdown

If any monitored thermistor reports a temperature above **65.5 °C**, the controller calls its emergency shutdown routine, turns off the controlled outputs, records the event, and sets the shared emergency state.

In the current implementation, that shared emergency state prevents the main HVAC control loop from resuming normal control until the controller is restarted or the state is otherwise reset during development.

> These protections are experimental software safeguards and **must not be considered substitutes for the manufacturer's existing electrical, pressure, overload, thermal, or mechanical protection devices.**

---

## Hardware

The project currently expects:

* Raspberry Pi Pico W
* Three NTC thermistors
* Appropriate fixed resistors for the thermistor voltage dividers
* Properly rated and electrically isolated relay/control circuitry
* HVAC equipment suitable for the intended control scheme
* Appropriate power supply, fusing, and protection

### Thermistor Defaults

The current configuration assumes nominal:

* 30 kΩ thermistors at 25 °C
* Beta value of approximately 4000
* 33 kΩ fixed resistors
* 25 °C reference temperature

These values should be verified against the actual components being used. Measuring the thermistors and fixed resistors with a multimeter is recommended before relying on calculated temperatures.

### Current GPIO Assignments

The table below reflects the assignments currently defined in `config.py`.

| Function | GPIO |
| --- | ---: |
| High Fan Relay | 0 |
| Low Fan Relay | 1 |
| Compressor Relay | 2 |
| Reversing Valve Relay | 4 |
| Electric Heat 1 *(future)* | 5 |
| Electric Heat 2 *(future)* | 6 |
| Room Thermistor ADC | 26 |
| Indoor Coil Thermistor ADC | 27 |
| Outdoor Coil Thermistor ADC | 28 |

**Verify all GPIO assignments against your own hardware before energizing anything.**

---

## Project Structure

```text
PicoThermostat/
├── main.py
├── config.py
├── hvacBoard.py
├── thermistor.py
├── shared_variables.py
├── web_server.py
├── logger.py
├── errorlog.py
├── complogger.py
├── led.py
├── README.md
└── License & Permitted Use.md
```

### `main.py`

Initializes the HVAC controller, reserves emergency exception memory, starts the web-server thread, provides a startup LED indication, and runs the primary HVAC control loop.

### `config.py`

Contains Wi-Fi settings, relay GPIO assignments, thermistor parameters, control delays, and thermal limits.

### `hvacBoard.py`

Contains the HVAC equipment-control and state logic, including:

* Thermistor polling
* Fan control
* Compressor sequencing
* Cooling operation
* Thermal protection and recovery
* Emergency shutdown
* Compressor-cycle logging calls

### `thermistor.py`

Handles ADC averaging, voltage-divider resistance calculation, NTC Beta-equation temperature conversion, and basic ADC fault-range checking.

### `shared_variables.py`

Provides shared HVAC state for the main control loop and web-server thread, including a lock for thread-safe access and packing/unpacking of mode, setpoint, and temperature-unit state.

### `web_server.py`

Implements:

* Wi-Fi connection and reconnection handling
* NTP time synchronization
* Local HTTP server
* Thermostat web interface
* Request parsing and URL decoding
* Input validation
* Shared-state updates
* Log-file discovery and download

### `logger.py`

Provides the base persistent logger, timestamp formatting, entry trimming, and file-writing behavior used by the specialized loggers.

### `errorlog.py`

Provides the `ErrorLogger` used for persistent error/event records. Exception tracebacks are captured when available.

### `complogger.py`

Provides the `CompressorLogger`, which records compressor state changes, elapsed ON/OFF duration, and the three current temperature readings.

### `led.py`

Provides the onboard LED helper used for startup/status blinking.

### `License & Permitted Use.md`

Contains the project's license and permitted-use terms. Review those terms before redistributing or reusing the project.

---

## Configuration

Before running the project, review `config.py` carefully.

At minimum, configure the Wi-Fi settings:

```python
WIFI_SSID = "your-network"
WIFI_PASSWORD = "your-password"
```

Also verify:

* Relay GPIO assignments
* Thermistor ADC assignments
* Thermistor nominal resistance (`R0`)
* Fixed-resistor values
* Thermistor Beta values
* Reference temperatures
* Indoor/outdoor coil temperature limits
* Compressor delay
* Thermal recovery delay
* Reversing-valve delay reserved for future heat-pump operation

---

## Running

Copy the project files to a Raspberry Pi Pico W running a compatible version of MicroPython.

On startup, the project:

1. Allocates the emergency MicroPython exception buffer.
2. Initializes the HVAC controller and GPIO outputs.
3. Starts the web-server thread.
4. Blinks the onboard LED three times as a startup/thread indication.
5. Begins the HVAC monitoring and control loop.

The web-server thread connects to the configured Wi-Fi network and prints an address similar to:

```text
HVAC page: http://192.168.1.123/
```

Open that address from a device on the same local network to access the thermostat interface.

---

## Logging

The project currently uses two persistent text logs:

### Error Log

`ErrorLog.txt`

* Stores errors and event messages
* Keeps up to 50 entries by default
* Captures MicroPython exception output when an exception object is supplied

### Compressor Log

`CompressorLog.txt`

* Stores compressor ON/OFF state changes
* Records the duration of the previous compressor state
* Records room, indoor-coil, and outdoor-coil temperatures
* Keeps up to 100 entries by default

Available `.txt` files can be selected and downloaded from the web interface.

The logger currently converts UTC to a fixed **UTC−6** timestamp. That matches CST, but it does not automatically adjust for daylight saving time.

---

## Development Status

**Current status: experimental / active development**

The present version is focused on air-conditioning functionality and local-network control.

Areas intended for future development include:

* Heating operation
* Heat-pump reversing-valve control
* Automatic heating/cooling modes
* Watchdog integration
* Additional fault handling
* Improved web interface and status reporting
* Additional operating-state information
* Further hardware testing and validation
* Credential/secrets separation for easier public distribution

The watchdog import and development placeholders remain in the project, but the watchdog is **not currently active** in `main.py`.

This project should not currently be treated as a drop-in replacement for a certified commercial thermostat or HVAC controller.

---

## Testing

When modifying the project, test progressively.

A recommended development sequence is:

1. Test thermistor readings independently.
2. Verify GPIO outputs without HVAC equipment connected.
3. Test relay/interface circuitry with safe loads.
4. Verify fan-state transitions.
5. Verify compressor startup and shutdown delays.
6. Verify compressor/fan interlocks.
7. Simulate thermal-limit conditions.
8. Verify thermal recovery timing.
9. Verify emergency shutdown behavior.
10. Test web commands and log downloads without the compressor connected.
11. Only then consider controlled testing with actual HVAC equipment.

Never rely solely on software to protect equipment from an unsafe electrical or mechanical configuration.

---

## Authorship & AI Assistance

**PicoThermostat was developed by Nick Germann.**

The project architecture, hardware integration, HVAC control behavior, safety logic, and implementation decisions were developed and written as part of a personal embedded-systems project.

AI tools were used as a development aid for:

* Code review
* Debugging
* Identifying implementation errors
* Assisting with development and refinement of the `web_server.py` interface
* Documentation and comment cleanup

The project was iteratively reviewed, modified, and tested by the author rather than being produced as AI-generated codebase.

---

## Disclaimer

This is an experimental personal project involving control of physical HVAC equipment.

The author makes no representation that the software is suitable for any particular HVAC system, complies with applicable electrical/building codes, or provides the protections required by any equipment manufacturer.

Use of this software does not replace appropriate:

* Fusing or circuit protection
* Electrical isolation
* Overcurrent protection
* Compressor overload protection
* Pressure switches
* Thermal protection
* Manufacturer-installed safety devices
* Proper HVAC servicing procedures
* Applicable electrical and mechanical codes

**You are responsible for determining whether this project is appropriate and safe for your application.**

Use it at your own risk.
