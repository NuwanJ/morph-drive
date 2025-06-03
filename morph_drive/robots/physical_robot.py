import logging
from abc import abstractmethod
from time import sleep # Keep this if used by PhyRobot logic not moved to SerialCommunicator
from types import TracebackType
from typing import Any, List, Optional, Type

import gymnasium
import numpy as np
# Remove direct serial import if all serial ops are in SerialCommunicator
# import serial

from . import RobotInterface
from .serial_communicator import SerialCommunicator # Added import

# TODO separate the serial communication logic into a separate class and inherit - This is now done
class PhyRobot(RobotInterface):
    """
    Implementation of RobotInterface for a real serial-based robot.
    Uses the SerialCommunicator class to handle serial communication.
    """

    metadata = {"render_modes": ["human"], 'render_fps': 30}

    observation_space: gymnasium.spaces.Space
    action_space: gymnasium.spaces.Space

    def __init__(
        self,
        robot_name: str = "SimRobot",
        observation_space: gymnasium.spaces.Space | None = None,
        action_space: gymnasium.spaces.Space | None = None,
        configs: dict[str, Any] | None = None,
    ):
        super().__init__()

        if configs is None:
            configs = {}

        # SerialCommunicator will handle port, baud_rate, timeout
        # self.port = str(configs.get("port", "/dev/ttyUSB0"))
        # self.baud_rate = int(configs.get("baud_rate", 115200))
        # self.timeout = float(configs.get("timeout", 1.0))
        self.logger = logging.getLogger(__name__)
        self.debug = bool(configs.get("debug", False)) # Keep if PhyRobot uses it directly

        # Create SerialCommunicator instance
        self.comm = SerialCommunicator(
            port=str(configs.get("port", "/dev/ttyUSB0")),
            baud_rate=int(configs.get("baud_rate", 115200)),
            timeout=float(configs.get("timeout", 1.0)),
            logger=self.logger,
        )

        self.robot_name = robot_name

        if observation_space is None:
            raise ValueError("Observation space must be provided.")

        if action_space is None:
            raise ValueError("Action space must be provided.")

        self.observation_space = observation_space
        self.action_space = action_space

        # self.ser: Optional[serial.Serial] = None # Moved to SerialCommunicator
        # self._connect() # Connection handled by SerialCommunicator's __enter__ or explicit call

        self.position: list[int] = []

        if configs.get("init_position"):
            init_position = configs.get("init_position")
            if isinstance(init_position, (list, tuple)):
                self.position = [int(v) for v in init_position]
            else:
                raise ValueError("Invalid type for 'init_position'. Expected list, or tuple.")
        else:
            if self.action_space and hasattr(self.action_space, 'shape'):
                self.position = [0] * self.action_space.shape[0]  # type: ignore
            else:
                raise ValueError("Action space must be properly initialized with a valid shape.")

    def get_observation_space(self) -> gymnasium.spaces.Space:
        return self.observation_space

    def get_action_space(self) -> gymnasium.spaces.Space:
        return self.action_space

    def get_observation(self):
        """
        Get the current observation from the robot's sensors.
        Handles potential errors during sensor reading.
        """
        try:
            sensor_values = self.get_sensor_readings()
            if sensor_values is None:
                self.logger.warning("Received None from get_sensor_readings(). Defaulting observation.")
                yaw_deg, pitch_deg, roll_deg = 0.0, 0.0, 0.0
            else:
                # Assuming get_sensor_readings() returns a tuple/list of 3 numbers
                if len(sensor_values) == 3:
                    yaw_deg, pitch_deg, roll_deg = float(sensor_values[0]), float(sensor_values[1]), float(sensor_values[2])
                else:
                    self.logger.warning(f"Received malformed sensor_readings (length {len(sensor_values)}): {sensor_values}. Defaulting observation.")
                    yaw_deg, pitch_deg, roll_deg = 0.0, 0.0, 0.0
        except Exception as e:
            self.logger.error(f"Error getting or parsing sensor readings: {e}. Defaulting observation.")
            yaw_deg, pitch_deg, roll_deg = 0.0, 0.0, 0.0

        obs = np.array([yaw_deg, pitch_deg, roll_deg], dtype=np.float32)

        # Store the last observation
        self._last_obs = obs

        return obs

    def apply_action(self, action: Any) -> None:
        actuator_values: List = self.set_action_values(action)  # type: ignore
        actuator_cmd = " ".join(str(v) for v in actuator_values)
        # Use SerialCommunicator to write
        if self.comm.write_line(f"W {actuator_cmd}\n"):
            attempts = 0
            max_attempts = 10
            # Use SerialCommunicator to read, _read_raw_line equivalent
            while self.comm._read_raw_line() == "OK" and attempts < max_attempts: # Assuming direct access for now, or add specific method
                sleep(0.1) # Consider if this sleep is still needed with SerialCommunicator's sleep
                attempts += 1
            if attempts >= max_attempts:
                self.logger.warning("Exceeded maximum attempts while waiting for response to W %s", actuator_cmd)
        else:
            self.logger.error("Failed to write action command: W %s", actuator_cmd)

        self.render()

    def render(self) -> None:
        """
        Render the robot's current state by printing its name and actuator values.
        """
        try:
            actuator_values = self.get_actuator_values()
            print(f"[{self.robot_name}] Actuator Values: {actuator_values}")
        except Exception as e:
            self.logger.error(f"Error getting actuator values for rendering: {e}")
            print(f"[{self.robot_name}] Actuator Values: Error retrieving values")

    def close(self) -> None:
        self.comm.close_connection() # Use SerialCommunicator

    def reset(self, *, seed=None, options=None):
        actuator_values: List = self.reset_action_values()  # type: ignore
        actuator_cmd = " ".join(str(v) for v in actuator_values)
        # Use SerialCommunicator to write
        self.comm.write_line(f"W {actuator_cmd}\n")
        # Potentially wait for ack or ready signal if applicable after reset
        return self.get_observation(), {}

    @abstractmethod
    def get_actuator_values(self):
        pass

    @abstractmethod
    def set_action_values(self, servo_angles):
        pass

    def reset_action_values(self):
        return self.action_space.sample()

    @abstractmethod
    def get_sensor_readings(self):
        # This method will now use self.comm.read_line() or self.comm.write_line()
        # if commands need to be sent to get readings.
        # Example:
        # self.comm.write_line("GET_SENSORS\n")
        # response = self.comm.read_line()
        # parse response
        pass

    # Methods to be removed as they are now in SerialCommunicator:
    # _connect, read, write, _flush_input, _close, _read_raw, _wait_for_ready, _is_serial_open

    def __enter__(self):
        self.comm.connect() # Use SerialCommunicator's connect
        # self.reset() # Reset might involve communication, ensure comm is up
        # Consider if wait_for_ready is needed here, it's also in comm.__enter__ if used as context manager
        # If PhyRobot needs specific ready signal:
        if not self.comm.wait_for_ready("ROBOT_READY_SIGNAL"): # Example signal
             self.logger.warning("Robot did not signal ready after connect in __enter__.")
        self.reset() # Call reset after connection and ready.
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self.comm.close_connection() # Use SerialCommunicator

    def __del__(self) -> None:
        # Ensure connection is closed if __exit__ wasn't called (e.g. error in __init__)
        if hasattr(self, 'comm'): # Check if comm was initialized
            self.comm.close_connection()


# ----------------------------------
# def reset(self) -> None:
#     """
#     Reset the robot to the default position (as defined in Robot.reset_position).
#     """
#     if self.robot is None:
#         return

#     # Reset servos to initial positions (Robot.reset sends servos to reset_position and returns those angles)
#     initial_angles = self.robot.reset()  # e.g., [65, 65, 65]
#     self._m1_angle, self._m2_angle, self._m3_angle = initial_angles

#     # Allow time for the robot to reach the position and stabilize
#     time.sleep(1.0)

#     # Flush any buffered input data from the robot
#     self.robot.flush_input()

# def apply_action(self, action: Any) -> None:
#     """
#     Apply a discrete action to the robot by adjusting servo angles.
#     """

#     # Ensure action has three components
#     try:
#         a0, a1, a2 = action
#     except Exception as e:
#         raise ValueError(
#             "Action must be an iterable of three values (for 3 servos)."
#         ) from e

#     # Map each discrete value {0,1,2} to an increment {-1,0,+1}
#     increments = [int(val) - 1 for val in (a0, a1, a2)]

#     # Define servo step size in degrees for each increment unit
#     servo_step = (
#         -3
#     )  # using a negative step so that 0->+1 increment, 2->-1 increment (per design choice)

#     # Update each servo angle and clamp within safe bounds [45, 110] degrees
#     self._m1_angle = int(
#         np.clip(self._m1_angle + increments[0] * servo_step, 45, 110)
#     )
#     self._m2_angle = int(
#         np.clip(self._m2_angle + increments[1] * servo_step, 45, 110)
#     )
#     self._m3_angle = int(
#         np.clip(self._m3_angle + increments[2] * servo_step, 45, 110)
#     )

#     # Send the movement command to the physical robot
#     # (non-blocking or blocking until move complete as implemented in Robot)
#     self.robot.send_movement(self._m1_angle, self._m2_angle, self._m3_angle)

#     # TODO handle this

#     # # Store the returns from the step
#     # self._last_obs = obs
#     # self._reward = reward
#     # self._done = done
#     # self._truncated = truncated
#     # self._info = info

# def get_sensor_data(self) -> str | None:
#     """
#     Retrieve raw sensor readings from the robot (e.g., yaw, pitch, roll angles as a comma-separated string).
#     """
#     if self.robot is None:
#         return None

#     # Send command to retrieve orientation data (assuming "C2" triggers the robot to respond with yaw,pitch,roll)
#     return self.robot.send_command_return_response("C2")

# def close(self) -> None:
#     """
#     Close the connection to the robot.
#     """
#     if self.robot:
#         self.robot.close()

# def render(self) -> None:
#     """
#     For a real robot, print the current servo angles as a simple form of feedback.
#     """
#     print(
#         f"[Robot] Servo angles: M1={self._m1_angle}, M2={self._m2_angle}, M3={self._m3_angle}"
#     )


# def send_command_return_response(self, command: str) -> Optional[str]:
#     """Send a command and return the response."""
#     self.write(f"{command}\n")
#     return self.read()

# def send_movement(self, value_1: int, value_2: int, value_3: int) -> None:
#     """Send a movement command."""
#     self.write(f"W {value_1} {value_2} {value_3}\n")
#     while self._read_raw() == "OK":
#         sleep(0.1)
#         sleep(0.1)
#         sleep(0.1)
