import logging
import serial
from time import sleep, time
from typing import Optional, Type, TracebackType

class SerialCommunicator:
    def __init__(self, port: str, baud_rate: int, timeout: float, logger: logging.Logger):
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.logger = logger
        self.ser: Optional[serial.Serial] = None

    def connect(self, retries: int = 3, delay: float = 2) -> bool:
        for attempt in range(1, retries + 1):
            try:
                self.ser = serial.Serial(
                    self.port, self.baud_rate, timeout=self.timeout
                )
                if self.ser.is_open:
                    self.logger.info(
                        "Connected to %s at %d baud.", self.port, self.baud_rate
                    )
                    return True
            except serial.SerialException as e:
                self.logger.warning(
                    "Connection failed (port:%s, baud_rate:%d attempt:%d). Retrying...",
                    self.port,
                    self.baud_rate,
                    attempt,
                )
                self.logger.debug(str(e))
                sleep(delay)
        # Raise ConnectionError if all retries fail
        raise ConnectionError(
            f"Failed to connect to {self.port} after {retries} attempts."
        )

    def read_line(self) -> Optional[str]:
        reading = self._read_raw_line()
        if reading == "OK": # Assuming "OK" is an acknowledgement, read next line for actual data
            reading = self._read_raw_line()
        self.logger.debug("Received: %s", reading)
        return reading

    def write_line(self, string: str) -> bool:
        if not self.is_open() or self.ser is None:
            return False
        try:
            self.flush_input()
            self.ser.write(string.encode())
            sleep(0.1) # Give device time to process
            self.logger.debug("<< %s", string)
            # Optional: Check for an "OK" or ack response if your device sends one
            # For now, assume write is successful if no exception
            return True
        except serial.SerialException as e:
            self.logger.error("Error while writing", exc_info=e)
            return False

    def flush_input(self) -> None:
        if self.is_open() and self.ser is not None:
            self.logger.debug("Flushing input buffer...")
            self.ser.reset_input_buffer()

    def close_connection(self) -> None:
        if self.is_open() and self.ser is not None:
            self.ser.close()
            self.logger.info("Serial connection closed.")

    def _read_raw_line(self) -> Optional[str]:
        if not self.is_open() or self.ser is None:
            return None
        try:
            line = self.ser.readline().decode().strip()
            return line
        except serial.SerialException as e:
            self.logger.error("Read error", exc_info=e)
            return None
        except UnicodeDecodeError as e:
            self.logger.error("Unicode decode error on read", exc_info=e)
            return None


    def wait_for_ready(self, ready_signal: str = "READY", timeout_seconds: float = 10.0) -> bool:
        self.flush_input()
        if not self.is_open() or self.ser is None:
            return False

        start_time = time.time()
        while (time.time() - start_time) < timeout_seconds:
            line = self._read_raw_line() # Use _read_raw_line to avoid ack processing
            if line == ready_signal:
                self.logger.info("Device is READY.")
                self.flush_input() # Flush again after ready signal
                return True
            sleep(0.1) # Short sleep to prevent busy-waiting

        self.logger.warning(f"Timeout waiting for '{ready_signal}' signal.")
        return False

    def is_open(self) -> bool:
        if not self.ser or not self.ser.is_open:
            # self.logger.error("Serial port is not open.") # This can be too noisy
            return False
        return True

    def __enter__(self):
        self.connect()
        # self.wait_for_ready() # Consider if wait_for_ready should always be here or called explicitly
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self.close_connection()
