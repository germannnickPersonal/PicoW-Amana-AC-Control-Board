import time

class Logger:

    def __init__(self, max_entries = 50,
                filename = "",
                 separator = "\n___LOG___\n" 
                 ):
        self.max_entries = max_entries
        self.filename = filename
        self.separator = separator

    def log(self, message):
        try:
            # Read any existing log entries
            try:
                with open(self.filename, "r") as file:
                    contents = file.read()
            except OSError:
                contents = ""

            # Split and clean the existing entries
            
            if contents:
                raw_data = contents.split(self.separator)
                clean_data = []
                for data in raw_data:
                    data = data.strip()
                    if data:
                        clean_data.append(data)
                entries = clean_data
            else:
                entries = []

            entries.append(
                "[{}] {}\n".format(
                self.get_timestamp(),
                message)
            )

            if len(entries) >= self.max_entries:
                entries = entries[-self.max_entries:]

            with open(self.filename, "w") as file:
                for i, entry in enumerate(entries):
                    if i > 0:
                        file.write(self.separator)
                    file.write(entry)
                    
        except Exception:
            # Logging failures must not crash the controller
            pass

    def get_timestamp(self):
        utc_seconds = time.time()

        # Apply a fixed UTC-6 offset for CST timestamps.
        # Adjust this offset for another local timezone as needed.
        # This fixed offset does not automatically account for daylight saving time.
        cst_seconds = utc_seconds - (6 * 60 * 60)

        timestamp = time.localtime(cst_seconds)
        formatted = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
            timestamp[0],
            timestamp[1],
            timestamp[2],
            timestamp[3],
            timestamp[4],
            timestamp[5]
        )

        return formatted