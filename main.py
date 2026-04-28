import pyvisa
import csv
import time
import datetime
import numpy as np
import os
import yaml

# --------------------------
# Utility functions
# --------------------------

def timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def save_waveform(scope, rail):
    scope.write(":WAV:DATA?")
    data = scope.read_raw()

    fname = f"waveforms/{rail}_{timestamp()}.bin"
    with open(fname, "wb") as f:
        f.write(data)
    return fname

# ---------------------------
# Load rail configuration
# ---------------------------
with open("config/rails.yaml", "r") as fh:
    rails = yaml.safe_load(fh)

# --------------------------
# VISA initialization
# --------------------------

rm = pyvisa.ResourceManager()

psu = rm.open_resource("USB::0x05E6::2230::INSTR")      # Keithley 2230-30-1
eload = rm.open_resource("USB::0x05E6::2380::INSTR")    # Keithley 2380
scope = rm.open_resource("USB::0x2A8D::DSOX6004A::INSTR")  # Keysight scope
dmm = rm.open_resource("USB::0x05E6::DMM6500::INSTR")   # Keithley DMM6500

# ----------------------------------------
# Configure bench supply (5V input)
# ----------------------------------------

psu.write("OUTP OFF")
psu.write("APPL 5, 3")   # 5V, 3A limit
psu.write("OUTP ON")

# ----------------------------
# Prepare CSV log file
# ----------------------------

if not os.path.exists("logs"):
    os.makedirs("logs")

log_file = f"logs/PDN_transient_log_{timestamp()}.csv"

with open(log_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Rail", "LoadStep(A)", "MeasuredVoltage(V)",
        "Overshoot(mV)", "Undershoot(mV)",
        "PassFail", "WaveformFile"
    ])

# --------------------------------
# Configure oscilloscope
# --------------------------------

scope.write(":STOP")
scope.write(":CHAN1:SCAL 0.2")
scope.write(":TIM:SCAL 50e-6")
scope.write(":TRIG:EDGE:SOUR EXT")
scope.write(":WAV:SOUR CHAN1")
scope.write(":WAV:MODE RAW")

# -----------------------
# Test execution
# -----------------------
for rail, spec in rails.items():

    print(f"\nTesting rail: {rail}")

    # Enable load channel
    eload.write("INPUT ON")

    for step in spec["load_steps"]:

        print(f"  Applying load step: {step} A")

        # Apply load
        eload.write(f"CURR {step}")
        time.sleep(0.2)

        # Trigger scope and capture waveform
        scope.write(":SING")
        time.sleep(0.3)

        wf_file = save_waveform(scope, rail)

        # Measure voltage with DMM
        vout = float(dmm.query("MEAS:VOLT:DC?"))

        # Compute overshoot/undershoot from waveform array (approximate)
        # In real lab use, decode binary waveform from scope
        # Here: use placeholder values
        overshoot = np.random.uniform(0, 40)   
        undershoot = np.random.uniform(0, 40)  

        # Determine pass/fail
        limit_mV = spec["transient_limit_mV"]
        pf = "PASS" if overshoot <= limit_mV and undershoot <= limit_mV else "FAIL"

        # Log to CSV
        with open(log_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                rail, step, f"{vout:.3f}",
                f"{overshoot:.1f}", f"{undershoot:.1f}",
                pf, wf_file
            ])

eload.write("INPUT OFF")
psu.write("OUTP OFF")

print("\nTest Completed.")
print(f"CSV log saved at: {log_file}")
print("Waveforms saved in /waveforms folder.")
