#!/usr/bin/python
import RPi.GPIO as GPIO
from time import sleep
import sys
sys.dont_write_bytecode = True

GPIO.setmode(GPIO.BCM)
#PUMP CONTROL
GPIO.setup(12, GPIO.OUT)
#MISTER
GPIO.setup(24, GPIO.OUT)
#INLINE FAN 
GPIO.setup(23, GPIO.OUT)
#HEAT MAT
GPIO.setup(16, GPIO.OUT)
#LED LIGHT
GPIO.setup(25, GPIO.OUT)


##########MISTER##########
def mister_output(state):
    #TRUE IS ON
    GPIO.output(24, GPIO.HIGH)
    GPIO.output(24, GPIO.LOW if state else GPIO.HIGH) 

def is_mister_on():
    return GPIO.input(24) == GPIO.HIGH

def test_mister():
    mister_output(False)
    print("Turning Mister  On")
    mister_output(True)
    sleep(5)
    print("Turning fan off")
    mister_output(False)

##########INLINE FAN##########
def inline_fan_output(state):
    #TRUE IS ON
    GPIO.output(23, GPIO.HIGH)
    GPIO.output(23, GPIO.LOW if state else GPIO.HIGH)
   
def is_inline_fan_on():
    return GPIO.input(23) == GPIO.HIGH

def test_inline_fan():
    inline_fan_output(False)
    print("Turning Inline Fan On")
    inline_fan_output(True)
    sleep(5)
    print("Turning Inline Fan Off")
    inline_fan_output(False)

##########HEAT MAT##########
def heat_mat_output(state):
    GPIO.output(16, GPIO.HIGH)
    GPIO.output(16, GPIO.LOW if state else GPIO.HIGH)

def is_heat_mat_on():
    return GPIO.input(16) == GPIO.HIGH


def heat_mat_output_test():
    heat_mat_output(False)
    heat_mat_output(True)
    sleep(5)
    heat_mat_output(False)

##########PUMP CONTROL##########
def pump_output(state):
    GPIO.output(16, GPIO.HIGH if state else GPIO.LOW)

def pump_test():
    print("Turning Pump On")
    GPIO.output(16, GPIO.HIGH)
    sleep(5)
    print("Turing fan off")
    GPIO.output(16, GPIO.LOW)

def is_pump_on():
    return GPIO.input(16) == GPIO.HIGH

##########LED LIGHT##########
def is_led_on():
    return GPIO.input(25) == GPIO.LOW

def led_output(state):
    GPIO.output(25, GPIO.LOW if state else GPIO.HIGH)

def led_test():
    led_output(False)
    print("Turning Inline Fan On")
    led_output(True)
    sleep(5)
    print("Turning Inline Fan Off")
    led_output(False)

# if __name__ == "__main__":
#     try:
#         led_test()
#     except KeyboardInterrupt:
#         print("Program stopped by user")
#     finally:
#         GPIO.cleanup() # clean up GPIO on normal exit or CTRL+C
