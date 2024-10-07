from machine import Pin, SPI, freq, PWM
import gc

from drivers.ili93xx.ili9341 import ILI9341 as SSD
freq(250_000_000)  # RP2 overclock
# Create and export an SSD instance
pdc = Pin(13, Pin.OUT, value=0)  # Arbitrary pins
prst = Pin(14, Pin.OUT, value=1)
pcs = Pin(15, Pin.OUT, value=1)
pspi = SPI(1, baudrate=30_000_000, sck=Pin(10), mosi=Pin(11), miso=Pin(8))
gc.collect()  # Precaution before instantiating framebuf
# Instantiate display and assign to ssd. For args see display drivers doc.
ssd = SSD(pspi, pcs, pdc, prst, usd=True)
# The following import must occur after ssd is instantiated.
from gui.core.tgui import Display, quiet
quiet()
# Define control buttons
# nxt = Pin(19, Pin.IN, Pin.PULL_UP)  # Move to next control
# sel = Pin(16, Pin.IN, Pin.PULL_UP)  # Operate current control
# prev = Pin(18, Pin.IN, Pin.PULL_UP)  # Move to previous control
# increase = Pin(20, Pin.IN, Pin.PULL_UP)  # Increase control's value
# decrease = Pin(17, Pin.IN, Pin.PULL_UP)  # Decrease control's value
# Create a Display instance and assign to display.
from touch.xpt2046 import XPT2046
tirq = Pin(1, Pin.IN)
tcs = Pin(5, Pin.OUT, value=1)
tspi = SPI(0, baudrate=2_500_000, sck=Pin(2), mosi=Pin(3), miso=Pin(4))
tpad = XPT2046(tspi, tcs, ssd)
tpad.init(240, 320, 221, 315, 3873, 3915, True, True, True)
display = Display(ssd, tpad)

backlight=PWM(Pin(6), freq=2000, duty_u16=0)