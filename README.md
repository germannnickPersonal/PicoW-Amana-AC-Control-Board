# PicoW-Amana-AC-Control-Board
# PicoThermostat

A Raspberry Pi Pico W–based thermostat and HVAC controller written in MicroPython.

PicoThermostat is a personal embedded-systems project designed to directly monitor and control a residential HVAC system using temperature sensors, relay outputs, compressor protection logic, and a lightweight browser-based interface.

The current version focuses on **air-conditioning operation**. Heating and additional automatic-control features are planned but are not yet enabled.

> **⚠️ Safety Warning**
>
> This project interfaces with HVAC equipment and can potentially control compressors, fans, relays, and circuits associated with hazardous voltages and high-current equipment.
>
> **Do not connect this project to live HVAC equipment unless you understand the electrical system, appropriate isolation methods, relay/contact ratings, HVAC control requirements, and the consequences of incorrect operation.**
>
> The software and documentation are provided **as-is and without warranty**. Anyone building, modifying, installing, or operating this project assumes all associated risk. Test control logic with loads safely isolated before allowing it to operate actual HVAC equipment.

---

## Features

The current AC-focused implementation includes:

* Raspberry Pi Pico W / MicroPython operation
* Three thermistor temperature inputs:

  * Room / return-air temperature
  * Indoor coil temperature
  * Outdoor coil temperature
* Low- and high-speed fan control
* Compressor relay control
* Reversing-valve output reserved for future heat-pump operation
* Configurable compressor startup delay
* Fan/compressor sequencing
* Coil-temperature protection
* Emergency high-temperature shutdown
* Thermistor fault detection
* Temperature hysteresis to prevent rapid cycling
* Celsius and Fahrenheit thermostat settings
* Thread-safe shared state between HVAC control and web-server threads
* Persistent on-device error logging
* Lightweight HTTP thermostat interface
* Browser-side and controller-side setpoint validation
* Automatic Wi-Fi reconnection after web-server failure

---

## Web Interface

The Pico W hosts a lightweight HTTP interface directly on the local network.

The interface displays:

* Current operating mode
* Requested temperature
* Room temperature
* Indoor coil temperature
* Outdoor coil temperature

It also provides controls for:

* Operating mode
* Celsius/Fahrenheit selection
* Temperature setpoint

Current supported modes are:

* Off
* Fan Low
* Fan High
* Cool Low
* Cool High

The thermostat accepts setpoints within:

| Units      | Minimum | Maximum |
| ---------- | ------: | ------: |
| Fahrenheit | 65.0 °F | 84.8 °F |
| Celsius    | 18.5 °C | 28.4 °C |

The browser performs input validation for convenience, while incoming requests are validated again by the Pico before they are allowed to modify the requested HVAC state.

---

## Control Behavior

### Cooling Hysteresis

Cooling uses a ±0.5 °C hysteresis band around the requested temperature.

For a requested temperature `T`:

* Compressor requested **ON** above `T + 0.5 °C`
* Existing compressor state is retained inside the hysteresis band
* Compressor requested **OFF** below `T - 0.5 °C`

This prevents the compressor from rapidly cycling around a single temperature threshold.

### Compressor Protection

The controller incorporates delays and sequencing intended to prevent inappropriate compressor operation.

The compressor will not immediately start simply because cooling is requested. Fan state, compressor-delay state, and thermal-protection state are considered before compressor activation.

### Thermal Protection

Indoor and outdoor coil thermistors are monitored against configured limits.

If a coil temperature moves outside its permitted operating range, the controller enters a thermal-protection state and prevents compressor operation until temperatures recover and the configured recovery delay has elapsed.

An extreme temperature reading can additionally trigger an emergency shutdown.

> These protections are experimental software safeguards and **must not be considered substitutes for the manufacturer's existing electrical, pressure, overload, thermal, or mechanical protection devices.**

---

## Hardware

The project currently expects:

* Raspberry Pi Pico W
* Three NTC thermistors
* Appropriate fixed resistors for the thermistor voltage dividers
* Properly rated and electrically isolated relay/control circuitry
* HVAC equipment suitable for the intended control scheme
* Appropriate power supply and protection

The default configuration currently assumes nominal:

* 30 kΩ thermistors at 25 °C
* Beta value of approximately 4000
* 33 kΩ fixed resistors

These values should be verified against the actual components being used.

### Current GPIO Assignments

| Function                    | GPIO |
| --------------------------- | ---: |
| Low Fan Relay               |    1 |
| High Fan Relay              |    2 |
| Compressor Relay            |    3 |
| Reversing Valve Relay       |    4 |
| Electric Heat 1 *(future)*  |    5 |
| Electric Heat 2 *(future)*  |    6 |
| Room Thermistor ADC         |   26 |
| Indoor Coil Thermistor ADC  |   27 |
| Outdoor Coil Thermistor ADC |   28 |

**Verify all GPIO assignments against your own hardware before energizing anything.**

---

## Project Structure

```text
PicoThermostat/
├── main.py
├── hvacBoard.py
├── thermistor.py
├── web_server.py
├── shared_variables.py
├── errorlog.py
└── config.py
```

### `main.py`

Initializes the HVAC controller, starts the web-server thread, and runs the primary control loop.

### `hvacBoard.py`

Contains the HVAC state and equipment-control logic, including:

* Fan control
* Compressor sequencing
* Cooling operation
* Thermal protection
* Emergency shutdown

### `thermistor.py`

Handles ADC sampling, voltage-divider resistance calculation, and NTC Beta-equation temperature conversion.

### `web_server.py`

Implements the Pico W Wi-Fi connection, HTTP server, thermostat web interface, request parsing, input validation, and web-side state updates.

### `shared_variables.py`

Provides the shared HVAC state used by the control and web-server threads, including locking for thread-safe access.

### `errorlog.py`

Provides a lightweight persistent error/event logger suitable for MicroPython.

### `config.py`

Contains hardware assignments, Wi-Fi configuration, thermistor parameters, delays, and thermal limits.

---

## Configuration

Before running the project, edit `config.py`.

At minimum, configure:

```python
WIFI_SSID = "your-network"
WIFI_PASSWORD = "your-password"
```

You should also verify:

* Relay GPIO assignments
* Thermistor ADC assignments
* Thermistor nominal resistance
* Fixed-resistor values
* Thermistor Beta values
* Temperature limits
* Compressor delays

### Do Not Commit Wi-Fi Credentials

This repository is public, **do not commit your real Wi-Fi password**.

Consider keeping credentials in a separate untracked configuration/secrets file or replacing them with placeholders before pushing any repository/fork to GitHub.

---

## Running

Copy the project files to a Raspberry Pi Pico W running a compatible version of MicroPython.

On startup, the web-server thread connects to the configured Wi-Fi network and prints an address similar to:

```text
HVAC page: http://192.168.1.123/
```

Open that address from a device on the same network to access the thermostat interface.

---

## Development Status

**Current status: experimental / active development**

The present version is focused on air-conditioning functionality.

Areas intended for future development include:

* Heating operation
* Heat-pump reversing-valve control
* Automatic heating/cooling modes
* Watchdog integration
* Additional fault handling
* Improved web interface
* Additional operating-state/status information
* Further hardware testing and validation

This project should not currently be treated as a drop-in replacement for a certified commercial thermostat or HVAC controller.

---

## Testing

When modifying the project, test progressively.

A recommended development sequence is:

1. Test thermistor readings independently.
2. Verify GPIO outputs without HVAC equipment connected.
3. Test relay/interface circuitry with safe loads.
4. Verify fan-state transitions.
5. Verify compressor delays and interlocks.
6. Simulate thermal-limit conditions.
7. Verify emergency shutdown behavior.
8. Test web commands without the compressor connected.
9. Only then consider controlled testing with actual HVAC equipment.

Never rely solely on software to protect equipment from an unsafe electrical or mechanical configuration.

---

## Authorship & AI Assistance

**PicoThermostat was developed by Nick Germann.**

The project architecture, hardware integration, HVAC control behavior, safety logic, and implementation decisions were developed as part of a personal embedded-systems project.

AI tools were used as a development aid for:

* Code review
* Debugging
* Identifying implementation errors
* Discussing control-flow and concurrency issues
* Assisting with development and refinement of the `web_server.py` interface

The project was iteratively reviewed, modified, and tested by the author rather than being produced as a fully AI-generated codebase.

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
