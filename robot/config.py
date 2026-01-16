"""
config.py - Whiteboard Bot Configuration

This file contains all the physical parameters of your whiteboard setup.
Modify these values to match the hardware/physical setup.
"""

class Config:
    # Physical size of whiteboard, in milimeters
    WHITEBOARD_WIDTH = 1200.0   # mm
    WHITEBOARD_HEIGHT = 900.0   # mm
    
    # Stepper Motor Specs
    STEPS_PER_REVOLUTION = 200  # Standard NEMA 17: 200 (1.8° per step)
    MICROSTEPS = 16              # Set on your driver (A4988/TMC2208)
    
    SPOOL_DIAMETER = 20.0  # mm - ACCURATE MEASUREMENT NEEDED
    
    # GPIO Pins
    
    # Motor 1 - Top Left Corner Reel
    MOTOR_TL_STEP_PIN = 14
    MOTOR_TL_DIR_PIN = 15
    MOTOR_TL_ENABLE_PIN = 18
    
    # Motor 2 - Top Right Corner Reel
    MOTOR_TR_STEP_PIN = 16
    MOTOR_TR_DIR_PIN = 20
    MOTOR_TR_ENABLE_PIN = 21
    
    # Motion Parameters
    MAX_SPEED = 2000  # steps per second
    ACCELERATION = 1000  # steps per second^2
    
    # Calculations
    @property # adds getters and setters
    def steps_per_mm(self):
        """Calculate steps needed to move 1mm of wire"""
        import math
        circumference = math.pi * self.SPOOL_DIAMETER
        total_steps_per_rev = self.STEPS_PER_REVOLUTION * self.MICROSTEPS
        return total_steps_per_rev / circumference