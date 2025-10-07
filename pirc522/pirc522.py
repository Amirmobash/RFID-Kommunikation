# -*- coding: utf-8 -*-

import spidev
import RPi.GPIO as GPIO
import time

class RFID:
    """
    Hauptklasse für die RFID RC522 Kommunikation
    """
    
    def __init__(self, bus=0, device=0, speed=1000000, pin_rst=25, pin_ce=0):
        """
        Initialisiert den RFID-Reader
        
        Args:
            bus (int): SPI Bus Nummer (standard: 0)
            device (int): SPI Device Nummer (standard: 0)
            speed (int): SPI Geschwindigkeit in Hz (standard: 1000000)
            pin_rst (int): GPIO Pin für Reset (standard: 25)
            pin_ce (int): GPIO Pin für Chip Enable (standard: 0 = CE0)
        """
        self.bus = bus
        self.device = device
        self.speed = speed
        self.pin_rst = pin_rst
        self.pin_ce = pin_ce
        
        # SPI initialisieren
        self.spi = spidev.SpiDev()
        self._init_spi()
        
        # GPIO initialisieren
        self._init_gpio()
        
        # RFID-Reader initialisieren
        self._init_reader()
    
    def _init_spi(self):
        """Initialisiert die SPI-Schnittstelle"""
        try:
            self.spi.open(self.bus, self.device)
            self.spi.max_speed_hz = self.speed
            self.spi.mode = 0
        except Exception as e:
            raise RuntimeError(f"SPI Initialisierung fehlgeschlagen: {e}")
    
    def _init_gpio(self):
        """Initialisiert die GPIO-Pins"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin_rst, GPIO.OUT)
        GPIO.output(self.pin_rst, 1)
    
    def _init_reader(self):
        """Initialisiert den RFID-Reader"""
        self.reset()
        self._write_register(0x2A, 0x8D)
        self._write_register(0x2B, 0x3E)
        self._write_register(0x2D, 30)
        self._write_register(0x2C, 0)
        self._write_register(0x15, 0x40)
        self._write_register(0x11, 0x3D)
        self.antenna_on()
    
    def reset(self):
        """Setzt den RFID-Reader zurück"""
        self._write_register(0x01, 0x0F)
        time.sleep(0.1)
    
    def antenna_on(self):
        """Aktiviert die Antenne"""
        value = self._read_register(0x14)
        if ~(value & 0x03):
            self._write_register(0x14, value | 0x03)
    
    def _write_register(self, address, value):
        """Schreibt in ein Register"""
        address = (address << 1) & 0x7E
        self.spi.xfer2([address, value])
    
    def _read_register(self, address):
        """Liest aus einem Register"""
        address = ((address << 1) & 0x7E) | 0x80
        response = self.spi.xfer2([address, 0])
        return response[1]
    
    def wait_for_tag(self):
        """Wartet auf eine RFID-Karte"""
        print("Warte auf Karte...")
        while True:
            (error, tag_type) = self.request()
            if not error:
                return tag_type
            time.sleep(0.1)
    
    def request(self):
        """
        Sendet Anfrage an Karte
        
        Returns:
            tuple: (error, tag_type)
        """
        # Implementierung der Kartenanfrage
        pass
    
    def anticoll(self):
        """
        Führt Anti-Collision durch
        
        Returns:
            tuple: (error, uid)
        """
        # Implementierung der Anti-Collision
        pass
    
    def cleanup(self):
        """Räumt GPIO auf"""
        GPIO.cleanup()
        self.spi.close()

# Weitere Methoden und Klassen hier implementieren...
