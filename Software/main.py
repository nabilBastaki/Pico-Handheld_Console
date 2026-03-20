import machine, time, random
from ili9341 import Display
from machine import ADC, Pin, PWM
import os

# --- 0. FILE SYSTEM INITIALIZATION ---
try:
    with open('highscore.txt', 'r') as f:
        pass 
except OSError:
    with open('highscore.txt', 'w') as f:
        f.write('0')

# --- 1. HARDWARE DEFINITIONS ---
led = Pin("LED", Pin.OUT)
spi = machine.SPI(0, baudrate=24000000, mosi=Pin(19), sck=Pin(18))

# HARD RESET LCD
rst_pin = Pin(17, Pin.OUT)
rst_pin.value(0)
time.sleep(0.1)
rst_pin.value(1)
time.sleep(0.1)

scr = Display(spi, cs=Pin(20), dc=Pin(16), rst=Pin(17))

joy_x, joy_y = ADC(Pin(26)), ADC(Pin(27))
btn_joy = Pin(22, Pin.IN, Pin.PULL_UP)

buzzer = PWM(Pin(15))
buzzer.duty_u16(0)

# --- 2. FONT & DATA ---
FONT = {'0':[0x3E,0x41,0x41,0x41,0x3E],'1':[0x00,0x42,0x7F,0x40,0x00],'2':[0x42,0x61,0x51,0x49,0x46],'3':[0x21,0x41,0x45,0x4B,0x31],'4':[0x18,0x14,0x12,0x7F,0x10],'5':[0x27,0x45,0x45,0x45,0x39],'6':[0x3C,0x4A,0x49,0x49,0x30],'7':[0x01,0x71,0x09,0x05,0x03],'8':[0x36,0x49,0x49,0x49,0x36],'9':[0x06,0x49,0x49,0x29,0x1E],'A':[0x7E,0x11,0x11,0x11,0x7E],'B':[0x7F,0x49,0x49,0x49,0x36],'C':[0x3E,0x41,0x41,0x41,0x22],'D':[0x7F,0x41,0x41,0x22,0x1C],'E':[0x7F,0x49,0x49,0x49,0x41],'F':[0x7F,0x09,0x09,0x09,0x01],'G':[0x3E,0x41,0x49,0x49,0x7A],'H':[0x7F,0x08,0x08,0x08,0x7F],'I':[0x00,0x41,0x7F,0x41,0x00],'J':[0x40,0x40,0x41,0x3F,0x01],'K':[0x7F,0x08,0x14,0x22,0x41],'L':[0x7F,0x40,0x40,0x40,0x40],'M':[0x7F,0x02,0x0C,0x02,0x7F],'N':[0x7F,0x04,0x08,0x10,0x7F],'O':[0x3E,0x41,0x41,0x41,0x3E],'P':[0x7F,0x09,0x09,0x09,0x06],'Q':[0x3E,0x41,0x51,0x21,0x5E],'R':[0x7F,0x09,0x19,0x29,0x46],'S':[0x26,0x49,0x49,0x49,0x32],'T':[0x01,0x01,0x7F,0x01,0x01],'U':[0x3F,0x40,0x40,0x40,0x3F],'V':[0x1F,0x20,0x40,0x20,0x1F],'W':[0x7F,0x20,0x18,0x20,0x7F],'X':[0x63,0x14,0x08,0x14,0x63],'Y':[0x07,0x08,0x70,0x08,0x07],'Z':[0x61,0x51,0x49,0x45,0x43],' ':[0,0,0,0,0],':':[0x00,0x36,0x36,0x00,0x00],'!':[0x00,0x00,0x5F,0x00,0x00]}

def load_highscore():
    try:
        with open("highscore.txt", "r") as f: return int(f.read())
    except: return 0

def save_highscore(val):
    try:
        with open("highscore.txt", "w") as f:
            f.write(str(val))
            f.flush()
            os.sync()
    except Exception as e:
        print("Save Error:", e)

def draw_text(x, y, txt, col, bg=0):
    for char in str(txt).upper():
        bm = FONT.get(char, [0x7F, 0x41, 0x41, 0x41, 0x7F])
        scr.fill_rect(int(x), int(y), 10, 14, bg)
        for i in range(5):
            for j in range(7):
                if (bm[i] >> j) & 1: scr.fill_rect(int(x+i*2), int(y+j*2), 2, 2, col)
        x += 12

def draw_heart(x, y):
    c = 0xF800
    scr.fill_rect(int(x+1), int(y), 2, 1, c); scr.fill_rect(int(x+4), int(y), 2, 1, c)
    scr.fill_rect(int(x), int(y+1), 7, 2, c); scr.fill_rect(int(x+1), int(y+3), 5, 1, c)
    scr.fill_rect(int(x+2), int(y+4), 3, 1, c); scr.fill_rect(int(x+3), int(y+5), 1, 1, c)

# --- 3. GAME STATE ---
DIFF_NAMES = ["EASY", "NORMAL", "HARD"]
settings = {"SPEED": 4.0, "LIVES": 3, "PADDLE": 60, "VOLUME": 2, "DIFF": 1}
BAR_H, BAR_COL, P_H, P_COL, P_Y, B_S = 25, 0x001F, 8, 0x07FF, 215, 8
score, high_score, lives = 0, load_highscore(), 3
is_demo, is_paused, sound_timer = True, False, 0
bx, by, bdx, bdy, px, obx, oby = 160.0, 150.0, 3.0, -3.0, 130.0, 160.0, 150.0
l_score, l_high, l_lives, l_time = -1, -1, -1, -1
bricks = []

def play_sound(freq, duration_ms):
    global sound_timer
    if settings["VOLUME"] == 0: return
    try:
        buzzer.freq(int(freq)); buzzer.duty_u16(settings["VOLUME"] * 1500)
        sound_timer = time.ticks_ms() + duration_ms
    except: pass

def gen_bricks():
    global bricks
    bricks = []
    colors = [0xF800, 0xFFE0, 0x07E0]
    for r in range(3):
        for c in range(7):
            is_ex = random.random() < 0.15
            bricks.append([10+c*44, 45+(r*15), 0xF81F if is_ex else colors[r], True, is_ex])

def update_hud(force=False):
    global l_score, l_high, l_lives, l_time
    bg = BAR_COL
    if force:
        scr.fill_rect(0, 0, 320, BAR_H, bg)
        draw_text(70, 5, "H", 0x07E0, bg); draw_text(150, 5, "S", 0x07FF, bg); draw_text(240, 5, "T", 0xFFE0, bg)
    if high_score != l_high or force:
        draw_text(90, 5, "{:03d}".format(high_score), 0xFFFF, bg); l_high = high_score
    if score != l_score or force:
        draw_text(170, 5, "{:03d}".format(score), 0xFFFF, bg); l_score = score
    if lives != l_lives or force:
        scr.fill_rect(5, 5, 65, 18, bg)
        if lives <= 4:
            for i in range(max(0, lives)): draw_heart(5 + (i * 12), 8)
        else:
            draw_heart(5, 8); draw_text(18, 5, "X" + str(lives), 0xFFFF, bg)
        l_lives = lives
    cur_t = (time.ticks_ms() // 1000) % 1000
    if cur_t != l_time or force:
        draw_text(260, 5, "{:03d}".format(cur_t), 0xFFFF, bg); l_time = cur_t

def wipe_ball():
    scr.fill_rect(int(bx), int(by), B_S, B_S, 0); scr.fill_rect(int(obx), int(oby), B_S, B_S, 0)

def reset_ball_pos():
    global bx, by, obx, oby, bdy
    bx = px + (settings["PADDLE"] // 2) - 4; by = P_Y - 12
    obx, oby = bx, by; bdy = -abs(float(settings["SPEED"]))

def show_game_over():
    play_sound(150, 600)
    scr.fill_rect(60, 100, 200, 50, 0)
    draw_text(110, 110, "GAME OVER", 0xF800); draw_text(85, 130, "CLICK JOYSTICK", 0xFFFF)
    time.sleep(0.6); buzzer.duty_u16(0) 
    while btn_joy.value() == 1: time.sleep(0.01)
    scr.fill(0)

def reset_logic():
    global score, lives, bx, by, bdx, bdy, px, obx, oby
    score, lives = 0, settings["LIVES"]
    px = 160 - (settings["PADDLE"]//2)
    bx, by, bdx, bdy = 160.0, 150.0, float(settings["SPEED"]), -float(settings["SPEED"])
    obx, oby = bx, by
    scr.fill(0); gen_bricks()
    for b in bricks: scr.fill_rect(int(b[0]), int(b[1]), 38, 10, b[2])
    update_hud(True)
    scr.fill_rect(int(px), P_Y, int(settings["PADDLE"]), P_H, P_COL)

def run_setup_menu():
    scr.fill(0)
    draw_text(110, 20, "SETUP", 0x07FF); draw_text(50, 215, "CLICK TO START", 0x07E0)
    sel, keys = 0, ["SPEED", "LIVES", "PADDLE", "VOLUME", "DIFF"]
    while True:
        for i, k in enumerate(keys):
            col = 0xFFFF if i == sel else 0x4444
            draw_text(50, 50 + (i*30), k, col)
            scr.fill_rect(170, 50 + (i*30), 100, 15, 0)
            val = DIFF_NAMES[settings[k]] if k == "DIFF" else str(int(settings[k]))
            draw_text(170, 50 + (i*30), val, col)
        while True:
            jy, jx = joy_y.read_u16(), joy_x.read_u16()
            if jy < 15000 or jy > 50000 or jx < 15000 or jx > 50000 or btn_joy.value()==0: break
            time.sleep(0.01)
        if jy < 15000: sel=(sel-1)%len(keys)
        elif jy > 50000: sel=(sel+1)%len(keys)
        elif jx < 15000:
            if keys[sel]=="PADDLE": settings[keys[sel]]=min(120, settings[keys[sel]]+10)
            elif keys[sel]=="VOLUME": settings[keys[sel]]=min(4, settings[keys[sel]]+1)
            elif keys[sel]=="DIFF": settings[keys[sel]]=(settings[keys[sel]]+1)%3
            else: settings[keys[sel]]=min(15, settings[keys[sel]]+1)
        elif jx > 50000:
            if keys[sel]=="PADDLE": settings[keys[sel]]=max(20, settings[keys[sel]]-10)
            elif keys[sel]=="VOLUME": settings[keys[sel]]=max(0, settings[keys[sel]]-1)
            elif keys[sel]=="DIFF": settings[keys[sel]]=(settings[keys[sel]]-1)%3
            else: settings[keys[sel]]=max(1, settings[keys[sel]]-1)
        if btn_joy.value() == 0: 
            time.sleep(0.3) 
            break
        time.sleep(0.15)

# --- 4. BOOT LOGIC ---
time.sleep(0.1) 
if btn_joy.value() == 0:
    led.value(1)
    run_setup_menu()
    led.value(0)

reset_logic()
is_demo = True

# --- 5. MAIN LOOP ---
while True:
    t_start = time.ticks_ms()
    
    if sound_timer != 0 and time.ticks_ms() > sound_timer:
        buzzer.duty_u16(0); sound_timer = 0
    
    if btn_joy.value() == 0 and is_demo: 
        is_demo = False
        reset_logic()
        time.sleep(0.2)

    o_px = px
    if is_demo: 
        px = bx - (settings["PADDLE"] // 2)
    else:
        jx = joy_x.read_u16()
        if jx < 20000: px += (settings["SPEED"] + 6)
        elif jx > 45000: px -= (settings["SPEED"] + 6)
    px = max(2, min(318 - settings["PADDLE"], px))

    obx, oby = bx, by
    bx += bdx; by += bdy
    
    if bx <= 2 or bx >= 312: bdx *= -1; play_sound(600, 20)
    if by <= BAR_H: bdy = abs(bdy); by = BAR_H + 1; play_sound(600, 20)
    
    if P_Y - 8 <= by <= P_Y and px - 5 <= bx <= px + settings["PADDLE"] + 5:
        bdy = -abs(bdy); by = P_Y - 9; play_sound(800, 30)
    
    # --- Brick Collision ---
    for b in bricks:
        if b[3] and b[0] < bx < b[0]+38 and b[1] < by < b[1]+10:
            bdy *= -1
            b[3] = False
            scr.fill_rect(int(b[0]), int(b[1]), 38, 10, 0)
            
            if not is_demo:
                score += 10
                if score > high_score: 
                    high_score = score
                    save_highscore(high_score)
            
            if b[4]: 
                lives += 1; play_sound(2000, 20)
            else: 
                play_sound(1000, 15)
            
            if not any(bk[3] for bk in bricks):
                wipe_ball(); play_sound(1500, 100)
                if not is_demo:
                    score += 100
                    if score > high_score:
                        high_score = score
                        save_highscore(high_score)
                if settings["DIFF"] == 1: settings["SPEED"] += 0.3
                elif settings["DIFF"] == 2: 
                    settings["SPEED"] += 0.6; settings["PADDLE"] = max(20, settings["PADDLE"]-5)
                gen_bricks()
                for bk in bricks: scr.fill_rect(int(bk[0]), int(bk[1]), 38, 10, bk[2])
                reset_ball_pos(); update_hud(True)
            break
    
    if by > 240:
        if not is_demo:
            lives -= 1
            if lives <= 0:
                if score > high_score: 
                    high_score = score
                    save_highscore(high_score)
                show_game_over(); is_demo = True; reset_logic()
            else: wipe_ball(); reset_ball_pos(); play_sound(200, 100)
        else: bdy = -abs(bdy); by = 230

    if int(bx) != int(obx) or int(by) != int(oby):
        scr.fill_rect(int(obx), int(oby), B_S, B_S, 0)
        scr.fill_rect(int(bx), int(by), B_S, B_S, 0xFFFF)
    if int(px) != int(o_px):
        scr.fill_rect(int(o_px), P_Y, int(settings["PADDLE"]), P_H, 0)
        scr.fill_rect(int(px), P_Y, int(settings["PADDLE"]), P_H, P_COL)
    
    update_hud()
    while time.ticks_diff(time.ticks_ms(), t_start) < 16: pass