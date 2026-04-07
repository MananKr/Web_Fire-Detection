# Fire Detection System - Complete Hardware Schematic & Wiring Diagram

## 📋 System Overview
```
┌─────────────────────────────────────────────────────────────┐
│         FIRE DETECTION SYSTEM (FAS) - Complete Setup        │
└─────────────────────────────────────────────────────────────┘

HARDWARE LAYER:
├─ Sensors & Inputs
├─ Arduino UNO R4 WiFi (Brain)
├─ Display & Indicators
└─ Communication Modules

FIRMWARE LAYER:
├─ ArduinoFlaskFASsystem.ino
├─ EEPROM Management
└─ Dual Communication (Serial + WiFi)

APPLICATION LAYER:
├─ Python Flask Server (Port 5000)
├─ YOLO Fire Detection Model
├─ Web Dashboard GUI
└─ Real-time Monitoring
```

---

## 🔌 ARDUINO UNO R4 WIFI - PIN CONFIGURATION

### Analog Inputs (A0-A3)
```
PIN A0  ──> FLAME DETECTOR (Analog Input, 0-1023)
PIN A1  ──> MULTI-DETECTOR / SMOKE SENSOR (Analog Input, 0-1023)
PIN A2  ──> (Available)
PIN A3  ──> (Available)
```

### Digital I/O Pins
```
PIN 0   ──> RX (Serial Receive from PC)
PIN 1   ──> TX (Serial Transmit to PC)
PIN 2   ──> (Available)
PIN 3   ──> SILENCE BUTTON (INPUT_PULLUP)
PIN 4   ──> MODE BUTTON (INPUT_PULLUP)
PIN 5   ──> LED FIRE / Buzzer Control (OUTPUT)
PIN 6   ──> LED RELAY (OUTPUT)
PIN 7   ──> RESET BUTTON (INPUT_PULLUP)
PIN 8   ──> LED OK / Status LED (OUTPUT)
PIN 9   ──> REBOOT PIN (OUTPUT)
PIN 10  ──> (SPI SS - Available)
PIN 11  ──> (SPI MOSI - Available)
PIN 12  ──> (SPI MISO - Available)
PIN 13  ──> LED_PIN / Status Light (OUTPUT)
PIN 14  ──> (Available)
PIN 15  ──> (Available)
PIN 16  ──> (Available)
PIN 17  ──> (Available)
PIN 18  ──> (Available)
PIN 19  ──> (Available)
PIN 20  ──> SDA (I2C for LCD Display)
PIN 21  ──> SCL (I2C for LCD Display)
```

---

## 🖥️ WIRING DIAGRAM - COMPLETE CONNECTIONS

### 1. FLAME DETECTOR CONNECTIONS
```
FLAME DETECTOR
├─ VCC (Power)       ──> Arduino 5V
├─ GND (Ground)      ──> Arduino GND
└─ AOUT (Analog Out) ──> Arduino PIN A0

┌───────────────────────────┐
│   FLAME DETECTOR MODULE   │
│  (Infrared Sensor)        │
├───────────────────────────┤
│  • Operating Voltage: 5V  │
│  • Output Range: 0~1023   │
│  • Threshold: ~700        │
│  • Detection Range: ~1M   │
└───────────────────────────┘

ARDUINO SIDE:
  A0 ←─[10kΩ Pull-up]─← FLAME_AOUT
      ├─ GND
      └─ 5V
```

### 2. MULTI-DETECTOR / SMOKE SENSOR CONNECTIONS
```
MULTI-DETECTOR (MQ-2 / MQ-135)
├─ VCC (Power)       ──> Arduino 5V
├─ GND (Ground)      ──> Arduino GND
└─ AOUT (Analog Out) ──> Arduino PIN A1

┌───────────────────────────────┐
│   MULTI-DETECTOR MODULE       │
│  (Smoke/Gas/LPG Sensor)       │
├───────────────────────────────┤
│  • Operating Voltage: 5V      │
│  • Output Range: 0~5V (1023)  │
│  • Detection: Smoke, CO, LPG  │
│  • Response Time: ~10s        │
│  • Threshold Voltage: 1.5-2V  │
└───────────────────────────────┘

ARDUINO SIDE:
  A1 ←─ SMOKE_AOUT
      ├─ GND
      └─ 5V
```

### 3. BUTTON CONNECTIONS (MICRO SWITCHES)
```
┌─────────────────────────────────────────└─┐
│         MICRO SWITCH BUTTONS               │
├──────────────────────────────────────────┤

SILENCE BUTTON (PIN 3)
  ┌──5V──[10kΩ Pull-up]──┐
  │                       │
  PIN 3 ────[SWITCH]──── GND
  • Debounce: 20ms
  • Action: Toggle buzzer/relay
  • State: HIGH (up) = Not pressed, LOW (down) = Pressed

MODE BUTTON (PIN 4)
  ┌──5V──[10kΩ Pull-up]──┐
  │                       │
  PIN 4 ────[SWITCH]──── GND
  • Debounce: 20ms
  • Modes: AUTO → CNN → MAINTENANCE → AUTO
  • State: HIGH (up) = Not pressed, LOW (down) = Pressed

RESET BUTTON (PIN 7)
  ┌──5V──[10kΩ Pull-up]──┐
  │                       │
  PIN 7 ────[SWITCH]──── GND
  • Press: Clear alert, reset system state
  • Hold >100ms: Perform system reset
  • State: HIGH (up) = Not pressed, LOW (down) = Pressed

WIRING DETAIL:
  ┌─ 5V
  │
  [10kΩ Resistor]
  │
  ├──→ Pin X (to Arduino)
  │
  ├─[Micro Switch]
  │
  └─ GND
```

### 4. STATUS INDICATOR LEDS
```
LED OK (Green, PIN 8)
  Arduino PIN 8 ──[220Ω]──[LED(+)]──── GND
  • Green indicator (System healthy)
  • Active: HIGH (5V)
  • Current Limit: 220Ω resistor
  
LED FIRE (Red, PIN 5)
  Arduino PIN 5 ──[220Ω]──[LED(+)]──── GND
  • Red indicator (Fire detected)
  • Active: HIGH (5V)
  • Current Limit: 220Ω resistor
  
LED RELAY (Yellow/Buzzer, PIN 6)
  Arduino PIN 6 ──[Relay/Buzzer Driver]──→ BUZZER
  • Buzzer/Relay control
  • Active: HIGH (5V)
  • Can drive small relay or buzzer

COMPLETE LED CIRCUIT:
  5V ─[220Ω]─┬─ PIN 8 (OK) ────→ GND
            ├─ PIN 5 (FIRE) ────→ GND
            └─ PIN 6 (RELAY) ────→ GND
```

### 5. LCD 16x2 DISPLAY (I2C)
```
LCD DISPLAY 16x2 with I2C Module
  • I2C Address: 0x27
  • Communication: I2C (SDA/SCL)
  • Resolution: 16 characters × 2 lines
  • Backlight: Enabled

CONNECTIONS:
  LCD VCC  ──→ Arduino 5V
  LCD GND  ──→ Arduino GND
  LCD SDA  ──→ Arduino PIN 20
  LCD SCL  ──→ Arduino PIN 21

I2C BUS WIRING:
  5V
  │
  ├─[4.7kΩ Pull-up]─── PIN 20 (SDA)
  │                        │
  │                      LCD_SDA
  │
  ├─[4.7kΩ Pull-up]─── PIN 21 (SCL)
  │                        │
  │                      LCD_SCL
  │
  └─ GND ────→ LCD_GND

LCD PIN LAYOUT:
  1:GND  2:VCC  3:Contrast  4:RS  5:RW  6:E  7-14:Data  15:BL+ 16:BL-
  (Handled by I2C module - backpack simplifies wiring)
```

### 6. SERIAL CONNECTION (USB to PC)
```
ARDUINO TO PC (Direct USB or FTDI Module)
  Pin 0 (RX) ──[USB]──→ PC COM Port (IN)
  Pin 1 (TX) ──[USB]──→ PC COM Port (OUT)
  GND        ──[USB]──→ PC GND

USB Connection:
  ┌─────────────────────┐
  │   USB Cable         │
  │ (Arduino → PC)      │
  ├─────────────────────┤
  │ • Baudrate: 115200  │
  │ • 8 Data Bits       │
  │ • 1 Stop Bit        │
  │ • No Parity         │
  │ • No Flow Control   │
  └─────────────────────┘

Flask receives:
  • ALERT: Fire/Smoke detection messages
  • CONFIG: Mode changes, system status
  • STATUS: WiFi, IP address updates
```

### 7. WIFI CONNECTIONS
```
ARDUINO WIFI (Built-in R4 Module)
  • Connection: WiFi IEEE 802.11 b/g/n (2.4GHz / 5GHz)
  • Protocol: TCP/IP
  • Security: WPA2/WPA3

NETWORK SETUP:
  ┌──────────────────────────┐
  │    WiFi ROUTER           │
  │ (2.4GHz/5GHz)            │
  └────────┬─────────────────┘
           │ (WiFi Signal)
    ┌──────┴──────┐
    │ Arduino     │
    │ UNO R4      │           ┌──────────────────┐
    │ WiFi Module │◄─────────→│ Flask Server (PC)│
    │             │ (HTTP/IP) │ Port: 5000       │
    └─────────────┘           └──────────────────┘

IP ADDRESSING:
  Arduino IP: Dynamic (DHCP) or Static (192.168.x.x)
  Flask IP: 192.168.x.x (configurable)
  Endoint: http://[Flask_IP]:5000/arduino_alert
```

### 8. CAMERA CONNECTION
```
HIKE-VISION PTZ CAMERA
  • Connection: USB or Ethernet/IP
  • Protocol: USB HID or RTSP
  • Resolution: HD (1080p or higher)

SETUP:
  Camera ──[USB/IP]──→ PC/Flask Server
           • Real-time video stream
           • PTZ control capability
           • Integration with YOLO detection
```

### 9. COMPLETE POWER DISTRIBUTION
```
POWER SUPPLY CIRCUIT
  ┌──────────────┐
  │ Power Supply │  5V, 2A minimum (for sensors + Arduino + LEDs)
  │ (5V, USB)    │
  └────┬─────────┘
       │
       ├─ 5V ──→ Arduino VCC
       ├─ 5V ──→ Flame Detector VCC
       ├─ 5V ──→ Smoke Detector VCC
       ├─ 5V ──→ LCD Display VCC
       ├─ 5V ──→ LED Pull-up Resistors
       │
       └─ GND ──→ All components GND (common ground)

POWER REQUIREMENTS:
  • Arduino UNO R4: 200mA
  • Flame Detector: 100mA
  • Smoke Detector: 100mA
  • LCD 16x2: 50mA
  • 3x LEDs: 60mA (3×20mA)
  • Total: ~510mA (use 2A supply for margin)
```

---

## 📊 SIGNAL FLOW DIAGRAM

```
DETECTION FLOW:
  ┌─────────────────────────────────────────────────┐
  │  Analog Sensors (A0, A1)                        │
  │  ├─ Flame: Reads 0-1023 (Threshold: ~700)     │
  │  └─ Smoke: Reads 0-1023 (Threshold: ~1.5-2V)  │
  └────────────┬────────────────────────────────────┘
               ↓
  ┌─────────────────────────────────────────────────┐
  │  Arduino Processing                             │
  │  • Read sensors every 250ms                     │
  │  • Process buttons (20ms debounce)              │
  │  • Update LCD every 150ms                       │
  │  • Check WiFi every 3s                          │
  └────────────┬────────────────────────────────────┘
               ↓
  ┌─────────────────────────────────────────────────┐
  │  Alert & Response                               │
  │  • Trigger LEDs (Red + Yellow)                  │
  │  • Activate Buzzer/Relay                        │
  │  • Display on LCD 16x2                          │
  │  • Send alerts via Serial + HTTP                │
  └────────────┬────────────────────────────────────┘
               ↓
  ┌─────────────────────────────────────────────────┐
  │  Flask Server & GUI                             │
  │  • Receive alert (HTTP POST)                    │
  │  • Log fire event                               │
  │  • Display on dashboard                         │
  │  • Send response/commands                       │
  └────────────┬────────────────────────────────────┘
               ↓
  ┌─────────────────────────────────────────────────┐
  │  User Control (GUI or Physical Buttons)         │
  │  • Mode Switch (AUTO/CNN/MAINTENANCE)           │
  │  • Silence Alert (Button or Web)                │
  │  • Reset System (Button or Web)                 │
  │  • View Live Feed & Logs                        │
  └─────────────────────────────────────────────────┘
```

---

## 🔧 COMMUNICATION PROTOCOLS

### Serial Communication (Arduino ↔ PC)
```
PROTOCOL: UART/Serial
Format: Text commands terminated with \n

COMMANDS (Flask → Arduino):
  • CMD:PING              → Test connection
  • CMD:FIRE              → Trigger fire alert
  • CMD:RESET             → Reset system
  • CMD:AUTO              → Set AUTO mode
  • CMD:CNN               → Set CNN mode
  • CMD:MAINTENANCE_ON    → Maintenance mode
  • CMD:MAINTENANCE_OFF   → Return from maintenance
  • SILENCE               → Toggle buzzer
  • FLASK_IP:192.168.x.x  → Set Flask IP
  • ARDUINO_IP:192.168.x.x → Set Arduino static IP

RESPONSES (Arduino → Flask):
  • ALERT:message         → Fire/smoke alert
  • CONFIG:message        → Mode/status config
  • STATUS:message        → System status
  • PONG                  → Response to ping

Baudrate: 115200
Data Bits: 8
Stop Bits: 1
Parity: None
```

### HTTP Communication (Arduino WiFi → Flask)
```
PROTOCOL: HTTP/1.1 POST
Endpoint: /arduino_alert

REQUEST HEADER:
  POST /arduino_alert HTTP/1.1
  Host: [Flask_IP]:5000
  Content-Type: application/json
  Content-Length: [length]
  Connection: close

REQUEST BODY:
  {"message":"[ALERT] Flame Detected"}
  {"message":"[CONFIG] AUTO Mode Active"}

RESPONSE:
  HTTP/1.1 200 OK
  Content-Type: application/json
  {"status":"ok","received":"message"}

Timeout: 2000ms
Attempts: 3 (with fallback to serial)
```

---

## 🎛️ CONTROL LAYOUT

### Physical Controls (Arduino Side)
```
┌────────────────────────────────────────┐
│     ARDUINO PANEL LAYOUT               │
├────────────────────────────────────────┤
│                                        │
│  [🟢] LED_OK        [FLAME DETECTOR]  │
│                                        │
│  [🔴] LED_FIRE      [SMOKE DETECTOR]  │
│                                        │
│  [🟡] LED_RELAY                       │
│                                        │
│  ┌────────────────────┐               │
│  │                    │               │
│  │   LCD 16x2         │               │
│  │   Display          │               │
│  │                    │               │
│  └────────────────────┘               │
│                                        │
│  [SILENCE]  [RESET]  [MODE]           │
│                                        │
│  🔇          🔄       ⚙️               │
│  PIN 3       PIN 7    PIN 4           │
│                                        │
└────────────────────────────────────────┘
```

### GUI Controls (Monitor Side)
```
┌─────────────────────────────────────────────┐
│     FLASK DASHBOARD GUI (Web Monitor)       │
├─────────────────────────────────────────────┤
│                                             │
│  🔴 FIRE DETECTION SYSTEM                   │
│                                             │
│  Mode: [AUTO] [CNN] [MAINTENANCE]          │
│                                             │
│  Status:                                    │
│  • Arduino: Connected ✓                     │
│  • WiFi: Connected ✓                        │
│  • Camera: Active ✓                         │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │  Live Video Feed (PTZ Camera)       │   │
│  │                                     │   │
│  │          [Video Stream]             │   │
│  │                                     │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  Last Alert: None                           │
│  System Mode: AUTO                          │
│  Silence Status: OFF                        │
│                                             │
│  [🔇 Silence] [🔄 Reset] [🛠️Reboot]         │
│                                             │
│  Recent Events:                             │
│  • 10:33:45 - System Started               │
│  • 10:35:20 - WiFi Connected               │
│  • ...                                      │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 📐 DIMENSIONS & LAYOUT

```
ARDUINO BOARD:
  Size: 68.6 x 53.3 mm (2.7" x 2.1")
  Connectors: USB, Headers
  Weight: ~25g

LCD DISPLAY (16x2):
  Size: 80 x 36 mm (3.15" x 1.42")
  Module: 80 x 45 x 15 mm (with backpack)
  Weight: ~50g

SENSOR MODULES:
  Flame Detector: 33 x 33 mm
  Smoke Detector: 45 x 28 x 22 mm

ENCLOSURE RECOMMENDATION:
  Size: 200 x 150 x 100 mm
  Material: ABS/PVC plastic
  Mounting: DIN rail or wall mount
  Ventilation: Required for sensors
```

---

## 🧪 TESTING CHECKLIST

```
HARDWARE VERIFICATION:
  ☐ All connections secured (no loose wires)
  ☐ Power supply voltage confirmed (5V ±0.5V)
  ☐ No short circuits (continuity test)
  ☐ All components powered (LEDs light up)
  ☐ LCD displays correctly (I2C address 0x27)
  ☐ Serial connection recognized on PC
  ☐ WiFi module detected

SENSOR CALIBRATION:
  ☐ Flame detector in normal light (~900)
  ☐ Flame detector with lighter (~200)
  ☐ Smoke detector in clean air (~900)
  ☐ Smoke detector with smoke (~300)

BUTTON TESTING:
  ☐ Silence button toggles LED_Relay
  ☐ Reset button clears alerts
  ☐ Mode button cycles through modes
  ☐ All buttons debounce correctly

COMMUNICATION:
  ☐ Serial messages visible in terminal
  ☐ Flask receives alerts via HTTP
  ☐ Commands sent via serial work
  ☐ WiFi connects to router
  ☐ Web GUI displays correctly

SYSTEM INTEGRATION:
  ☐ Camera stream in web GUI
  ☐ YOLO detection working
  ☐ Alerts log to database
  ☐ Historical data displayed
  ☐ All modes (AUTO/CNN/MAINTENANCE) work
```

---

## 📝 FIRMWARE PARAMETERS

```
// Threshold Configurations
#define FLAME_THRESHOLD 700        // Analog value for flame detection
#define SMOKE_VOLTAGE_MIN 1.5      // Minimum voltage for smoke
#define ADC_MAX 1023.0             // Maximum ADC value
#define ADC_REF_VOLT 4.8           // Reference voltage

// Timing Configurations
#define SENSOR_READ_INTERVAL 250   // ms - read sensors
#define LCD_UPDATE_INTERVAL 150    // ms - update display
#define WIFI_CHECK_INTERVAL 3000   // ms - check WiFi
#define DEBOUNCE_DELAY 20          // ms - button debounce
#define HOLD_TIME 5000             // ms - button hold time

// Communication
#define FLASK_PORT 5000
#define BAUD_RATE 115200

// EEPROM Addresses
#define EEPROM_WIFI_START 0
#define EEPROM_MODE_ADDR 500
#define WIFI_MAGIC 0xA5A5
#define EEPROM_MAGIC_MODE 0xB5B5
```

---

## 🚀 QUICK START GUIDE

1. **Hardware Assembly:**
   - Mount Arduino, sensors, and buttons
   - Connect all components per wiring diagram
   - Verify power supply (5V, 2A)

2. **Firmware Upload:**
   - Upload `ArduinoFlaskFASsystem.ino` to Arduino
   - Verify compilation (115200 baudrate)
   - Check serial monitor for startup messages

3. **Network Setup:**
   - Run Flask server on PC: `python FD_yolo_model.py`
   - Connect Arduino to WiFi router
   - Configure Flask IP via serial or web GUI

4. **Camera Setup:**
   - Connect HIKE-VISION PTZ camera
   - Configure in Flask settings
   - Test video stream

5. **Testing:**
   - Monitor serial output for debug messages
   - Test sensors with flame/smoke
   - Verify alerts in web GUI
   - Test all buttons and modes

---

## 📞 TROUBLESHOOTING

### Sensors not responding
- Check ADC connections (A0, A1)
- Verify pull-up resistors (10kΩ)
- Test with Serial Monitor: read analog values

### LCD not displaying
- Verify I2C address (0x27) with scanner code
- Check SDA/SCL connections (pins 20, 21)
- Ensure pull-up resistors (4.7kΩ)

### Buttons not working
- Check INPUT_PULLUP mode
- Verify debounce timing
- Test with Serial Monitor: read pin states

### WiFi disconnection
- Check WiFi credentials in EEPROM
- Verify router is accessible
- Monitor WiFi signal strength

### Alerts not sent
- Verify serial connection working
- Check Flask server running (port 5000)
- Monitor HTTP communication logs
- Verify firewall not blocking

---

**Created:** March 28, 2026  
**System:** Fire Detection System v5.3  
**Author:** Arduino Fire Detection Team  
**Last Updated:** Current Session
