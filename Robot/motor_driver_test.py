import RPi.GPIO as gpio
import time

def init():
    gpio.setmode(gpio.BCM)
    gpio.setup(17, gpio.OUT)
    gpio.setup(22, gpio.OUT)
    gpio.setup(23, gpio.OUT)
    gpio.setup(24, gpio.OUT)
    gpio.setup(12, gpio.OUT) #PWM0
    gpio.setup(13, gpio.OUT) #PWM1
    

def backward(sec):
    init()
    pwm0 = gpio.PWM(12, 1000)
    pwm1 = gpio.PWM(13, 1000)
    gpio.output(17, True)
    gpio.output(22, False)
    gpio.output(23, True) 
    gpio.output(24, False)
    pwm0.start(50)
    pwm1.start(50)
    time.sleep(sec)
    gpio.cleanup()
 
def left(sec):
    init()
    pwm0 = gpio.PWM(12, 1000)
    pwm1 = gpio.PWM(13, 1000)
    gpio.output(17, False)
    gpio.output(22, True)
    gpio.output(23, True) 
    gpio.output(24, False)
    pwm0.start(50)
    pwm1.start(50)
    time.sleep(sec)
    gpio.cleanup()
    
def right(sec):
    init()
    pwm0 = gpio.PWM(12, 1000)
    pwm1 = gpio.PWM(13, 1000)
    gpio.output(17, True)
    gpio.output(22, False)
    gpio.output(23, False) 
    gpio.output(24, True)
    pwm0.start(50)
    pwm1.start(50)
    time.sleep(sec)
    gpio.cleanup()

def forward(sec):
    init()
    pwm0 = gpio.PWM(12, 1000)
    pwm1 = gpio.PWM(13, 1000)
    gpio.output(17, False)
    gpio.output(22, True)
    gpio.output(23, False) 
    gpio.output(24, True)
    pwm0.start(50)
    pwm1.start(50)
    time.sleep(sec)
    gpio.cleanup()
 
print("forward")
forward(10)
print("reverse")
backward(10)
print("right")
right(10)
print("left")
left(10)
