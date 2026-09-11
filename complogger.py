from logger import Logger

class CompressorLogger(Logger):
    def __init__(self):
        super().__init__(
            max_entries = 100,
            filename = "CompressorLog.txt",
            separator = "\n___Compressor Cycle___\n"
        )


    def log(self, state, duration,
            airtemp, incoil, outcoil):

        # Convert milliseconds into an HH:MM:SS duration
        duration = self.format_duration(duration)
        if state == "ON":
            duration_state = "OFF"
        elif state == "OFF":
            duration_state = "ON"
        else:
            duration_state = "Bad state input"

        message = (
            "Compressor {} | {} Duration: {} | "
            "Air: {} | Indoor Coil: {} | "
            "Outdoor Coil: {}"
        ).format(state, duration_state, duration,
                 airtemp, incoil, outcoil)

        super().log(message)


    def format_duration(self, duration_ms):
        total_seconds = duration_ms // 1000

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        return"{:02d}:{:02d}:{:02d}".format(
            hours, minutes, seconds)
        

comp_logger = CompressorLogger()