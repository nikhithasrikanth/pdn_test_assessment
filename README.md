# PDN Load Transient Test Automation

This repository automates load transient testing for a four‑rail Power Distribution Network:
3.6V, 1.8V, 3.3V, and 2.5V.

## Features
- PyVISA-based SCPI control for PSU, Electronic Load, Scope, and DMM
- Automated load‑step generation
- Transient waveform capture and storage
- CSV logging with timestamp and Pass/Fail
- Waveform file archiving
- Configurable rail definitions (rails.yaml)

## Required Hardware
- Keithley 2230‑30‑1 Power Supply
- Keithley 2380 Electronic Load
- Keysight DSOX6004A Oscilloscope
- Keithley DMM6500

## Running the script
1. Install Python 3.9+
2. Install dependencies:
   pip install pyvisa numpy pyyaml
3. Connect instruments via USB
4. Run:
   python3 main.py

CSV logs will appear in /logs  
Waveforms will appear in /waveforms  
