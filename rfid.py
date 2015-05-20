#!/user/bin/env python
# This set up is using the ID-20LA RFID Reader, using a SparkFun RFID
#  Reader Breakout, connected to a Rasp Pi B+.  
# Freed up the UART_RXD pin by editing /etc/inittab and /boot/cmdline.txt,
#  tested with minicom. 
# It is being powered by the 3.3V rail VCC yellow to p1, D0 blue to p10UART_RXD,
#  FORM purple to p9, GND black to p6 and RES green to p13.
# Version Jan 5, 2015, klh
# It reads an RFID card and outputs the string so we can see it.
import serial, time
ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=0.5)
try:
	while True:
		string = ser.read(12)
		if len(string) == 0:
			continue
		else:
			string = string[1:11]
			print string
		if string == '6A0049F913':
			print("Here's some medicine for you\n")
			time.sleep(1)
			print("Actually, this is where the stepper motor turns to dispense.")
except KeyboardInterrupt:
	pass
