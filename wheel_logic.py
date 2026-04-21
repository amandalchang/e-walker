import math
import time

L = 0.5  # distance btwn back wheels in m
MAX_W = 2.0  # fastest angular vel
KP = 1.5  # p gain

def get_pivot_speeds(target_azimuth, distance):
    """
    Calculates wheel speeds to pivot toward a target azimuth.
    'target_azimuth' should be the relative angle to the target in radians.
    """

    error = math.atan2(math.sin(target_azimuth), math.cos(target_azimuth))

    if distance < 0.05: #you're really close
        return 0.0, 0.0

    w = KP * error

    # speed cap
    w = max(min(w, MAX_W), -MAX_W)

    v_l = w * (L / 2)
    v_r = -v_l  # Opposite directions for a pure pivot
    return v_l, v_r

# If the target is 45 degrees (pi/4) to the right 
l_speed, r_speed = get_pivot_speeds(math.pi/2, 1.0)
print(f"Left Wheel: {l_speed:.2f} m/s, Right Wheel: {r_speed:.2f} m/s")

def go_forward(distance):
    """
    Calculates wheel speeds to move forward a certain distance.
    'distance' should be the distance to the target in meters.
    """

    if distance < 0.05: #you're really close
        return 0.0, 0.0

    # Simple proportional control for forward movement
    speed = KP * distance

    # speed cap
    speed = max(min(speed, MAX_W), -MAX_W)

    return speed, speed 

class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        
        self.last_error = 0
        self.integral = 0
        self.last_time = time.time()

    def update(self, target_angle, current_angle):
        now = time.time()
        dt = now - self.last_time
        if dt <= 0: return 0 # Prevent division by zero
        
        # 1. Calculate Shortest Path Error (Normalize to [-pi, pi])
        error = target_angle - current_angle
        error = math.atan2(math.sin(error), math.cos(error))
        
        # 2. Integral term (sum of errors over time)
        self.integral += error * dt
        
        # 3. Derivative term (rate of change of error)
        derivative = (error - self.last_error) / dt
        
        # 4. Compute Output
        output = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)
        
        # Save state for next iteration
        self.last_error = error
        self.last_time = now
        
        return output

# --- Setup for your robot ---
L = 0.5  # Wheel track width
azimuth_pid = PIDController(kp=1.8, ki=0.1, kd=0.05)

def stream_wheel_speeds(azimuth_data, distance_data):
    """
    In a pivot, azimuth_data is essentially our 'current_angle' error 
    if we treat 0.0 as the 'straight ahead' target.
    """
    # We want azimuth to be 0 (facing the target)
    angular_velocity = azimuth_pid.update(target_angle=0, current_angle=azimuth_data)
    
    # Differential drive pivot kinematics
    v_r = angular_velocity * (L / 2)
    v_l = -v_r
    
    return v_l, v_r
