# various.py micropython-touch demo of multiple controls on a large display

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021-2024 Peter Hinch

# Initialise hardware and framebuf before importing modules.
# Create SSD instance. Must be done first because of RAM use.
import hardware_setup

from gui.core.tgui import Screen, ssd
from gui.core.writer import CWriter
import gui.fonts.freesans17 as font17  # Font for CWriter
import gui.fonts.freesans20 as font20
import gui.fonts.freesans23 as font23
from gui.core.colors import *

from gui.widgets import (
    Label,
    Button,
    CloseButton,
    Textbox,
    HorizSlider
)

import uasyncio as asyncio
import gc
import machine
from tinyframe import TinyFrame

label_conf={"bgcolor":WHITE, "fgcolor":BLACK}

class SettingScreen(Screen):
    def __init__(self):
        super().__init__()
        self.wri17 = CWriter(ssd, font17, verbose=False)
        self.close_btn = CloseButton(self.wri17)
        self.backlight_label = Label(self.wri17, 5, 5, text="Backlight", **label_conf)
        self.backlight_scale = HorizSlider(self.wri17, 25, 5, width=280, divisions=10, value=hardware_setup.backlight.duty_u16()/25565, callback=lambda s: hardware_setup.backlight.duty_u16(int(s.value()*25565)) )

class MainScreen(Screen):
    def __init__(self):
        super().__init__()
        self.wri17 = CWriter(ssd, font17, verbose=False)
        self.wri20 = CWriter(ssd, font20, verbose=False)
        self.wri23 = CWriter(ssd, font23, verbose=False)
        self.afr_label = Label(self.wri20, 10, 30, text="AFR", **label_conf)
        self.rpm_label = Label(self.wri20, 100, 30, text="RPM", **label_conf)
        self.speed_label = Label(self.wri20, 10, 130, text="SPEED", **label_conf)
        self.warn_label = Label(self.wri20, 10, 240, text="WARN", **label_conf)
        self.afr_value = Label(self.wri23, 50, 30, text="14.7", **label_conf)
        self.rpm_value = Label(self.wri23, 130, 30, text="2700", **label_conf)
        self.speed_value = Label(self.wri23, 100, 130, text="20", **label_conf)
        self.warn_value = Textbox(self.wri17, 30, 220, 90, 12, bdcolor=GREEN, **label_conf)
        for i in range(100): self.warn_value.append("python!!")
        self.setting_btn = Button(self.wri20, 200, 30, **label_conf, text="Setting", height=30, litcolor=BLUE, callback=lambda bt: Screen.change(SettingScreen))
        
        self.uart = machine.UART(0, 9600)
        self.uart_reader = asyncio.StreamReader(self.uart)
        self.uart_frame = TinyFrame()
        asyncio.create_task(self.loop())
    async def loop(self):
        while 1:
            data = await self.uart_reader.readline()
            print(data)
            self.uart_frame.accept(data)
            

def main():
    hardware_setup.backlight.duty_u16(25565)
    if ssd.height < 240 or ssd.width < 320:
        print(" This test requires a display of at least 320x240 pixels.")
    else:
        print("Start monitor")
        Screen.change(MainScreen)

from async_websocket_client import AsyncWebsocketClient
WS_SERVER="wss://ecorun.marusoftware.net"
SSID=""
PSK=""

self.ws = AsyncWebsocketClient()
self.ws.handshake(WS_SERVER)

main()
