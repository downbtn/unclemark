#!/usr/bin/env python3
"""
Simple motor spin test - all in one file
Just run: sudo python3 motor_spin.py
"""

import RPi.GPIO as GPIO
import time

# ===== CONFIGURATION =====
# Motor 1 - Top Left
MOTOR_TL_STEP = 14
MOTOR_TL_DIR = 15
MOTOR_TL_ENABLE = 18

# Motor 2 - Top Right
MOTOR_TR_STEP = 16
MOTOR_TR_DIR = 20
MOTOR_TR_ENABLE = 21

# Speed settings
DELAY = 0.002  # seconds between steps (lower = faster)
STEPS = 800    # number of steps (800 = 4 full rotations with 200 steps/rev)

# ===== SETUP =====
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Setup all pins as outputs
GPIO.setup(MOTOR_TL_STEP, GPIO.OUT)
GPIO.setup(MOTOR_TL_DIR, GPIO.OUT)
GPIO.setup(MOTOR_TL_ENABLE, GPIO.OUT)

GPIO.setup(MOTOR_TR_STEP, GPIO.OUT)
GPIO.setup(MOTOR_TR_DIR, GPIO.OUT)
GPIO.setup(MOTOR_TR_ENABLE, GPIO.OUT)

# Enable motors - try LOW first, change to HIGH if it doesn't work
GPIO.output(MOTOR_TL_ENABLE, GPIO.LOW)
GPIO.output(MOTOR_TR_ENABLE, GPIO.LOW)

print("Motors enabled and ready")
print(f"Will spin {STEPS} steps with {DELAY}s delay between steps")
print("-" * 50)

try:
    # ===== SPIN MOTOR 1 (Top Left) =====
    print("\nSpinning Motor 1 (Top Left) clockwise...")
    GPIO.output(MOTOR_TL_DIR, GPIO.HIGH)
    
    for i in range(STEPS):
        GPIO.output(MOTOR_TL_STEP, GPIO.HIGH)
        time.sleep(DELAY)
        GPIO.output(MOTOR_TL_STEP, GPIO.LOW)
        time.sleep(DELAY)
    
    print("Motor 1 done!")
    time.sleep(1)
    
    # ===== SPIN MOTOR 2 (Top Right) =====
    print("\nSpinning Motor 2 (Top Right) clockwise...")
    GPIO.output(MOTOR_TR_DIR, GPIO.HIGH)
    
    for i in range(STEPS):
        GPIO.output(MOTOR_TR_STEP, GPIO.HIGH)
        time.sleep(DELAY)
        GPIO.output(MOTOR_TR_STEP, GPIO.LOW)
        time.sleep(DELAY)
    
    print("Motor 2 done!")
    time.sleep(1)
    
    # ===== SPIN BOTH TOGETHER =====
    print("\nSpinning BOTH motors together...")
    GPIO.output(MOTOR_TL_DIR, GPIO.HIGH)
    GPIO.output(MOTOR_TR_DIR, GPIO.HIGH)
    
    for i in range(STEPS):
        GPIO.output(MOTOR_TL_STEP, GPIO.HIGH)
        GPIO.output(MOTOR_TR_STEP, GPIO.HIGH)
        time.sleep(DELAY)
        GPIO.output(MOTOR_TL_STEP, GPIO.LOW)
        GPIO.output(MOTOR_TR_STEP, GPIO.LOW)
        time.sleep(DELAY)
    
    print("\nAll done! Motors spinning successfully!")

except KeyboardInterrupt:
    print("\n\nStopped by user (Ctrl+C)")

finally:
    print("Cleaning up GPIO...")
    GPIO.cleanup()
    print("Done!")