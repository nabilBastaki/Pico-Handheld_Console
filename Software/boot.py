from machine import Pin, Timer
import utime
led = Pin("LED", Pin.OUT)
timer = Timer()

def ledblink(timer):
    led.toggle()
    
timer.init(freq=1, mode=Timer.PERIODIC, callback=ledblink)
