# RFID-Kommunikation mit RC522 und Raspberry Pi
**Entwickelt von: Amir Mobasheraghdam**

Pi-RC522 ist eine umfassende Python-Bibliothek für Raspberry Pi zur Steuerung des beliebten RFID-RC522-Moduls über die SPI-Schnittstelle. Diese Bibliothek ermöglicht eine einfache Integration von RFID-Funktionalität in Ihre Raspberry Pi-Projekte.

---

## RFID Communication with RC522 and Raspberry Pi
**Developed by: Amir Mobasheraghdam**

Pi-RC522 is a comprehensive Python library for Raspberry Pi to control the popular RFID-RC522 module via the SPI interface. This library enables easy integration of RFID functionality into your Raspberry Pi projects.

---

## Inhaltsverzeichnis / Table of Contents
- [Eigenschaften / Features](#eigenschaften--features)
- [Installation / Installation](#installation--installation)
- [Schnellstart / Quick Start](#schnellstart--quick-start)
- [Pin-Konfiguration / Pin Configuration](#pin-konfiguration--pin-configuration)
- [Beispiele / Examples](#beispiele--examples)
- [Lizenz / License](#lizenz--license)

---

## Eigenschaften / Features

### Deutsch
- Vollständige SPI-Protokollunterstützung
- Lesen und Schreiben von RFID-Karten und -Tags
- Unterstützung für Mifare-Karten
- Einfache und benutzerfreundliche Funktionen
- GPIO-Steuerung über RPi.GPIO

### English
- Full SPI protocol support
- Read and write RFID cards and tags
- Mifare card support
- Simple and user-friendly functions
- GPIO control via RPi.GPIO

---

## Installation / Installation

### Deutsch
```bash
pip install pi-rc522
```

### English
```bash
pip install pi-rc522
```

---

## Schnellstart / Quick Start

### Deutsch
```python
import RPi.GPIO as GPIO
from pi_rc522 import RFID

# RFID-Objekt erstellen
rc522 = RFID()

# Auf RFID-Karte warten
print("Bitte RFID-Karte halten...")
rc522.wait_for_tag()

# Karten-ID auslesen
uid = rc522.read_id()
print(f"Karten-ID: {uid}")
```

### English
```python
import RPi.GPIO as GPIO
from pi_rc522 import RFID

# Create RFID object
rc522 = RFID()

# Wait for RFID card
print("Please hold RFID card...")
rc522.wait_for_tag()

# Read card ID
uid = rc522.read_id()
print(f"Card ID: {uid}")
```

---

## Pin-Konfiguration / Pin Configuration

| RC522 Pin | Raspberry Pi Pin (Deutsch) | Raspberry Pi Pin (English) |
|-----------|----------------------------|---------------------------|
| SDA       | GPIO 8 (CE0)               | GPIO 8 (CE0)              |
| SCK       | GPIO 11 (SCLK)             | GPIO 11 (SCLK)            |
| MOSI      | GPIO 10 (MOSI)             | GPIO 10 (MOSI)            |
| MISO      | GPIO 9 (MISO)              | GPIO 9 (MISO)             |
| RST       | GPIO 25                     | GPIO 25                   |
| 3.3V      | Pin 1 (3.3V)               | Pin 1 (3.3V)              |
| GND       | Pin 6 (GND)                 | Pin 6 (GND)               |

---

## Beispiele / Examples

### Deutsch
**Karte lesen:**
```python
from pi_rc522 import RFID

rfid = RFID()
while True:
    if rfid.wait_for_tag():
        uid = rfid.read_id()
        print(f"Karte erkannt: {uid}")
```

### English
**Read card:**
```python
from pi_rc522 import RFID

rfid = RFID()
while True:
    if rfid.wait_for_tag():
        uid = rfid.read_id()
        print(f"Card detected: {uid}")
```

---

## API Referenz / API Reference

### Deutsch
- `RFID()` - Erstellt eine neue RFID-Instanz
- `wait_for_tag()` - Wartet auf eine RFID-Karte
- `read_id()` - Liest die UID der Karte
- `read_block(block)` - Liest einen bestimmten Block
- `write_block(block, data)` - Schreibt Daten in einen Block

### English
- `RFID()` - Creates a new RFID instance
- `wait_for_tag()` - Waits for an RFID card
- `read_id()` - Reads the card UID
- `read_block(block)` - Reads a specific block
- `write_block(block, data)` - Writes data to a block

---

## Fehlerbehebung / Troubleshooting

### Deutsch
- **SPI nicht aktiviert:** Aktivieren Sie SPI mit `sudo raspi-config`
- **Keine Karte erkannt:** Überprüfen Sie die Verkabelung
- **Berechtigungsfehler:** Führen Sie das Skript mit `sudo` aus

### English
- **SPI not enabled:** Enable SPI with `sudo raspi-config`
- **No card detected:** Check your wiring
- **Permission error:** Run the script with `sudo`

---

## Lizenz / License

### Deutsch
MIT Lizenz © 2024 Amir Mobasheraghdam

### English
MIT License © 2024 Amir Mobasheraghdam

---

## Autor / Author
**Amir Mobasheraghdam** (امیر مبشراقدم)

---
⭐ **Bitte sternen Sie dieses Repository / Please star this repository**
```

This README is completely bilingual (German/English) with:
- Full documentation in both languages
- Your name as the author
- Installation instructions
- Code examples
- Pin configuration
- API reference
- Troubleshooting guide
- License information
