"""
设置对话框
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QSlider, QTimeEdit, QComboBox,
                             QGroupBox, QFormLayout, QSpinBox, QCheckBox)
from PyQt5.QtCore import Qt, QTime
from PyQt5.QtGui import QFont
from src.utils.config_manager import ConfigManager
from src.utils.data_manager import DataManager

class SettingsDialog(QDialog):
    """设置对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = ConfigManager()
        self.data_manager = DataManager()
        
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("系统设置")
        self.setFixedSize(500, 600)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # 刷牙设置组
        self.create_brush_settings_group(layout)
        
        # 音频设置组
        self.create_audio_settings_group(layout)
        
        # 摄像头设置组
        self.create_camera_settings_group(layout)
        
        # MQTT设置组
        self.create_mqtt_settings_group(layout)
        
        # 按钮组
        self.create_button_group(layout)
        
        self.setup_style()
        
    def create_brush_settings_group(self, parent_layout):
        """创建刷牙设置组"""
        group = QGroupBox("刷牙设置")
        layout = QFormLayout(group)
        
        # 早晨刷牙时间
        self.morning_time = QTimeEdit()
        self.morning_time.setDisplayFormat("HH:mm")
        layout.addRow("早晨提醒时间:", self.morning_time)
        
        # 晚上刷牙时间
        self.evening_time = QTimeEdit()
        self.evening_time.setDisplayFormat("HH:mm")
        layout.addRow("晚上提醒时间:", self.evening_time)
        
        # 刷牙时长
        self.brush_duration = QSpinBox()
        self.brush_duration.setRange(60, 300)
        self.brush_duration.setSuffix(" 秒")
        layout.addRow("刷牙总时长:", self.brush_duration)
        
        # 每步时长
        self.step_duration = QSpinBox()
        self.step_duration.setRange(15, 60)
        self.step_duration.setSuffix(" 秒")
        layout.addRow("每步时长:", self.step_duration)
        
        # 难度级别
        self.difficulty = QComboBox()
        self.difficulty.addItems(["简单", "普通", "困难"])
        layout.addRow("难度级别:", self.difficulty)
        
        parent_layout.addWidget(group)
        
    def create_audio_settings_group(self, parent_layout):
        """创建音频设置组"""
        group = QGroupBox("音频设置")
        layout = QFormLayout(group)
        
        # 音量设置
        volume_layout = QHBoxLayout()
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        
        self.volume_label = QLabel("80%")
        volume_layout.addWidget(self.volume_slider)
        volume_layout.addWidget(self.volume_label)
        
        layout.addRow("音量:", volume_layout)
        
        # 语音提醒开关
        self.voice_reminder = QCheckBox("启用语音提醒")
        layout.addRow("", self.voice_reminder)
        
        parent_layout.addWidget(group)
        
    def create_camera_settings_group(self, parent_layout):
        """创建摄像头设置组"""
        group = QGroupBox("摄像头设置")
        layout = QFormLayout(group)
        
        # 摄像头设备
        self.camera_device = QSpinBox()
        self.camera_device.setRange(0, 5)
        layout.addRow("摄像头设备ID:", self.camera_device)
        
        # 分辨率
        self.resolution = QComboBox()
        self.resolution.addItems(["640x480", "800x600", "1024x768", "1280x720"])
        layout.addRow("分辨率:", self.resolution)
        
        # 帧率
        self.fps = QSpinBox()
        self.fps.setRange(15, 60)
        self.fps.setSuffix(" fps")
        layout.addRow("帧率:", self.fps)
        
        parent_layout.addWidget(group)
        
    def create_mqtt_settings_group(self, parent_layout):
        """创建MQTT设置组"""
        group = QGroupBox("MQTT设置")
        layout = QFormLayout(group)
        
        # MQTT开关
        self.mqtt_enabled = QCheckBox("启用MQTT连接")
        layout.addRow("", self.mqtt_enabled)
        
        # 连接状态显示
        self.mqtt_status = QLabel("未连接")
        self.mqtt_status.setStyleSheet("color: red;")
        layout.addRow("连接状态:", self.mqtt_status)
        
        parent_layout.addWidget(group)
        
    def create_button_group(self, parent_layout):
        """创建按钮组"""
        button_layout = QHBoxLayout()
        
        # 恢复默认按钮
        reset_btn = QPushButton("恢复默认")
        reset_btn.clicked.connect(self.reset_to_defaults)
        
        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        
        # 确定按钮
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept_settings)
        ok_btn.setDefault(True)
        
        button_layout.addWidget(reset_btn)
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(ok_btn)
        
        parent_layout.addLayout(button_layout)
        
    def setup_style(self):
        """设置样式"""
        style = """
        QGroupBox {
            font-weight: bold;
            border: 2px solid #4ECDC4;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: #2C3E50;
        }
        
        QPushButton {
            background-color: #4ECDC4;
            border: none;
            border-radius: 6px;
            color: white;
            padding: 8px 16px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #45B7B8;
        }
        
        QPushButton:pressed {
            background-color: #3FBDB7;
        }
        
        QSlider::groove:horizontal {
            border: 1px solid #999999;
            height: 8px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);
            margin: 2px 0;
            border-radius: 4px;
        }
        
        QSlider::handle:horizontal {
            background: #4ECDC4;
            border: 1px solid #5c5c5c;
            width: 18px;
            margin: -2px 0;
            border-radius: 9px;
        }
        
        QSlider::handle:horizontal:hover {
            background: #45B7B8;
        }
        """
        
        self.setStyleSheet(style)
        
    def load_settings(self):
        """加载设置"""
        # 加载刷牙设置
        morning_time = self.config.get('brush_settings.morning_time', '08:00')
        evening_time = self.config.get('brush_settings.evening_time', '21:00')
        
        self.morning_time.setTime(QTime.fromString(morning_time, "HH:mm"))
        self.evening_time.setTime(QTime.fromString(evening_time, "HH:mm"))
        
        self.brush_duration.setValue(self.config.get('brush_settings.brush_duration', 120))
        self.step_duration.setValue(self.config.get('brush_settings.step_duration', 30))
        
        # 加载音频设置
        volume = int(self.config.get('audio.volume', 0.8) * 100)
        self.volume_slider.setValue(volume)
        self.volume_label.setText(f"{volume}%")
        
        # 加载摄像头设置
        self.camera_device.setValue(self.config.get('camera.device_id', 0))
        self.fps.setValue(self.config.get('camera.fps', 30))
        
        # 设置分辨率
        width = self.config.get('camera.width', 640)
        height = self.config.get('camera.height', 480)
        resolution_text = f"{width}x{height}"
        index = self.resolution.findText(resolution_text)
        if index >= 0:
            self.resolution.setCurrentIndex(index)
            
    def on_volume_changed(self, value):
        """音量改变处理"""
        self.volume_label.setText(f"{value}%")
        
    def accept_settings(self):
        """接受设置"""
        # 保存刷牙设置
        self.config.set('brush_settings.morning_time', self.morning_time.time().toString("HH:mm"))
        self.config.set('brush_settings.evening_time', self.evening_time.time().toString("HH:mm"))
        self.config.set('brush_settings.brush_duration', self.brush_duration.value())
        self.config.set('brush_settings.step_duration', self.step_duration.value())
        
        # 保存音频设置
        self.config.set('audio.volume', self.volume_slider.value() / 100.0)
        
        # 保存摄像头设置
        self.config.set('camera.device_id', self.camera_device.value())
        self.config.set('camera.fps', self.fps.value())
        
        # 解析分辨率
        resolution_text = self.resolution.currentText()
        if 'x' in resolution_text:
            width, height = map(int, resolution_text.split('x'))
            self.config.set('camera.width', width)
            self.config.set('camera.height', height)
        
        # 保存配置
        self.config.save()
        
        self.accept()
        
    def reset_to_defaults(self):
        """恢复默认设置"""
        self.morning_time.setTime(QTime.fromString("08:00", "HH:mm"))
        self.evening_time.setTime(QTime.fromString("21:00", "HH:mm"))
        self.brush_duration.setValue(120)
        self.step_duration.setValue(30)
        self.volume_slider.setValue(80)
        self.camera_device.setValue(0)
        self.fps.setValue(30)
        self.resolution.setCurrentText("640x480")