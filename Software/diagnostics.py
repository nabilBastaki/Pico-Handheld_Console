import machine, time
from machine import Pin, ADC, PWM
from ili9341 import Display

# --- 1. HARDWARE ---
spi = machine.SPI(0, baudrate=24000000, mosi=Pin(19), sck=Pin(18))

# PCB MOSFET GATE (Uncomment when moving to final PCB)
# gate = Pin(14, Pin.OUT); gate.value(1)

# LCD RESET (Fixes fading)
rst = Pin(17, Pin.OUT)
rst.value(0); time.sleep(0.1); rst.value(1); time.sleep(0.1)

scr = Display(spi, cs=Pin(20), dc=Pin(16), rst=Pin(17))
joy_x, joy_y = ADC(Pin(26)), ADC(Pin(27))
btn_joy = Pin(22, Pin.IN, Pin.PULL_UP)
buzzer = PWM(Pin(15))
buzzer.duty_u16(0)

print("--- UNIVERSAL DIAGNOSTIC READY ---")

while True:
    x_raw, y_raw = joy_x.read_u16(), joy_y.read_u16()
    
    # --- CLAMPED COORDINATES ---
    # (Value / Max) * (ScreenSize - ObjectSize)
    # This keeps the 12x12 square fully visible at the 320/240 edges
    # if joystick to left moves paddle to right, use: cur_x = (320 - 12) - int((x_raw / 65535) * (320 - 12)) instead.
    cur_x = int((x_raw / 65535) * (320 - 12)) 
    cur_y = int((y_raw / 65535) * (240 - 12))
    
    scr.fill(0)
    
    if btn_joy.value() == 0:
        color = 0xF800 # Red
        buzzer.freq(1000)
        buzzer.duty_u16(2000)
    else:
        color = 0xFFFF # White
        buzzer.duty_u16(0)
        
    scr.fill_rect(cur_x, cur_y, 12, 12, color)
    time.sleep(0.04) # Slightly faster refresh