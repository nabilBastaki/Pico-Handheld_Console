import time, ustruct, machine

class Display:
    def __init__(self, spi, cs, dc, rst, w=320, h=240):
        self.spi, self.cs, self.dc, self.rst = spi, cs, dc, rst
        self.width, self.height = w, h
        for p in [cs, dc, rst]: p.init(machine.Pin.OUT, value=1)
        self.reset()
        self._init()

    def _write(self, cmd, data=None):
        self.dc.low(); self.cs.low()
        self.spi.write(bytearray([cmd]))
        self.cs.high()
        if data:
            self.dc.high(); self.cs.low()
            self.spi.write(data)
            self.cs.high()

    def reset(self):
        self.rst.low(); time.sleep_ms(100); self.rst.high(); time.sleep_ms(100)

    def _init(self):
        setup_sequence = [
            (0x01, None), (0x11, None), (0x3A, b'\x55'),
            (0x36, b'\x28'), (0x20, None), (0x29, None)
        ]
        for cmd, data in setup_sequence:
            self._write(cmd, data)
            time.sleep_ms(150 if cmd in [0x01, 0x11] else 50)

    def fill_rect(self, x, y, w, h, color):
        x, y, w, h = int(x), int(y), int(w), int(h)
        if x < 0 or y < 0 or x + w > self.width or y + h > self.height: return
        self._write(0x2a, ustruct.pack(">HH", x, x + w - 1))
        self._write(0x2b, ustruct.pack(">HH", y, y + h - 1))
        self._write(0x2c)
        px = ustruct.pack(">H", color)
        self.dc.high(); self.cs.low()
        chunk_size = 512
        chunk = px * chunk_size
        total_pixels = w * h
        for _ in range(total_pixels // chunk_size): self.spi.write(chunk)
        if total_pixels % chunk_size > 0: self.spi.write(px * (total_pixels % chunk_size))
        self.cs.high()

    def fill(self, color):
        self.fill_rect(0, 0, self.width, self.height, color)