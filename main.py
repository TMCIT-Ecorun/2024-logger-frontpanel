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
import json
from async_websocket_client import AsyncWebsocketClient
#from rp2 import PIO, asm_pio, StateMachine
from network import STAT_GOT_IP, STAT_CONNECTING
import binascii

try:
    with open("config.json","r") as f:
        config=json.load(f)
    print("Config loaded")
except:
    config={"backlight":25565}
    
label_conf={"bgcolor":WHITE, "fgcolor":BLACK}



class SettingScreen(Screen):
    def __init__(self):
        super().__init__()
        self.wri17 = CWriter(ssd, font17, verbose=False)
        self.close_btn = CloseButton(self.wri17)
        self.backlight_label = Label(self.wri17, 5, 5, text="Backlight", **label_conf)
        self.backlight_scale = HorizSlider(self.wri17, 25, 5, width=280, divisions=10, value=hardware_setup.backlight.duty_u16()/25565, callback=lambda s: hardware_setup.backlight.duty_u16(int(s.value()*25565)) )
        self.mac_label=Label(self.wri17, 50, 5, **label_conf,
                             text="MAC: "+hardware_setup.wlan.config("mac").hex())
        self.ip_label=Label(self.wri17, 70, 5, **label_conf,
                            text=(f"Connected: {hardware_setup.wlan.ifconfig()[0]}" if hardware_setup.wlan.isconnected() else "Disconnected!"))

class MainScreen(Screen):
    def __init__(self):
        super().__init__()
        self.wri17 = CWriter(ssd, font17, verbose=False)
        self.wri20 = CWriter(ssd, font20, verbose=False)
        self.wri23 = CWriter(ssd, font23, verbose=False)
        #self.afr_label = Label(self.wri20, 10, 30, text="AFR", **label_conf)
        #self.rpm_label = Label(self.wri20, 100, 30, text="RPM", **label_conf)
        self.speed_label = Label(self.wri20, 10, 130, text="SPEED", **label_conf)
        self.warn_label = Label(self.wri20, 10, 240, text="WARN", **label_conf)
        #self.afr_value = Label(self.wri23, 50, 30, text="14.7", **label_conf)
        #self.rpm_value = Label(self.wri23, 130, 30, text="2700", **label_conf)
        self.speed_value = Label(self.wri23, 100, 130, text="20", **label_conf)
        self.warn_value = Textbox(self.wri17, 30, 220, 90, 12, bdcolor=GREEN, **label_conf)
        self.setting_btn = Button(self.wri20, 200, 30, **label_conf, text="Setting", height=30, litcolor=BLUE, callback=lambda bt: Screen.change(SettingScreen))
        self.wss=AsyncWebsocketClient(200)
        self.uart = machine.UART(0, 115200, tx=machine.Pin(16), rx=machine.Pin(17), rxbuf=1)
        #self.uart_reader = asyncio.StreamReader(self.uart)
        #self.uart_frame = TinyFrame()
        asyncio.create_task(self.loop())
        self.wifi_con=False
        self.wss_con=False
    async def loop(self):
        gpsdata=b""
        speed=0
        await asyncio.sleep_ms(3_000)
        hardware_setup.gps.write(b'$PSRF106,21*0F\r\n')
        while 1:
            stat=hardware_setup.wlan.status()
            if stat==STAT_GOT_IP:
                if self.wifi_con==False:
                    print("Wifi connected!")
                    self.wifi_con=True
                if (not self.wss_con) or (not await self.wss.open()):
                    print("WS connecting...")
                    try:
                        self.wss_con=await self.wss.handshake("ws://marusoftware.net:8989/ws")
                    except:
                        self.wss_con=False
                    if self.wss_con:
                        print("WS connected!")
            elif stat!=STAT_CONNECTING:
                print("WIFI reconnecting...")
                hardware_setup.wlan.connect(config["wifi_ssid"], config["wifi_psk"])
                self.wifi_con=False
            await asyncio.sleep_ms(80)
            #data = await self.uart_reader.readline()
            uart_tmp=self.uart.read()
            if uart_tmp is not None:
                speed=int.from_bytes(uart_tmp, "big")
                self.speed_value.value(str(speed))
            else:
                speed=-1
            gps_tmp=hardware_setup.gps.readline()
            if gps_tmp is not None:
                if gps_tmp[:1] == b'$':
                    gpsdata=gps_tmp
                else:
                    gpsdata+=gps_tmp
                if gpsdata[-2:] == b'\r\n':
                    try:
                        gpsstr=gpsdata[:-2].decode()
                    except UnicodeError:
                        continue
                    if not gpsstr.startswith("$GPGGA"):
                        continue
                    #print(gpsstr)
                    self.speed_value.value(gpsdata.split(",")[8])
#                     if self.wss_con:
#                         try:
#                             await self.wss.send(gpsstr, speed)#, speed*3.6, difference))
#                         except:
#                             pass
            if self.wss_con:
                try:
                    await self.wss.send("{} {}\n".format(speed))
                except:
                    pass
            
            #print(data, speed*3.6, difference)
    def on_open(self):
        if "wifi_ssid" in config and not self.wifi_con:
            hardware_setup.wlan.active(True)
            hardware_setup.wlan.connect(config["wifi_ssid"], config["wifi_psk"])
            print("Connecting wifi...")
            

def main():
    if ssd.height < 240 or ssd.width < 320:
        print(" This test requires a display of at least 320x240 pixels.")
    else:
        print("Start monitor")
        hardware_setup.backlight.duty_u16(config["backlight"])
        Screen.change(MainScreen)

main()
