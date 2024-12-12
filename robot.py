import RPi.GPIO as GPIO
import time
import board
import busio
import adafruit_mcp4725

i2c = busio.I2C(board.SCL, board.SDA)
dac = adafruit_mcp4725.MCP4725(i2c, address=0x60)

statusPin = 23
gripperPin = 24
colorPin = 20
shapePin = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(statusPin, GPIO.OUT)
GPIO.setup(gripperPin, GPIO.OUT)
GPIO.setup(colorPin, GPIO.OUT)
GPIO.setup(shapePin, GPIO.OUT)
GPIO.output(statusPin, GPIO.LOW)
GPIO.output(gripperPin, GPIO.LOW)
GPIO.output(colorPin, GPIO.LOW)
GPIO.output(shapePin, GPIO.LOW)

def move(x = 0, y = 0, z = 0, pitch = 0):
	xpwm = x/4+50
	ypwm = y/4+50
	zpwm = z/8+50
	ppwm = pitch + 50
	pwmsignals = [xpwm, ypwm, zpwm, ppwm]
		
	for i in range(4):
		GPIO.output(statusPin, GPIO.HIGH) #High -> Du kriegst gleich Koordinaten
		dac_val = int(2 ** 12 * pwmsignals[i]/10)
		dac.value = dac_val
		time.sleep(0.5)
	GPIO.output(statusPin, GPIO.LOW)
	 
	time.sleep(1)
	return

def openGripper():
	GPIO.output(gripperPin, GPIO.HIGH)
	time.sleep(5)

def closeGripper():
	GPIO.output(gripperPin, GPIO.LOW)
	time.sleep(5)
	
def sendcolorandshape(color, shape):
	colors = ["rot", "gruen", "blau", "orange"]
	shapes = ["square", "rectangle", "circle", "hexagon", "octagon"]
	
	GPIO.output(colorPin, GPIO.HIGH)
	if color not in colors:
		color = -1		
		dac.value = 0
	else:
		color = colors.index(color)
		dac_val = int(2 ** 12 * (5 + color))
		dac.value = dac_val
	time.sleep(1)
	GPIO.output(colorPin, GPIO.LOW)
		
	GPIO.output(shapePin, GPIO.HIGH)
	if shape not in shapes:
		shape = -1	
		dac.value = 0
	else:
		shape = shapes.index(shape)
		dac_val = int(2 ** 12 * (5 + shape))
		dac.value = dac_val
	time.sleep(1)
	GPIO.output(shapePin, GPIO.LOW)
    
