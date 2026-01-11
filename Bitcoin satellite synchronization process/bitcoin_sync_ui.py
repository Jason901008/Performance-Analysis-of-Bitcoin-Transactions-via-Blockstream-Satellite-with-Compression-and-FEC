import sys
import json
import time
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

# ====== 資料儲存區 ======
MAX_POINTS_HEIGHT_TX = 10
MAX_POINTS_OTHERS = 30

# 分開兩組時間軸，避免互相影響
times_htx, times_others = [], []
heights, tx_counts, sync_progresses = [], [], []
block_sizes, tx_densities, disk_usages = [], [], []


def run_cli(cmd):
    """執行 bitcoin-cli 並回傳 JSON 結果"""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)


def update_data():
    """更新比特幣區塊鏈資料"""
    info = run_cli(["bitcoin-cli", "getblockchaininfo"])
    besthash = info["bestblockhash"]
    block = run_cli(["bitcoin-cli", "getblock", besthash, "2"])

    now = time.strftime("%H:%M:%S")
    size = block.get("size", 0)
    tx_count = len(block.get("tx", []))
    tx_density = tx_count / size if size else 0

    # --- 新增資料 ---
    times_htx.append(now)
    times_others.append(now)
    heights.append(info["blocks"])
    tx_counts.append(tx_count)
    sync_progresses.append(info["verificationprogress"])
    block_sizes.append(size)
    tx_densities.append(tx_density)
    disk_usages.append(info["size_on_disk"] / (1024 * 1024))  # MB

    # --- 限制筆數（分開設定）---
    if len(heights) > MAX_POINTS_HEIGHT_TX:
        heights.pop(0)
        times_htx.pop(0)
    if len(tx_counts) > MAX_POINTS_HEIGHT_TX:
        tx_counts.pop(0)

    for lst in [sync_progresses, block_sizes, tx_densities, disk_usages]:
        if len(lst) > MAX_POINTS_OTHERS:
            lst.pop(0)
    if len(times_others) > MAX_POINTS_OTHERS:
        times_others.pop(0)


# ====== 主視窗 ======
class BitcoinTabs(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bitcoin Blockchain Charts - Tabs v2")
        self.setGeometry(100, 100, 1400, 800)
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # 建立四個分頁
        self.tab1, self.tab2, self.tab3, self.tab4 = QWidget(), QWidget(), QWidget(), QWidget()
        self.tabs.addTab(self.tab1, "區塊高度/交易/同步")
        self.tabs.addTab(self.tab2, "區塊大小")
        self.tabs.addTab(self.tab3, "交易密度")
        self.tabs.addTab(self.tab4, "磁碟使用量")

        # 初始化各分頁
        self.init_tab1()
        self.init_tab2()
        self.init_tab3()
        self.init_tab4()

        # 啟動定時更新
        self.refresh_loop()

    # --- Tab1: 區塊高度 / 交易數 / 同步 ---
    def init_tab1(self):
        self.layout1 = QVBoxLayout()
        self.fig1, (self.ax1, self.ax2, self.ax3) = plt.subplots(1, 3, figsize=(18, 6))
        plt.subplots_adjust(top=0.85, wspace=0.4)

        title = (
            "Satellite Name: Telstar 18V Ku Band | Receiver Vendor: Novra | Receiver Model: S400\n"
            "Network Device: ens33 | Antenna Label: 90cm / 36in | LNB Vendor: GEOSATpro"
        )
        self.fig1.suptitle(title, fontsize=10, y=0.95)

        self.canvas1 = FigureCanvas(self.fig1)
        self.layout1.addWidget(self.canvas1)
        self.tab1.setLayout(self.layout1)

    # --- Tab2: 區塊大小 ---
    def init_tab2(self):
        self.layout2 = QVBoxLayout()
        self.fig2, self.ax2_1 = plt.subplots(figsize=(10, 5))
        self.canvas2 = FigureCanvas(self.fig2)
        self.layout2.addWidget(self.canvas2)
        self.tab2.setLayout(self.layout2)

    # --- Tab3: 交易密度 ---
    def init_tab3(self):
        self.layout3 = QVBoxLayout()
        self.fig3, self.ax3_1 = plt.subplots(figsize=(10, 5))
        self.canvas3 = FigureCanvas(self.fig3)
        self.layout3.addWidget(self.canvas3)
        self.tab3.setLayout(self.layout3)

    # --- Tab4: 磁碟使用量 ---
    def init_tab4(self):
        self.layout4 = QVBoxLayout()
        self.fig4, self.ax4_1 = plt.subplots(figsize=(10, 5))
        self.canvas4 = FigureCanvas(self.fig4)
        self.layout4.addWidget(self.canvas4)
        self.tab4.setLayout(self.layout4)

    # --- 定時刷新 ---
    def refresh_loop(self):
        try:
            update_data()
            self.update_tab1()
            self.update_tab2()
            self.update_tab3()
            self.update_tab4()

            self.canvas1.draw()
            self.canvas2.draw()
            self.canvas3.draw()
            self.canvas4.draw()
        except Exception as e:
            print(f"[錯誤] {e}")
        QTimer.singleShot(5000, self.refresh_loop)

    # --- 更新分頁內容 ---
    def update_tab1(self):
        # 區塊高度
        self.ax1.cla()
        self.ax1.plot(times_htx, heights, 'r-', label="Block Height", linewidth=2, alpha=0.8, marker='o')
        self.ax1.set_ylabel("Block Height", color="red", fontsize=12)
        self.ax1.tick_params(axis='y', labelcolor="red")
        self.ax1.grid(True, linestyle='--', alpha=0.5)
        self.ax1.set_title("Bitcoin Blockchain Data - Block Height", fontsize=14)
        self.ax1.tick_params(axis='x', rotation=45)
        self.ax1.legend()

        # 區塊交易數
        self.ax2.cla()
        self.ax2.plot(times_htx, tx_counts, 'b--', label="Total Transactions", linewidth=2, alpha=0.8, marker='s')
        self.ax2.set_ylabel("Total Transactions", color="blue", fontsize=12)
        self.ax2.tick_params(axis='y', labelcolor="blue")
        self.ax2.grid(True, linestyle='--', alpha=0.5)
        self.ax2.set_title("Bitcoin Blockchain Data - Total Transactions", fontsize=14)
        self.ax2.tick_params(axis='x', rotation=45)
        self.ax2.legend()

        # 同步進度圓餅圖
        self.ax3.cla()
        p = sync_progresses[-1] if sync_progresses else 0
        self.ax3.pie([p * 100, (1 - p) * 100], labels=["Completed", "Remaining"],
                     colors=["green", "red"], autopct='%1.1f%%', startangle=90)
        self.ax3.set_title("Blockchain Sync Progress", fontsize=14)

    def update_tab2(self):
        self.ax2_1.cla()
        self.ax2_1.plot(times_others, block_sizes, 'c-o', label="Block Size (bytes)")
        self.ax2_1.set_title("Block Size Over Time")
        self.ax2_1.set_ylabel("Bytes")
        self.ax2_1.tick_params(axis='x', rotation=45)
        self.ax2_1.grid(True)
        self.ax2_1.legend()

    def update_tab3(self):
        self.ax3_1.cla()
        self.ax3_1.plot(times_others, tx_densities, 'm-^', label="Tx Density (tx/byte)")
        self.ax3_1.set_title("Transaction Density Over Time")
        self.ax3_1.set_ylabel("Tx / Byte")
        self.ax3_1.tick_params(axis='x', rotation=45)
        self.ax3_1.grid(True)
        self.ax3_1.legend()

    def update_tab4(self):
        self.ax4_1.cla()
        self.ax4_1.plot(times_others, disk_usages, 'g-s', label="Disk Usage (MB)")
        self.ax4_1.set_title("Blockchain Size on Disk")
        self.ax4_1.set_ylabel("Size (MB)")
        self.ax4_1.tick_params(axis='x', rotation=45)
        self.ax4_1.grid(True)
        self.ax4_1.legend()


# ====== 主程式啟動 ======
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BitcoinTabs()
    window.show()
    sys.exit(app.exec_())

