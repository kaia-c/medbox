#!/user/bin/env python
# Combining two working files: rfid.py and stepmotor.py to rfid_step.py
# Reads the card and if it is recognized, will go onto next step (haha)
# Version Jan 5, 2015, klh 
#Version 2 1/9/15, kmc, net
import serial, time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(16, GPIO.OUT) #16 goes to stepmotor
GPIO.setup(18, GPIO.OUT) #18 for direction

#set up pulse rate modulation object for pulses for 16
p = GPIO.PWM(16,500) #500Hz
def SpinMotor(direction, number_steps):
	GPIO.output(18, direction)
	while number_steps > 0:
		p.start(1)
		time.sleep(0.01) # change impacts rotation .02 175 full rotation
# or if value .01, then 350 steps for full rotation
		number_steps -= 1
	p.stop()
	return True

# I realize that adding cards in elif statements not the best way to code
# cards = ['6A004A16C0', '6A0049F913']
# rfid reader 
ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=0.5)
rfidStr=['6A0049F913', '6A004A16C0', '770096EE82', '77009700B7', '770096CD0B']
try:
	while True:
		worked = False
		string = ser.read(12)
		string = string[1:11]
		if string in rfidStr:
			worked = SpinMotor(True, 350)
		print(worked)
except KeyboardInterrupt:
	pass
finally:
	GPIO.cleanup()