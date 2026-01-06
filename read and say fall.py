import serial
import math
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# -----------------------
#  FALL DETECTION LIMITS
# -----------------------
NO_FALL_MAX = 1.0
PRE_FALL_MIN = 1.5
FALL_MIN = 2.0
POST_FALL_MAX = 1.2

# -----------------------
# Initialize Serial
# -----------------------
ser = serial.Serial("COM6", 115200, timeout=1)
print("Real-Time Fall Detection Started...\n")

# -----------------------
# State mapping
# -----------------------
state_map = {
    "NO-FALL": 0,
    "PRE-FALL": 1,
    "FALL": 2,
    "POST-FALL": 3
}

time_values = []
state_values = []

WINDOW_SECONDS = 5  # REAL 5 seconds

def get_state_from_svm(svm):
    if svm < NO_FALL_MAX:
        return "NO-FALL"
    elif svm < PRE_FALL_MIN:
        return "PRE-FALL"
    elif svm >= FALL_MIN:
        return "FALL"
    elif svm < POST_FALL_MAX:
        return "POST-FALL"
    return "NO-FALL"

def update(frame):

    line = ser.readline().decode(errors="ignore").strip()
    if not line:
        return

    parts = line.split()
    if len(parts) != 6:
        return

    try:
        ax = float(parts[0])
        ay = float(parts[1])
        az = float(parts[2])
    except:
        return

    svm = math.sqrt(ax*ax + ay*ay + az*az)
    state = get_state_from_svm(svm)

    print(f"{state:10} | SVM = {svm:.2f}")

    # Timestamp of this sample
    t = time.time()

    # Store
    time_values.append(t)
    state_values.append(state_map[state])

    # ---- KEEP ONLY LAST 5 SECONDS ----
    while time_values and (t - time_values[0]) > WINDOW_SECONDS:
        time_values.pop(0)
        state_values.pop(0)

    # ---- PLOT ----
    plt.cla()
    # Shift time axis so leftmost = 0 sec
    t0 = time_values[0]
    shifted_times = [tv - t0 for tv in time_values]

    plt.step(shifted_times, state_values, linewidth=2)
    plt.ylim(-0.5, 3.5)
    plt.yticks([0, 1, 2, 3], ["NO-FALL", "PRE-FALL", "FALL", "POST-FALL"])
    plt.xlabel("Time (seconds)")
    plt.title("Real-Time Fall Detection (Last 5 Seconds)")
    plt.grid(True)


fig = plt.figure("Fall Detection Window")
ani = animation.FuncAnimation(fig, update, interval=10)  # update every 10ms
plt.show()
