"""
位置状态显示组件 - 显示刷牙位置是否正确的UI提示
"""

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor

class PositionStatusWidget(QWidget):
    """位置状态显示组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
        # 警告闪烁定时器
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self.toggle_warning_visibility)
        self.blink_state = True
        
    def init_ui(self):
        """初始化用户界面"""
        self.setFixedSize(300, 80)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(5)
        
        # 状态图标和文本
        status_layout = QHBoxLayout()
        
        # 状态图标
        self.status_icon = QLabel("⚪")
        self.status_icon.setAlignment(Qt.AlignCenter)
        self.status_icon.setFixedSize(30, 30)
        self.status_icon.setStyleSheet("""
            QLabel {
                font-size: 20px;
                border-radius: 15px;
                background-color: #F0F0F0;
            }
        """)
        
        # 状态文本
        self.status_text = QLabel("等待开始刷牙...")
        self.status_text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.status_text.setWordWrap(True)
        self.status_text.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #666666;
                padding: 5px;
            }
        """)
        
        status_layout.addWidget(self.status_icon)
        status_layout.addWidget(self.status_text, 1)
        
        # 警告提示（默认隐藏）
        self.warning_label = QLabel()
        self.warning_label.setAlignment(Qt.AlignCenter)
        self.warning_label.setWordWrap(True)
        self.warning_label.setStyleSheet("""
            QLabel {
                background-color: #FF4444;
                color: white;
                font-size: 11px;
                font-weight: bold;
                padding: 3px 8px;
                border-radius: 3px;
                margin: 2px 0px;
            }
        """)
        self.warning_label.hide()
        
        layout.addLayout(status_layout)
        layout.addWidget(self.warning_label)
        
        # 设置整体样式
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
            }
        """)
    
    def update_position_status(self, is_correct, status_text):
        """更新位置状态显示"""
        if is_correct:
            # 位置正确 - 绿色
            self.status_icon.setText("✅")
            self.status_icon.setStyleSheet("""
                QLabel {
                    font-size: 20px;
                    border-radius: 15px;
                    background-color: #4CAF50;
                    color: white;
                }
            """)
            self.status_text.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #2E7D32;
                    font-weight: bold;
                    padding: 5px;
                }
            """)
            self.setStyleSheet("""
                QWidget {
                    background-color: #E8F5E8;
                    border: 2px solid #4CAF50;
                    border-radius: 8px;
                }
            """)
            
            # 停止警告闪烁
            self.stop_warning_blink()
            
        else:
            # 位置不正确 - 橙色警告
            self.status_icon.setText("⚠️")
            self.status_icon.setStyleSheet("""
                QLabel {
                    font-size: 20px;
                    border-radius: 15px;
                    background-color: #FF9800;
                    color: white;
                }
            """)
            self.status_text.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #E65100;
                    font-weight: bold;
                    padding: 5px;
                }
            """)
            self.setStyleSheet("""
                QWidget {
                    background-color: #FFF3E0;
                    border: 2px solid #FF9800;
                    border-radius: 8px;
                }
            """)
        
        self.status_text.setText(status_text)
    
    def show_warning(self, warning_text):
        """显示警告信息"""
        # 位置严重错误 - 红色闪烁
        self.status_icon.setText("❌")
        self.status_icon.setStyleSheet("""
            QLabel {
                font-size: 20px;
                border-radius: 15px;
                background-color: #F44336;
                color: white;
            }
        """)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #FFEBEE;
                border: 2px solid #F44336;
                border-radius: 8px;
            }
        """)
        
        # 显示警告文本并开始闪烁
        self.warning_label.setText(warning_text)
        self.warning_label.show()
        self.start_warning_blink()
    
    def start_warning_blink(self):
        """开始警告闪烁效果"""
        self.blink_timer.start(500)  # 每500ms闪烁一次
    
    def stop_warning_blink(self):
        """停止警告闪烁效果"""
        self.blink_timer.stop()
        self.warning_label.hide()
        self.blink_state = True
    
    def toggle_warning_visibility(self):
        """切换警告可见性（闪烁效果）"""
        self.blink_state = not self.blink_state
        if self.blink_state:
            self.warning_label.setStyleSheet("""
                QLabel {
                    background-color: #F44336;
                    color: white;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 3px 8px;
                    border-radius: 3px;
                    margin: 2px 0px;
                }
            """)
        else:
            self.warning_label.setStyleSheet("""
                QLabel {
                    background-color: #FFCDD2;
                    color: #D32F2F;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 3px 8px;
                    border-radius: 3px;
                    margin: 2px 0px;
                }
            """)
    
    def reset_status(self):
        """重置状态显示"""
        self.status_icon.setText("⚪")
        self.status_icon.setStyleSheet("""
            QLabel {
                font-size: 20px;
                border-radius: 15px;
                background-color: #F0F0F0;
            }
        """)
        self.status_text.setText("等待开始刷牙...")
        self.status_text.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #666666;
                padding: 5px;
            }
        """)
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
            }
        """)
        self.stop_warning_blink()