#!/usr/bin/env python
# This code makes the stepper motor turn
# Version Dec 29, KeyaLea
# It is connected to an EasyDriver controller receiving external power
# EasyDriver has three wires - lower right corner connecting to gpio
# blue GND, to pin 14 on pi
# green STEP, to pin 16
# yellow DIR, to pin 18
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(16, GPIO.OUT) #16 goes to stepmotor
GPIO.setup(18, GPIO.OUT) #18 for direction
#set up pulse rate modulation object for pulses for 16
p = GPIO.PWM(16,500) #500Hz
def SpinMotor(direction, number_steps):
	GPIO.output(18, direction)
	while number_steps > 0:
		p.start(1)
		time.sleep(0.02) # change impacts rotation .02 175 full rotation
# or if value .01, then 350 steps for full rotation
		number_steps -= 1
	p.stop()
	GPIO.cleanup()
	return True

direction_input = raw_input('Please enter CW for Clockwise or CC for CounterClockwise: ')
number_steps = input('Please enter the number of steps: ')
if direction_input == 'CW':
	SpinMotor(False, number_steps)
else:
	SpinMotor(True, number_steps)


