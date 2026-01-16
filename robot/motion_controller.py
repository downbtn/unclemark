"""
motion_controller.py - Coordinated Motion for 2-Motor System

Synchronizes both motors to move the marker smoothly to target positions.
Handles coordinated movement of the two-wire suspension system.
"""

import time
import threading
from stepper_motor import StepperMotor
from kinematics import Kinematics
from config import Config
import RPi.GPIO as GPIO

class MotionController:
    def __init__(self, config: Config):
        """
        Initialize the motion control system for 2-motor setup.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.kinematics = Kinematics(config)
        
        # Setup GPIO mode
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Initialize two motors
        self.motors = {
            'tl': StepperMotor(
                config.MOTOR_TL_STEP_PIN,
                config.MOTOR_TL_DIR_PIN,
                config.MOTOR_TL_ENABLE_PIN,
                "Top-Left"
            ),
            'tr': StepperMotor(
                config.MOTOR_TR_STEP_PIN,
                config.MOTOR_TR_DIR_PIN,
                config.MOTOR_TR_ENABLE_PIN,
                "Top-Right"
            )
        }
        
        # Current position in Cartesian coordinates
        self.current_x = config.WHITEBOARD_WIDTH / 2  # Start at center
        self.current_y = config.WHITEBOARD_HEIGHT / 2
        
        # Lock for thread-safe operations
        self.lock = threading.Lock()
        
        print("Motion controller initialized (2-motor system)")
        print(f"Starting position: ({self.current_x:.1f}, {self.current_y:.1f})")
        
    def enable_all_motors(self):
        """Enable both motors"""
        for motor in self.motors.values():
            motor.enable()
            
    def disable_all_motors(self):
        """Disable both motors"""
        for motor in self.motors.values():
            motor.disable()
    
    def move_to(self, x, y, speed=None):
        """
        Move marker to absolute position (x, y).
        
        Args:
            x: Target x coordinate in mm
            y: Target y coordinate in mm
            speed: Movement speed in steps/sec (uses config default if None)
        """
        if not self.kinematics.validate_position(x, y):
            print(f"Warning: Position ({x}, {y}) is outside whiteboard bounds")
            return False
        
        if speed is None:
            speed = self.config.MAX_SPEED
        
        with self.lock:
            # Calculate required step changes for each motor
            delta_steps = self.kinematics.calculate_delta_steps(
                self.current_x, self.current_y, x, y
            )
            
            print(f"Moving from ({self.current_x:.2f}, {self.current_y:.2f}) "
                  f"to ({x:.2f}, {y:.2f})")
            print(f"Delta steps - TL: {delta_steps['tl']}, TR: {delta_steps['tr']}")
            
            # Execute coordinated movement
            self._execute_coordinated_move(delta_steps, speed)
            
            # Update current position
            self.current_x = x
            self.current_y = y
            
        return True
    
    def _execute_coordinated_move(self, delta_steps, speed):
        """
        Execute a coordinated move where both motors finish simultaneously.
        
        This ensures the marker travels in a straight line between points.
        Both motors must move in perfect sync.
        
        Args:
            delta_steps: Dict of step changes {'tl': steps, 'tr': steps}
            speed: Maximum speed in steps/sec
        """
        # Find motor that needs to move the most steps
        max_steps = max(abs(delta_steps['tl']), abs(delta_steps['tr']))
        
        if max_steps == 0:
            return
        
        # Enable both motors
        self.enable_all_motors()
        
        # Calculate speed for each motor to finish at same time
        motor_speeds = {}
        for motor_name, steps in delta_steps.items():
            if steps == 0:
                motor_speeds[motor_name] = 0
            else:
                # Scale speed proportionally
                motor_speeds[motor_name] = int(abs(steps) / max_steps * speed)
        
        # Set directions for both motors
        for motor_name, steps in delta_steps.items():
            if steps != 0:
                self.motors[motor_name].set_direction(steps > 0)
        
        # Calculate step timing
        base_delay = 1.0 / (2 * speed)  # For the fastest motor
        
        # Perform coordinated stepping
        steps_remaining = {
            'tl': abs(delta_steps['tl']),
            'tr': abs(delta_steps['tr'])
        }
        
        while steps_remaining['tl'] > 0 or steps_remaining['tr'] > 0:
            for motor_name, motor in self.motors.items():
                if steps_remaining[motor_name] > 0:
                    # Calculate this motor's delay
                    if motor_speeds[motor_name] > 0:
                        delay = 1.0 / (2 * motor_speeds[motor_name])
                    else:
                        continue
                    
                    motor.step_once(delay)
                    steps_remaining[motor_name] -= 1
                    motor.position += 1 if delta_steps[motor_name] > 0 else -1
            
            # Small delay to prevent overwhelming the system
            time.sleep(0.00001)
    
    def draw_line(self, x1, y1, x2, y2, steps=50):
        """
        Draw a straight line by interpolating between two points.
        
        Args:
            x1, y1: Start point
            x2, y2: End point
            steps: Number of interpolation steps
        """
        print(f"Drawing line from ({x1}, {y1}) to ({x2}, {y2})")
        
        # Generate intermediate points
        for i in range(steps + 1):
            t = i / steps
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            self.move_to(x, y)
    
    def execute_path(self, positions):
        """
        Execute a sequence of positions.
        
        Args:
            positions: List of (x, y) tuples in mm
        """
        print(f"Executing path with {len(positions)} positions")
        
        for i, (x, y) in enumerate(positions):
            print(f"Point {i+1}/{len(positions)}: ({x}, {y})")
            self.move_to(x, y)
            time.sleep(0.05)  # Small pause between points
    
    def home(self):
        """
        Home the system - move to center of whiteboard.
        """
        center_x = self.config.WHITEBOARD_WIDTH / 2
        center_y = self.config.WHITEBOARD_HEIGHT / 2
        
        print(f"Homing to center: ({center_x}, {center_y})")
        self.move_to(center_x, center_y)
        
    def cleanup(self):
        """Clean up GPIO and disable motors"""
        print("Cleaning up motion controller...")
        self.disable_all_motors()
        for motor in self.motors.values():
            motor.cleanup()
        GPIO.cleanup()