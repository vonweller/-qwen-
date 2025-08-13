"""
智能洗漱台系统 - 主程序入口
基于PyQt5的智能刷牙引导系统
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from src.ui.main_window import MainWindow

def main():
    """主程序入口"""
    # 在创建QApplication之前设置高DPI属性
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("智能洗漱台系统")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("SmartBrush")
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()