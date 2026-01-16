#!/usr/bin/env python3
"""
TMC2209 Diagnostic Test
"""

import RPi.GPIO as GPIO
import time

MOTOR_TL_STEP = 14
MOTOR_TL_DIR = 15

print("=" * 70)
print("TMC2209 DIAGNOSTIC TEST")
print("=" * 70)

input("\nPress ENTER to start test...")

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(MOTOR_TL_STEP, GPIO.OUT)
GPIO.setup(MOTOR_TL_DIR, GPIO.OUT)

print("\n" + "=" * 70)
print("TEST 1: GPIO Signal Verification")
print("=" * 70)
print("\nWatch for yellow STEP LED on driver board")
print("Sending 100 slow pulses (5 per second)...\n")

GPIO.output(MOTOR_TL_DIR, GPIO.HIGH)
time.sleep(0.5)

for i in range(100):
    print(f"Step {i+1}/100", end="\r")
    GPIO.output(MOTOR_TL_STEP, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(MOTOR_TL_STEP, GPIO.LOW)
    time.sleep(0.1)

print("\n\n" + "=" * 70)
response = input("Did yellow STEP LED blink? (y/n): ")
print("=" * 70)

if response.lower() != 'y':
    print("\nYellow LED not blinking - check connections:")
    print("- STEP wire: Pi GPIO 14 to Driver STEP pin")
    print("- VDD: Pi 5V to Driver VDD")
    print("- GND: Pi GND to Driver GND")
    GPIO.cleanup()
    exit()

print("\nGPIO signals working correctly")
time.sleep(1)

print("\n" + "=" * 70)
print("TEST 2: Motor Response")
print("=" * 70)
print("\nSending 400 steps at moderate speed...")
print("Listen and watch for any motor response\n")

GPIO.output(MOTOR_TL_DIR, GPIO.HIGH)

for i in range(400):
    GPIO.output(MOTOR_TL_STEP, GPIO.HIGH)
    time.sleep(0.005)
    GPIO.output(MOTOR_TL_STEP, GPIO.LOW)
    time.sleep(0.005)


GPIO.cleanup()
print("\nTest complete")