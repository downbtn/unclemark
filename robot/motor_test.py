#!/usr/bin/env python3
"""
motor_test.py - Simple motor test script for Whiteboard Bot

Tests both motors by spinning them in both directions.
Run this to verify your wiring and motor functionality.

Usage:
    sudo python3 motor_test.py
"""

import RPi.GPIO as GPIO
import time
from config import Config

def setup_gpio():
    """Initialize GPIO pins"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    cfg = Config()
    
    # Setup Motor 1 (Top Left)
    GPIO.setup(cfg.MOTOR_TL_STEP_PIN, GPIO.OUT)
    GPIO.setup(cfg.MOTOR_TL_DIR_PIN, GPIO.OUT)
    GPIO.setup(cfg.MOTOR_TL_ENABLE_PIN, GPIO.OUT)
    
    # Setup Motor 2 (Top Right)
    GPIO.setup(cfg.MOTOR_TR_STEP_PIN, GPIO.OUT)
    GPIO.setup(cfg.MOTOR_TR_DIR_PIN, GPIO.OUT)
    GPIO.setup(cfg.MOTOR_TR_ENABLE_PIN, GPIO.OUT)
    
    # Enable both motors (LOW = enabled for most drivers)
    GPIO.output(cfg.MOTOR_TL_ENABLE_PIN, GPIO.LOW)
    GPIO.output(cfg.MOTOR_TR_ENABLE_PIN, GPIO.LOW)
    
    print("GPIO setup complete")
    return cfg

def step_motor(step_pin, num_steps, delay=0.001):
    """
    Send step pulses to a motor
    
    Args:
        step_pin: GPIO pin for step signal
        num_steps: Number of steps to take
        delay: Delay between steps (seconds)
    """
    for _ in range(num_steps):
        GPIO.output(step_pin, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(step_pin, GPIO.LOW)
        time.sleep(delay)

def test_motor(name, step_pin, dir_pin, steps=400, delay=0.001):
    """
    Test a single motor in both directions
    
    Args:
        name: Motor name for display
        step_pin: GPIO pin for step signal
        dir_pin: GPIO pin for direction signal
        steps: Number of steps per direction
        delay: Delay between steps
    """
    print(f"\n=== Testing {name} ===")
    
    # Spin clockwise
    print(f"Spinning {name} clockwise ({steps} steps)...")
    GPIO.output(dir_pin, GPIO.HIGH)
    step_motor(step_pin, steps, delay)
    time.sleep(0.5)
    
    # Spin counter-clockwise
    print(f"Spinning {name} counter-clockwise ({steps} steps)...")
    GPIO.output(dir_pin, GPIO.LOW)
    step_motor(step_pin, steps, delay)
    time.sleep(0.5)
    
    print(f"{name} test complete")

def test_both_motors_simultaneous(cfg, steps=400, delay=0.001):
    """Test both motors spinning at the same time"""
    print(f"\n=== Testing Both Motors Simultaneously ===")
    print(f"Spinning both motors ({steps} steps)...")
    
    # Set both motors to same direction
    GPIO.output(cfg.MOTOR_TL_DIR_PIN, GPIO.HIGH)
    GPIO.output(cfg.MOTOR_TR_DIR_PIN, GPIO.HIGH)
    
    # Step both motors together
    for _ in range(steps):
        GPIO.output(cfg.MOTOR_TL_STEP_PIN, GPIO.HIGH)
        GPIO.output(cfg.MOTOR_TR_STEP_PIN, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(cfg.MOTOR_TL_STEP_PIN, GPIO.LOW)
        GPIO.output(cfg.MOTOR_TR_STEP_PIN, GPIO.LOW)
        time.sleep(delay)
    
    print("Simultaneous test complete")

def main():
    """Main test sequence"""
    print("=" * 50)
    print("Whiteboard Bot - Motor Test Script")
    print("=" * 50)
    
    try:
        # Setup
        cfg = setup_gpio()
        
        # Test individual motors
        test_motor(
            "Motor TL (Top Left)",
            cfg.MOTOR_TL_STEP_PIN,
            cfg.MOTOR_TL_DIR_PIN,
            steps=400,  # 1 full revolution with 200 steps/rev
            delay=0.001  # 1ms delay = moderate speed
        )
        
        test_motor(
            "Motor TR (Top Right)",
            cfg.MOTOR_TR_STEP_PIN,
            cfg.MOTOR_TR_DIR_PIN,
            steps=400,
            delay=0.001
        )
        
        # Test both motors together
        test_both_motors_simultaneous(cfg, steps=400, delay=0.001)
        
        print("\n" + "=" * 50)
        print("All tests complete!")
        print("=" * 50)
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    
    except Exception as e:
        print(f"\n\nError occurred: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Disable motors and cleanup
        print("\nCleaning up GPIO...")
        GPIO.cleanup()
        print("Done!")

if __name__ == "__main__":
    main()