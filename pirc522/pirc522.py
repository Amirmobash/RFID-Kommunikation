#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RFID RC522 Bibliothek für Raspberry Pi
Autor: Amir Mobasheraghdam
Version: 2.0 (Verbesserte Version)

Diese Klasse ermöglicht die Kommunikation mit dem RFID-Modul RC522 über SPI.
Enthält Methoden zum Initialisieren, Erkennen von Karten, Lesen der UID,
Authentifizieren sowie Lesen und Schreiben von Datenblöcken.

English:
This class enables communication with the RC522 RFID module via SPI.
It provides methods for initialization, card detection, UID reading,
authentication, and reading/writing data blocks.
"""

import spidev
import RPi.GPIO as GPIO
import time

class RFID:
    """Hauptklasse für die RFID RC522 Kommunikation / Main class for RFID RC522 communication."""

    # Register addresses (from MFRC522 datasheet)
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

    # Commands for the module
    IDLE_CMD         = 0x00
    CALC_CRC_CMD     = 0x03
    TRANSMIT_CMD     = 0x04
    NO_CMD_CHANGE    = 0x07
    RECEIVE_CMD      = 0x08
    TRANSCEIVE_CMD   = 0x0C
    AUTHENT_CMD      = 0x0E
    SOFT_RESET_CMD   = 0x0F

    # Mifare commands
    REQ_IDLE         = 0x26
    REQ_ALL          = 0x52
    ANTICOLL_CMD     = 0x93
    ANTICOLL_CL1     = 0x20
    SELECT_CMD       = 0x93
    SELECT_CL1       = 0x70
    READ_BLOCK_CMD   = 0x30
    WRITE_BLOCK_CMD  = 0xA0
    HALT_CMD         = 0x50

    def __init__(self, bus=0, device=0, speed=1000000, pin_rst=25, pin_ce=0):
        """
        Initialisiert den RFID-Reader / Initializes the RFID reader.

        Args:
            bus (int): SPI Bus number (default: 0)
            device (int): SPI device number (default: 0)
            speed (int): SPI speed in Hz (default: 1000000)
            pin_rst (int): GPIO pin for reset (default: 25)
            pin_ce (int): GPIO pin for chip enable (default: 0 = CE0)
        """
        self.bus = bus
        self.device = device
        self.speed = speed
        self.pin_rst = pin_rst
        self.pin_ce = pin_ce

        # Initialize SPI
        self.spi = spidev.SpiDev()
        self._init_spi()

        # Initialize GPIO
        self._init_gpio()

        # Initialize RFID reader
        self._init_reader()

    def _init_spi(self):
        """Initialisiert die SPI-Schnittstelle / Initializes SPI interface."""
        try:
            self.spi.open(self.bus, self.device)
            self.spi.max_speed_hz = self.speed
            self.spi.mode = 0
        except Exception as e:
            raise RuntimeError(f"SPI initialization failed: {e}")

    def _init_gpio(self):
        """Initialisiert die GPIO-Pins / Initializes GPIO pins."""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin_rst, GPIO.OUT)
        GPIO.output(self.pin_rst, 1)

    def _init_reader(self):
        """Initialisiert den RFID-Reader / Initializes the RFID reader."""
        self.reset()
        self._write_register(self.TX_AUTO_REG, 0x40)
        self._write_register(self.MODE_REG, 0x3D)   # CRC enabled
        self._write_register(self.TX_CONTROL_REG, 0x03)
        self.antenna_on()

    def reset(self):
        """Führt einen Soft-Reset durch / Performs a soft reset."""
        self._write_register(self.COMMAND_REG, self.SOFT_RESET_CMD)
        time.sleep(0.05)
        # Wait for reset to complete
        while self._read_register(self.COMMAND_REG) & (1 << 4):
            pass

    def antenna_on(self):
        """Aktiviert die Antenne / Enables the antenna."""
        value = self._read_register(self.TX_CONTROL_REG)
        if ~(value & 0x03):
            self._write_register(self.TX_CONTROL_REG, value | 0x03)

    def antenna_off(self):
        """Deaktiviert die Antenne / Disables the antenna."""
        value = self._read_register(self.TX_CONTROL_REG)
        self._write_register(self.TX_CONTROL_REG, value & ~0x03)

    def _write_register(self, address, value):
        """Schreibt in ein Register / Writes to a register."""
        address = (address << 1) & 0x7E
        self.spi.xfer2([address, value])

    def _read_register(self, address):
        """Liest ein Register / Reads a register."""
        address = ((address << 1) & 0x7E) | 0x80
        response = self.spi.xfer2([address, 0])
        return response[1]

    def _set_bitmask(self, address, mask):
        """Setzt bestimmte Bits / Sets certain bits."""
        value = self._read_register(address)
        self._write_register(address, value | mask)

    def _clear_bitmask(self, address, mask):
        """Löscht bestimmte Bits / Clears certain bits."""
        value = self._read_register(address)
        self._write_register(address, value & (~mask))

    def _flush_fifo(self):
        """Leert den FIFO-Puffer / Flushes the FIFO buffer."""
        self._write_register(self.FIFO_LEVEL_REG, 0x80)

    def _communicate(self, command, send_data, bits=8, rx_wait=True):
        """
        Führt einen Befehl aus und sendet/empfängt Daten / Executes a command and sends/receives data.

        Args:
            command (int): Command code (e.g., TRANSCEIVE_CMD)
            send_data (list): Bytes to send
            bits (int): Bits per byte (usually 8)
            rx_wait (bool): Wait for receive (for transceive commands)

        Returns:
            tuple: (error, received_data)
        """
        # Flush FIFO before starting
        self._flush_fifo()

        # Write data to FIFO
        for byte in send_data:
            self._write_register(self.FIFO_DATA_REG, byte)

        # Execute command
        self._write_register(self.COMMAND_REG, command)
        if command == self.TRANSCEIVE_CMD:
            self._set_bitmask(self.BIT_FRAMING_REG, 0x80)  # StartSend

        # Wait for completion
        timeout = 1000  # ~100ms
        while True:
            irq = self._read_register(self.COM_IRQ_REG)
            if irq & 0x30:  # TimerIRQ or RxIRQ
                break
            timeout -= 1
            if timeout == 0:
                break
            time.sleep(0.0001)

        # Clear interrupt flags
        self._write_register(self.COM_IRQ_REG, 0x30)

        # Deactivate StartSend
        if command == self.TRANSCEIVE_CMD:
            self._clear_bitmask(self.BIT_FRAMING_REG, 0x80)

        # Check for errors
        error = self._read_register(self.ERROR_REG)
        if error & 0x13:  # BufferOvfl, ParityErr, ProtocolErr
            return (error, None)

        # Read received data (if any)
        received = []
        if rx_wait:
            while self._read_register(self.FIFO_LEVEL_REG) > 0:
                received.append(self._read_register(self.FIFO_DATA_REG))

        return (0, received)

    def request(self, req_mode=REQ_IDLE):
        """
        Sendet eine Anfrage an eine Karte / Sends a request to a card.

        Args:
            req_mode (int): 0x26 = REQ_IDLE, 0x52 = REQ_ALL

        Returns:
            tuple: (error, tag_type) – tag_type is 2 bytes (e.g., 0x0400 for MIFARE)
        """
        self._write_register(self.BIT_FRAMING_REG, 0x07)  # 7 bits per byte
        send_data = [req_mode]
        error, received = self._communicate(self.TRANSCEIVE_CMD, send_data)
        self._write_register(self.BIT_FRAMING_REG, 0x00)  # Back to 8 bits

        if error or not received or len(received) != 2:
            return (error or -1, None)
        tag_type = (received[0] << 8) | received[1]
        return (0, tag_type)

    def anticoll(self, cascade_level=1):
        """
        Führt die Anti-Kollision durch und gibt die UID zurück / Performs anticollision and returns UID.

        Args:
            cascade_level (int): 1 for first cascade, 2 for second, etc.

        Returns:
            tuple: (error, uid_list) – uid_list is a list of bytes
        """
        # For cascade level 1 (standard 4-byte UID)
        if cascade_level == 1:
            self._write_register(self.BIT_FRAMING_REG, 0x00)  # 8 bits
            send_data = [self.ANTICOLL_CMD, self.ANTICOLL_CL1]
            error, received = self._communicate(self.TRANSCEIVE_CMD, send_data)
            if error or not received or len(received) != 5:
                return (error or -1, None)
            # Verify BCC
            bcc = 0
            for i in range(4):
                bcc ^= received[i]
            if bcc != received[4]:
                return (-2, None)
            return (0, received[:4])
        else:
            # For 7-byte UID (cascade level 2) – simplified; see full library for complete implementation
            # This version only supports 4-byte UID (MIFARE Classic)
            return (-1, None)

    def select_tag(self, uid):
        """
        Wählt eine Karte anhand ihrer UID aus / Selects a card by its UID.

        Args:
            uid (list): UID bytes (4 bytes for MIFARE Classic)

        Returns:
            bool: True if successful, False otherwise
        """
        send_data = [self.SELECT_CMD, self.SELECT_CL1] + uid
        # The CRC will be calculated automatically, but we need to send two dummy bytes for the CRC.
        # The _communicate method handles the FIFO, so just send the data and let the hardware append CRC.
        # However, the RC522 expects the command to be sent with the CRC appended. We'll send the data
        # and the CRC will be added automatically if enabled. To simplify, we append zeros and the hardware
        # will overwrite them with the correct CRC.
        send_data.extend([0, 0])
        error, received = self._communicate(self.TRANSCEIVE_CMD, send_data)
        if error or not received:
            return False
        # If successful, the first byte (SAK) should have bit 3 set (0x10)
        return (received[0] & 0x10) != 0

    def authenticate(self, block, key, key_type='A', uid=None):
        """
        Authentifiziert sich für einen bestimmten Block / Authenticates for a specific block.

        Args:
            block (int): Block number (0-63 for 1K)
            key (list): 6 bytes key
            key_type (str): 'A' or 'B'
            uid (list): 4 bytes UID (must be provided for MIFARE Classic)

        Returns:
            bool: True if successful
        """
        if uid is None or len(uid) != 4:
            return False

        # Prepare authentication command
        mode = 0x60 if key_type.upper() == 'A' else 0x61
        send_data = [mode, block] + key + uid[:4]

        # Write authentication command and data to FIFO
        self._flush_fifo()
        for byte in send_data:
            self._write_register(self.FIFO_DATA_REG, byte)

        # Start authentication
        self._write_register(self.COMMAND_REG, self.AUTHENT_CMD)

        # Wait for completion
        timeout = 1000  # ~100ms
        while True:
            cmd = self._read_register(self.COMMAND_REG)
            if cmd & 0x0F == self.IDLE_CMD:  # Idle
                break
            timeout -= 1
            if timeout == 0:
                break
            time.sleep(0.0001)

        # Check Crypto1On bit in Status2Reg
        status2 = self._read_register(self.STATUS2_REG)
        if status2 & 0x08:
            return True
        return False

    def stop_crypto(self):
        """Beendet die aktuelle Verschlüsselung / Stops encryption."""
        self._clear_bitmask(self.STATUS2_REG, 0x08)

    def read_block(self, block):
        """
        Liest einen 16-Byte-Block / Reads a 16-byte block.

        Args:
            block (int): Block number (0-63 for 1K)

        Returns:
            list: 16 bytes or None if error
        """
        send_data = [self.READ_BLOCK_CMD, block, 0, 0]  # Two dummy bytes for CRC
        error, received = self._communicate(self.TRANSCEIVE_CMD, send_data)
        if error or not received:
            return None
        if len(received) == 16:
            return received
        return None

    def write_block(self, block, data):
        """
        Schreibt 16 Bytes in einen Block / Writes 16 bytes to a block.

        Args:
            block (int): Block number
            data (list): 16 bytes data

        Returns:
            bool: True if successful
        """
        if len(data) != 16:
            return False
        send_data = [self.WRITE_BLOCK_CMD, block] + data + [0, 0]  # dummy CRC
        error, received = self._communicate(self.TRANSCEIVE_CMD, send_data)
        if error or not received:
            return False
        # Success response is 0x0A (ACK)
        return received[0] == 0x0A

    def halt(self):
        """Versetzt die Karte in den HALT-Zustand / Puts the card into HALT state."""
        send_data = [self.HALT_CMD, 0x00, 0x00, 0x00]  # Dummy CRC
        self._communicate(self.TRANSCEIVE_CMD, send_data, rx_wait=False)

    def wait_for_tag(self, timeout=None):
        """
        Wartet auf eine RFID-Karte und gibt deren UID zurück / Waits for an RFID card and returns its UID.

        Args:
            timeout (float): Max wait time in seconds (None = infinite)

        Returns:
            list: UID as list of bytes, or None if timeout/error
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
        """Räumt GPIO auf und schließt SPI / Cleans up GPIO and closes SPI."""
        self.antenna_off()
        GPIO.cleanup()
        self.spi.close()


# Beispiel zur Verwendung / Example usage
if __name__ == "__main__":
    rfid = RFID()
    print("RFID Reader initialisiert. Warte auf Karte...")
    try:
        while True:
            uid = rfid.wait_for_tag(timeout=1.0)
            if uid:
                print(f"Karte erkannt! UID: {uid}")
                uid_hex = ''.join(f'{b:02X}' for b in uid)
                print(f"UID (hex): {uid_hex}")

                if rfid.select_tag(uid):
                    print("Karte ausgewählt.")
                else:
                    print("Auswahl fehlgeschlagen.")

                # Authentifizierung mit Standard-Schlüssel
                key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]  # Default key
                if rfid.authenticate(4, key, 'A', uid):
                    print("Authentifizierung erfolgreich.")
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
