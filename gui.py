import tkinter as tk
from tkinter import ttk
from wifi_scanner import scan_wifi
import os


def get_version():
    """ 从 version.txt 读取版本号 """
    version_file = "version.txt"
    if os.path.exists(version_file):
        with open(version_file, "r") as f:
            return f.read().strip()
    return "Unknown Version"


class WiFiScannerApp:

    def __init__(self, root):
        self.sort_descending = None
        self.root = root
        self.root.title(f"Wi-Fi Signal Testing Tool - v{get_version()}")
        self.root.geometry("400x300")


        # self.sort_descending = True  # 默认信号强的排在前

        # create data table
        columns = ("SSID", "Signal Strength")
        self.tree = ttk.Treeview(root, columns=columns, show="headings")
        self.tree.heading("SSID", text="WiFi name")
        self.tree.heading("Signal Strength", text="Signal Strength (%)")
        self.tree.pack(fill="both", expand=True)

        # button area
        btn_frame = tk.Frame(root)
        btn_frame.pack(fill="x")

        self.refresh_btn = tk.Button(btn_frame, text="Refresh Signal", command=self.update_table)
        self.refresh_btn.pack(side="left", expand=True)

        self.sort_btn = tk.Button(btn_frame, text="Switch asc/des", command=self.toggle_sort)
        self.sort_btn.pack(side="right", expand=True)

        # first load Wi-Fi data
        self.update_table()

    def update_table(self):
        """ update the table """
        wifi_data = scan_wifi()
        if wifi_data.empty:
            return

        # sort the data in ascending/descending based on the given Wi-Fi strength
        wifi_data = wifi_data.sort_values(by="Signal", ascending=not self.sort_descending)

        # clear the table
        for item in self.tree.get_children():
            self.tree.delete(item)

        # insert data
        for index, row in wifi_data.iterrows():
            self.tree.insert("", "end", values=(row["SSID"], row["Signal"]))

    def toggle_sort(self):
        """ switch the sorting method """
        self.sort_descending = not self.sort_descending
        self.update_table()


def start_gui():
    """ start Tkinter GUI """
    root = tk.Tk()
    app = WiFiScannerApp(root)
    root.mainloop()
