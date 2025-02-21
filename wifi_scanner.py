import subprocess
import platform
import pandas as pd
import re


def scan_wifi():
    """ Scans for available Wi-Fi networks and returns a DataFrame with the results. """
    system = platform.system()
    networks = []

# scan available Wi-Fi networks on linux
    if system == "Linux":
        result = subprocess.run(["nmcli", "-t", "-f", "SSID,SIGNAL", "dev", "wifi"], capture_output=True, text=True)
        lines = result.stdout.strip().split("\n")
        for line in lines:
            parts = line.split(":")
            if len(parts) == 2 and parts[1].isdigit():
                networks.append(parts)

# scan available Wi-Fi networks on windows
    elif system == "Windows":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW # completely hide the CMD window on Windows

        result = subprocess.run(["netsh", "wlan", "show", "network", "mode=Bssid"], capture_output=True, text=True,
                                encoding='utf-8', startupinfo=startupinfo)
        output = result.stdout.strip().split("\n")

        ssid = None
        for line in output:
            line = line.strip()
            ssid_match = re.match(r"SSID \d+ : (.+)", line)
            signal_match = re.match(r"Signal\s*:\s*(\d+)%", line)

            if ssid_match:
                ssid = ssid_match.group(1)

            if signal_match and ssid:
                signal_strength = int(signal_match.group(1))
                networks.append([ssid, signal_strength])
                ssid = None

    else:
        raise NotImplementedError("Unsupported OS")

    df = pd.DataFrame(networks, columns=["SSID", "Signal"])

    # make sure the signal is integer
    df["Signal"] = pd.to_numeric(df["Signal"], errors='coerce')
    df = df.dropna()
    df["Signal"] = df["Signal"].astype(int)

    return df
