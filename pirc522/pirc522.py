#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RFID RC522 Bibliothek für Raspberry Pi (Deutsche Version)
Autor: AmirMobasheraghdam
Datum: 2025

Diese Klasse ermöglicht die Kommunikation mit dem RFID-Modul RC522 über SPI.
Sie enthält Methoden zum Initialisieren, Erkennen von Karten, Lesen der UID,
Authentifizieren sowie Lesen und Schreiben von Datenblöcken.
"""

import spidev
import RPi.GPIO as GPIO
import time

class RFID:
    """
    Hauptklasse für die RFID RC522 Kommunikation
    """
    
    # Register-Adressen (aus dem Datenblatt)
    COMMAND_REG      = 0x01
    COM_IEN_REG      = 0x02
    DIV_IEN_REG      = 0x03
    COM_IRQ_REG      = 0x04
    DIV_IRQ_REG      = 0x05
    ERROR_REG        = 0x06
    STATUS1_REG      = 0x07
    STATUS2_REG      = 0x08
    FIFO_DATA_REG    = 0x09
    FIFO_LEVEL_REG   = 0x0A
    WATER_LEVEL_REG  = 0x0B
    CONTROL_REG      = 0x0C
    BIT_FRAMING_REG  = 0x0D
    COLL_REG         = 0x0E
    MODE_REG         = 0x11
    TX_MODE_REG      = 0x12
    RX_MODE_REG      = 0x13
    TX_CONTROL_REG   = 0x14
    TX_AUTO_REG      = 0x15
    TX_SEL_REG       = 0x16
    RX_SEL_REG       = 0x17
    RX_THRESHOLD_REG = 0x18
    DEMOD_REG        = 0x19
    MF_TX_REG        = 0x1C
    MF_RX_REG        = 0x1D
    SERIAL_SPEED_REG = 0x1F
    CRC_RESULT_REG_H = 0x21
    CRC_RESULT_REG_L = 0x22
    RF_CFG_REG       = 0x26
    VERSION_REG      = 0x37

    # Befehle für das Modul
    IDLE_CMD         = 0x00
    CALC_CRC_CMD     = 0x03
    TRANSMIT_CMD     = 0x04
    NO_CMD_CHANGE    = 0x07
    RECEIVE_CMD      = 0x08
    TRANSCEIVE_CMD   = 0x0C
    AUTHENT_CMD      = 0x0E
    SOFT_RESET_CMD   = 0x0F

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
        self._write_register(self.TX_AUTO_REG, 0x40)
        self._write_register(self.MODE_REG, 0x3D)
        self._write_register(self.TX_CONTROL_REG, 0x03)
        self.antenna_on()
    
    def reset(self):
        """Setzt den RFID-Reader zurück (Soft-Reset)"""
        self._write_register(self.COMMAND_REG, self.SOFT_RESET_CMD)
        time.sleep(0.1)
        # Warten bis Reset abgeschlossen
        while self._read_register(self.COMMAND_REG) & (1 << 4):
            pass
    
    def antenna_on(self):
        """Aktiviert die Antenne"""
        value = self._read_register(self.TX_CONTROL_REG)
        if ~(value & 0x03):
            self._write_register(self.TX_CONTROL_REG, value | 0x03)
    
    def antenna_off(self):
        """Deaktiviert die Antenne"""
        value = self._read_register(self.TX_CONTROL_REG)
        self._write_register(self.TX_CONTROL_REG, value & ~0x03)
    
    def _write_register(self, address, value):
        """Schreibt in ein Register des RC522"""
        address = (address << 1) & 0x7E
        self.spi.xfer2([address, value])
    
    def _read_register(self, address):
        """Liest aus einem Register des RC522"""
        address = ((address << 1) & 0x7E) | 0x80
        response = self.spi.xfer2([address, 0])
        return response[1]
    
    def _set_bitmask(self, address, mask):
        """Setzt bestimmte Bits in einem Register (ODER-Maske)"""
        value = self._read_register(address)
        self._write_register(address, value | mask)
    
    def _clear_bitmask(self, address, mask):
        """Löscht bestimmte Bits in einem Register (UND-NOT-Maske)"""
        value = self._read_register(address)
        self._write_register(address, value & (~mask))
    
    def _communicate(self, command, send_data, bits=8):
        """
        Führt einen Befehl aus und sendet/empfängt Daten über SPI
        
        Args:
            command (int): Befehlscode (z.B. TRANSCEIVE_CMD)
            send_data (list): Zu sendende Bytes
            bits (int): Anzahl der Bits pro Byte (meist 8)
        
        Returns:
            tuple: (error_code, received_data)
        """
        # FIFO leeren
        self._clear_bitmask(self.FIFO_LEVEL_REG, 0x80)
        # Daten in FIFO schreiben
        for byte in send_data:
            self._write_register(self.FIFO_DATA_REG, byte)
        
        # Befehl ausführen
        self._write_register(self.COMMAND_REG, command)
        if command == self.TRANSCEIVE_CMD:
            self._set_bitmask(self.BIT_FRAMING_REG, 0x80)  # StartSend aktivieren
        
        # Warten bis Befehl abgeschlossen
        max_wait = 1000  # Timeout ~100ms
        while True:
            n = self._read_register(self.COM_IRQ_REG)
            if n & 0x30:  # TimerIRQ oder RxIRQ?
                break
            max_wait -= 1
            if max_wait == 0:
                break
            time.sleep(0.001)
        
        self._clear_bitmask(self.BIT_FRAMING_REG, 0x80)  # StartSend deaktivieren
        
        # Fehler auslesen
        error = self._read_register(self.ERROR_REG)
        if error & 0x13:  # BufferOvfl, ParityErr, ProtocolErr
            return (error, None)
        
        # Daten aus FIFO lesen
        received = []
        while self._read_register(self.FIFO_LEVEL_REG) > 0:
            received.append(self._read_register(self.FIFO_DATA_REG))
        
        return (error, received)
    
    def request(self, req_mode=0x26):
        """
        Sendet eine Anfrage (Request) an eine Karte in der Nähe.
        
        Args:
            req_mode (int): Anfragemodus (0x26 = Standard Request, 0x52 = All Request)
        
        Returns:
            tuple: (error, tag_type) – tag_type ist 2 Bytes (z.B. 0x0400 für MIFARE)
        """
        self._write_register(self.BIT_FRAMING_REG, 0x07)  # 7 Bits pro Byte senden
        send_data = [req_mode]
        error, received = self._communicate(self.TRANSCEIVE_CMD, send_data)
        if error or not received:
            return (error, None)
        if len(received) != 2:
            return (-1, None)
        tag_type = (received[0] << 8) | received[1]
        return (0, tag_type)
    
    def anticoll(self):
        """
        Führt die Anti-Kollision durch und liefert die UID der Karte.
        
        Returns:
            tuple: (error, uid) – uid ist eine Liste von 4 Bytes (bei MIFARE Classic)
        """
        self._write_register(self.BIT_FRAMING_REG, 0x00)  # 8 Bits pro Byte
        send_data = [0x93, 0x20]  # Anti-Collision Befehl (CL1)
        error, received = self._communicate(self.TRANSCEIVE_CMD, send_data)
        if error or not received:
            return (error, None)
        if len(received) != 5:  # 4 Bytes UID + 1 Byte Prüfsumme (BCC)
            return (-1, None)
        # Prüfsumme berechnen und prüfen
        bcc = 0
        for i in range(4):
            bcc ^= received[i]
        if bcc != received[4]:
            return (-2, None)  # Prüfsummenfehler
        return (0, received[:4])
    
    def select_tag(self, uid):
        """
        Wählt eine Karte anhand ihrer UID aus.
        
        Args:
            uid (list): 4 Bytes UID
        
        Returns:
            bool: True wenn erfolgreich, sonst False
        """
        send_data = [0x93, 0x70] + uid
        # CRC berechnen (vereinfacht: wir hängen 0x00,0x00 an, der Reader berechnet automatisch)
        send_data.extend([0, 0])
        error, received = self._communicate(self.TRANSCEIVE_CMD, send_data)
        if error or not received:
            return False
        # Erfolg wenn received[0] & 0x10 gesetzt (SAK)
        if received[0] & 0x10:
            return True
        return False
    
    def stop_crypto(self):
        """Beendet die aktuelle Verschlüsselung"""
        self._clear_bitmask(self.STATUS2_REG, 0x08)
    
    def authenticate(self, block, key, key_type='A', uid=None):
        """
        Authentifiziert sich für einen bestimmten Block.
        
        Args:
            block (int): Blocknummer
            key (list): 6 Bytes Schlüssel
            key_type (str): 'A' oder 'B'
            uid (list): 4 Bytes UID (muss bei MIFARE Classic übergeben werden)
        
        Returns:
            bool: True wenn Authentifizierung erfolgreich
        """
        if uid is None or len(uid) != 4:
            return False
        
        # Authentifizierungsbefehl vorbereiten
        mode = 0x60 if key_type.upper() == 'A' else 0x61
        send_data = [mode, block] + key + uid[:4]
        
        error, received = self._communicate(self.AUTHENT_CMD, send_data)
        if error or not received:
            return False
        # Erfolg wenn kein Fehler und Bit 0x08 in STATUS2_REG gesetzt (Crypto1 aktiv)
        status2 = self._read_register(self.STATUS2_REG)
        if status2 & 0x08:
            return True
        return False
    
    def read_block(self, block):
        """
        Liest einen 16-Byte-Block aus dem aktuell authentifizierten Sektor.
        
        Args:
            block (int): Blocknummer (0-63 bei 1K)
        
        Returns:
            list: 16 Bytes oder None bei Fehler
        """
        send_data = [0x30, block]
        # CRC anhängen
        send_data.extend([0, 0])
        error, received = self._communicate(self.TRANSCEIVE_CMD, send_data)
        if error or not received:
            return None
        if len(received) == 16:
            return received
        return None
    
    def write_block(self, block, data):
        """
        Schreibt 16 Bytes in einen Block.
        
        Args:
            block (int): Blocknummer
            data (list): 16 Bytes Daten
        
        Returns:
            bool: True bei Erfolg
        """
        if len(data) != 16:
            return False
        
        send_data = [0xA0, block] + data
        # CRC anhängen (wird automatisch berechnet)
        send_data.extend([0, 0])
        error, received = self._communicate(self.TRANSCEIVE_CMD, send_data)
        if error or not received:
            return False
        # Erfolg wenn received[0] == 0x0A
        if len(received) > 0 and received[0] == 0x0A:
            return True
        return False
    
    def halt(self):
        """Versetzt die Karte in den HALT-Zustand"""
        send_data = [0x50, 0x00, 0x00, 0x00]  # Halt Befehl + CRC (00 00)
        self._communicate(self.TRANSCEIVE_CMD, send_data)
    
    def wait_for_tag(self, timeout=None):
        """
        Wartet auf eine RFID-Karte und gibt deren UID zurück.
        
        Args:
            timeout (float): Maximale Wartezeit in Sekunden (None = unendlich)
        
        Returns:
            list: UID als Liste von 4 Bytes oder None bei Timeout/Fehler
        """
        start = time.time()
        while True:
            error, tag_type = self.request()
            if not error and tag_type:
                error, uid = self.anticoll()
                if not error and uid:
                    return uid
            if timeout and (time.time() - start) > timeout:
                return None
            time.sleep(0.05)
    
    def cleanup(self):
        """Räumt GPIO auf und schließt SPI"""
        self.antenna_off()
        GPIO.cleanup()
        self.spi.close()

# Beispiel zur Verwendung (wenn direkt ausgeführt)
if __name__ == "__main__":
    rfid = RFID()
    print("RFID Reader initialisiert. Warte auf Karte...")
    try:
        while True:
            uid = rfid.wait_for_tag(timeout=1.0)
            if uid:
                print(f"Karte erkannt! UID: {uid}")
                # UID hexadezimal ausgeben
                uid_hex = ''.join(f'{b:02X}' for b in uid)
                print(f"UID (hex): {uid_hex}")
                
                # Karte auswählen (optional)
                if rfid.select_tag(uid):
                    print("Karte ausgewählt.")
                else:
                    print("Auswahl fehlgeschlagen.")
                    
                # Authentifizierung für Block 4 (Sektor 1, Block 0)
                key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]  # Standard-Transponderschlüssel
                if rfid.authenticate(4, key, 'A', uid):
                    print("Authentifizierung erfolgreich.")
                    # Block 4 lesen
                    data = rfid.read_block(4)
                    if data:
                        print(f"Gelesene Daten: {data}")
                    else:
                        print("Lesen fehlgeschlagen.")
                    rfid.stop_crypto()
                else:
                    print("Authentifizierung fehlgeschlagen.")
                print("-" * 40)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nAbbruch durch Benutzer")
    finally:
        rfid.cleanup()
