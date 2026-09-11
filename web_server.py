import ntptime
import network
import os
import socket
import time

import config
import shared_variables
from errorlog import logger


def run_web_server():
    while True:
        try:
            server_session()

        except Exception as error:
            logger.log("Run Web Server", error)

        try:
            wlan = network.WLAN(network.STA_IF)
            wlan.disconnect()
            wlan.active(False)

        except Exception as error:
            logger.log("Wifi Shutdown", error)

        time.sleep(2)


def server_session():
    wlan = connect_wifi()
    sync_time()

    address = socket.getaddrinfo("0.0.0.0", 80)[0][-1]

    server = socket.socket()
    server.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server.bind(address)
    server.listen(2)
    server.settimeout(1.0)

    # Wi-Fi is connected here, so the assigned address
    # can now be safely displayed.
    print(
        "HVAC page: http://{}/".format(
            wlan.ifconfig()[0]
        )
    )

    try:
        while True:
            client = None

            # Handle accept() separately because the normal
            # one-second socket timeout raises OSError.
            try:
                client, _ = server.accept()

            except OSError:
                continue

            try:
                client.settimeout(1.0)

                request = client.recv(1024).decode()

                request_path = get_request_path(request)

                if request_path.startswith("/download?"):
                    send_log_file(client, request_path)

                else:
                    parse_request(request)

                    body = page()
                    body_bytes = body.encode()

                    header = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: text/html; charset=utf-8\r\n"
                        "Content-Length: {}\r\n"
                        "Connection: close\r\n"
                        "\r\n"
                    ).format(len(body_bytes))

                    client.sendall(header.encode())
                    client.sendall(body_bytes)

            except Exception as error:
                logger.log("Web Client", error)

            finally:
                if client is not None:
                    try:
                        client.close()
                    except:
                        pass

    finally:
        try:
            server.close()
        except:
            pass


def connect_wifi(timeout_ms=15000):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        wlan.connect(
            config.WIFI_SSID,
            config.WIFI_PASSWORD
        )

        started = time.ticks_ms()

        while not wlan.isconnected():
            if (
                time.ticks_diff(
                    time.ticks_ms(),
                    started
                )
                > timeout_ms
            ):
                wlan.active(False)

                raise RuntimeError(
                    "Wi-Fi connection timeout"
                )

            time.sleep_ms(200)

    return wlan


def page():
    with shared_variables.resource_lock:
        packed_state = shared_variables.modeTempType

        air_temp = shared_variables.current_temps[0]
        indoor_temp = shared_variables.current_temps[1]
        outdoor_temp = shared_variables.current_temps[2]

    mode, set_temp, temp_type = (
        shared_variables.unpackModeTemp(
            packed_state)
    )

    log_files = get_log_files()
    log_options = ""

    for filename in log_files:
        log_options += (
            '<option value="{}">{}</option>'
        ).format(filename, filename)

    # Controller temperatures are stored internally in Celsius.
    # Convert values only when preparing the webpage display.
    if temp_type == "F":
        air_display = round(
            (air_temp * 9 / 5) + 32,
            1
        )

        indoor_display = round(
            (indoor_temp * 9 / 5) + 32,
            1
        )

        outdoor_display = round(
            (outdoor_temp * 9 / 5) + 32,
            1
        )

        min_temp = 65
        max_temp = 84.8

    else:
        air_display = air_temp
        indoor_display = indoor_temp
        outdoor_display = outdoor_temp

        min_temp = 18.5
        max_temp = 28.4

    mode_selected = {
        "off": "",
        "fan low": "",
        "fan high": "",
        "cool low": "",
        "cool high": ""
    }

    if mode in mode_selected:
        mode_selected[mode] = "selected"

    type_selected = {
        "F": "",
        "C": ""
    }

    if temp_type in type_selected:
        type_selected[temp_type] = "selected"

    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta
        name="viewport"
        content="width=device-width, initial-scale=1"
    >

    <title>Pico HVAC</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 500px;
            margin: 30px auto;
            padding: 20px;
        }

        h1 {
            margin-bottom: 25px;
        }

        .status {
            padding: 15px;
            border: 1px solid #aaa;
            border-radius: 8px;
            margin-bottom: 20px;
        }

        .controls {
            padding: 15px;
            border: 1px solid #aaa;
            border-radius: 8px;
        }

        select,
        input {
            font-size: 16px;
            padding: 6px;
        }

        input[type="submit"] {
            padding: 8px 18px;
            cursor: pointer;
        }
    </style>
</head>

<body>

    <h1>Pico HVAC Controller</h1>

    <div class="status">
        <h2>Status</h2>

        <p>Mode: %s</p>
        <p>Set Temperature: %s %s</p>

        <h2>Temperatures</h2>

        <p>Room: %s %s</p>
        <p>Indoor Coil: %s %s</p>
        <p>Outdoor Coil: %s %s</p>
    </div>

    <div class="controls">
        <h2>Controls</h2>

        <form action="/" method="GET">

            <label for="mode">
                Mode:
            </label>

            <select
                name="mode"
                id="mode"
            >
                <option
                    value="off"
                    %s
                >
                    Off
                </option>

                <option
                    value="fan low"
                    %s
                >
                    Fan Low
                </option>

                <option
                    value="fan high"
                    %s
                >
                    Fan High
                </option>

                <option
                    value="cool low"
                    %s
                >
                    Cool Low
                </option>

                <option
                    value="cool high"
                    %s
                >
                    Cool High
                </option>
            </select>

            <br><br>

            <label for="type">
                Temperature Unit:
            </label>

            <select
                name="type"
                id="type"
                onchange="changeTempType()"
            >
                <option
                    value="F"
                    %s
                >
                    F
                </option>

                <option
                    value="C"
                    %s
                >
                    C
                </option>
            </select>

            <br><br>

            <label for="temp">
                Set Temperature:
            </label>

            <input
                type="number"
                id="temp"
                name="temp"
                value="%s"
                min="%s"
                max="%s"
                step="0.1"
                required
            >

            <br><br>

            <input
                type="submit"
                value="Apply"
            >

        </form>
    </div>

    <script>
        var previousType = "%s";

        function changeTempType() {
            var type =
                document.getElementById("type");

            var temp =
                document.getElementById("temp");

            var value =
                parseFloat(temp.value);

            if (type.value === "F") {
                temp.min = "65";
                temp.max = "84.8";

                if (
                    previousType === "C"
                    && !isNaN(value)
                ) {
                    value =
                        (value * 9 / 5) + 32;

                    temp.value =
                        value.toFixed(1);
                }

            } else {
                temp.min = "18.5";
                temp.max = "28.4";

                if (
                    previousType === "F"
                    && !isNaN(value)
                ) {
                    value =
                        (value - 32) * 5 / 9;

                    temp.value =
                        value.toFixed(1);
                }
            }

            previousType = type.value;
        }
    </script>

    <div class="controls">
        <h2>Logs</h2>

        <form action="/download" method="GET">

            <label for="logfile">
                Select Log:
            </label>

            <select
                name="file"
                id="logfile"
            >
                %s
            </select>

            <br><br>

            <input
                type="submit"
                value="Download Log"
            >

        </form>
    </div>

</body>
</html>
""" % (
        mode,
        set_temp,
        temp_type,

        air_display,
        temp_type,

        indoor_display,
        temp_type,

        outdoor_display,
        temp_type,

        mode_selected["off"],
        mode_selected["fan low"],
        mode_selected["fan high"],
        mode_selected["cool low"],
        mode_selected["cool high"],

        type_selected["F"],
        type_selected["C"],

        set_temp,
        min_temp,
        max_temp,

        temp_type,

        log_options
    )

    return html


def parse_request(request):
    try:
        path = get_request_path(request)

        if not path:
            return

        # A plain GET / request only needs the current page.
        if "?" not in path:
            return

        path, query = path.split("?", 1)

        params = parse_query(query)

        # Control requests must include mode, temperature, and unit.
        if (
            "mode" not in params
            or "temp" not in params
            or "type" not in params
        ):
            return

        mode = params["mode"]
        temp_type = params["type"]

        try:
            temp = float(params["temp"])

        except ValueError:
            logger.log(
                "Parse Request",
                "Invalid temperature format"
            )
            return

        # NaN does not behave normally in range comparisons,
        # so reject it explicitly.
        if temp != temp:
            logger.log(
                "Parse Request",
                "Invalid temperature value"
            )
            return

        valid_modes = (
            "off",
            "fan low",
            "fan high",
            "cool low",
            "cool high"
        )

        if mode not in valid_modes:
            logger.log(
                "Parse Request",
                "Invalid mode: {}".format(mode)
            )
            return

        if temp_type not in ("F", "C"):
            logger.log(
                "Parse Request",
                "Invalid temperature type: {}".format(
                    temp_type
                )
            )
            return

        if temp_type == "F":
            if temp < 65 or temp > 84.8:
                logger.log(
                    "Parse Request",
                    "F temperature out of range: {}".format(
                        temp
                    )
                )
                return

        elif temp_type == "C":
            if temp < 18.5 or temp > 28.4:
                logger.log(
                    "Parse Request",
                    "C temperature out of range: {}".format(
                        temp
                    )
                )
                return

        # The packed state stores the setpoint to one decimal place.
        temp = round(temp, 1)

        # Update shared controller state only after every
        # requested value has passed validation.
        packed_state = (shared_variables.packModeTemp(
                mode, temp, temp_type
            )
        )

        with shared_variables.resource_lock:
            shared_variables.modeTempType = packed_state

    except Exception as error:
        logger.log("Parse Request", error)


def url_decode(value):
    # HTML form encoding commonly represents spaces with +
    value = value.replace("+", " ")

    result = ""
    i = 0

    while i < len(value):
        if (
            value[i] == "%"
            and i + 2 < len(value)
        ):
            try:
                hex_value = value[i + 1:i + 3]

                result += chr(
                    int(hex_value, 16)
                )

                i += 3
                continue

            except ValueError:
                pass

        result += value[i]
        i += 1

    return result

def sync_time():
    if shared_variables.time_init:
        return

    try:
        ntptime.settime()

        with shared_variables.resource_lock:
            shared_variables.time_init = True

    except Exception as error:
        logger.log("Time Syne", error)


def get_log_files():
    files = []

    try:
        for filename in os.listdir():
            if filename.endswith(".txt"):
                files.append(filename)
        files.sort()

    except Exception as error:
        logger.log("Get Log Files", error)

    return files


def parse_query(query):
    params = {}

    for pair in query.split("&"):
        if "=" not in pair:
            continue

        key, value = pair.split("=", 1)

        key = url_decode(key)
        value = url_decode(value)

        params[key] = value

    return params


def get_request_path(request):
    first_line = request.split("\r\n")[0]

    parts = first_line.split(" ")

    if len(parts) < 2:
        return ""

    return parts[1]

def send_log_file(client, request_path):
    try:
        if "?" not in request_path:
            return

        path, query = request_path.split("?", 1)

        params = parse_query(query)

        if "file" not in params:
            return

        filename = params["file"]

        if filename not in get_log_files():
            return

        file_size = os.stat(filename)[6]

        header = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain; charset=utf-8\r\n"
            "Content-Disposition: attachment; filename=\"{}\"\r\n"
            "Content-Length: {}\r\n"
            "Connection: close\r\n"
            "\r\n"
        ).format(
            filename,
            file_size
        )

        client.sendall(header.encode())
        with open(filename, "rb") as file:
            while True:
                chunk = file.read(512)
                if not chunk:
                    break
                client.sendall(chunk)

    except Exception as error:
        logger.log("Download log Failure", error)