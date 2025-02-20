import subprocess
import platform
import pandas as pd
import re
import matplotlib.pyplot as plt


def scan_wifi():
    system = platform.system()
    networks = []

    if system == "Linux":
        # 使用 nmcli 获取 WiFi 信号
        result = subprocess.run(["nmcli", "-t", "-f", "SSID,SIGNAL", "dev", "wifi"], capture_output=True, text=True)
        lines = result.stdout.strip().split("\n")
        for line in lines:
            parts = line.split(":")
            if len(parts) == 2 and parts[1].isdigit():  # 确保信号强度是数字
                networks.append(parts)

    elif system == "Windows":
        # 运行 netsh 命令
        result = subprocess.run(["netsh", "wlan", "show", "network", "mode=Bssid"], capture_output=True, text=True,
                                encoding='utf-8')
        output = result.stdout.strip().split("\n")

        ssid = None  # 存储当前的 SSID
        for line in output:
            line = line.strip()
            ssid_match = re.match(r"SSID \d+ : (.+)", line)  # 解析 SSID
            signal_match = re.match(r"Signal\s*:\s*(\d+)%", line)  # 解析 Signal

            if ssid_match:
                ssid = ssid_match.group(1)  # 记录 SSID

            if signal_match and ssid:
                signal_strength = int(signal_match.group(1))
                networks.append([ssid, signal_strength])
                ssid = None  # 处理完后清空 SSID，避免重复匹配

    else:
        raise NotImplementedError("Unsupported OS")

    df = pd.DataFrame(networks, columns=["SSID", "Signal"])

    # 确保 Signal 是整数型
    df["Signal"] = pd.to_numeric(df["Signal"], errors='coerce')
    df = df.dropna()  # 移除无效数据
    df["Signal"] = df["Signal"].astype(int)  # 确保 Signal 是 int

    return df


wifi_data = scan_wifi()

# 检查数据是否为空
if wifi_data.empty:
    print("No WiFi networks found!")
else:
    print(wifi_data)

    # 保存到 CSV
    wifi_data.to_csv("wifi_scan_results.csv", index=False)
    print("WiFi 扫描结果已保存到 wifi_scan_results.csv")

    # 绘制 WiFi 信号强度柱状图
    plt.figure(figsize=(10, 5))
    plt.bar(wifi_data["SSID"], wifi_data["Signal"], color='blue')
    plt.xlabel("WiFi SSID")
    plt.ylabel("Signal Strength (%)")
    plt.title("WiFi Signal Strength Comparison")
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.show()
