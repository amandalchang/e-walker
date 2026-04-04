import math
import time

KP_D = 1.2
KP_A = 1.8
KI_A = 0.1
KD_A = 0.05
WHEEL_DIST = 0.5  # distance between wheels in meters
MAX_W = 2.0  # max angular speed in rad/s
MAX_FORWARD_SPEED = 1.5  # max forward speed in m/s


class WalkerController:
    def __init__(self):
        # Thresholds
        self.ANGLE_TOLERANCE = 0.05  # ~3 degrees
        self.DIST_TOLERANCE = 0.05   # 5 cm

        # PID State
        self.last_error = 0
        self.integral = 0
        self.last_time = time.time()

    def _update_pid(self, error):
        """Internal helper to calculate PID output for the heading."""
        now = time.time()
        dt = now - self.last_time
        if dt <= 0:
            return 0

        # Normalize error to [-pi, pi] for shortest path
        error = math.atan2(math.sin(error), math.cos(error))

        self.integral += error * dt
        # if robot gets stuck dont add to infinity
        self.integral = max(min(self.integral, 0.5), -0.5)

        der = (error - self.last_error) / dt

        self.last_error = error
        self.last_time = now

        updated_w = (KP_A * error) + (KI_A * self.integral) + (KD_A * der)
        return max(min(updated_w, MAX_W), -MAX_W)

    def get_commands(self, azimuth, distance):
        """
        Main entry point for streaming data. 
        Logic: Pivot until aligned, then drive forward.
        """
        # arrival check
        if distance < self.DIST_TOLERANCE:
            return 0.0, 0.0

        # PIVOT STATE
        if abs(azimuth) > self.ANGLE_TOLERANCE:
            # We treat target_angle as 0 (straight ahead)
            w = self._update_pid(azimuth)
            v_l = w * (WHEEL_DIST / 2)
            v_r = -v_l
            return v_l, v_r

        # FORWARD STATE
        else:
            # Reset PID state so the next turn starts fresh
            self.integral = 0

            speed = KP_D * distance
            speed = min(speed, MAX_FORWARD_SPEED)
            return speed, speed

# Example usage for your stream:
robot = WalkerController()

# In your real-time loop:
# l_speed, r_speed = robot.get_commands(current_azimuth, current_distance)
