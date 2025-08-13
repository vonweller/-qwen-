"""
主窗口界面
"""

import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QFrame, QGridLayout, QProgressBar,
                             QStackedWidget, QScrollArea)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap, QPainter, QBrush
from src.ui.camera_widget import CameraWidget
from src.ui.settings_dialog import SettingsDialog
from src.ui.records_widget import RecordsWidget
from src.ui.brush_animation import BrushAnimationWidget
from src.ui.rating_widget import RatingWidget
from src.ui.main_window_styles import MAIN_WINDOW_STYLE
from src.core.brush_controller import BrushController
from src.core.brush_position_monitor import BrushPositionMonitor
from src.ui.position_status_widget import PositionStatusWidget
from src.utils.config_manager import ConfigManager

class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.brush_controller = BrushController()
        
        # 连接信号
        self.brush_controller.status_changed.connect(self.on_status_changed)
        self.brush_controller.progress_updated.connect(self.on_progress_updated)
        self.brush_controller.brushing_started.connect(self.on_brushing_started)
        self.brush_controller.brushing_completed.connect(self.on_brushing_completed)
        self.brush_controller.step_changed.connect(self.on_step_changed)
        self.brush_controller.analysis_completed.connect(self.on_analysis_completed)
        self.brush_controller.analysis_status_changed.connect(self.update_analysis_status)
        self.brush_controller.countdown_updated.connect(self.on_countdown_updated)
        
        self.init_ui()
        self.setup_style()
        
        # 将摄像头组件传递给刷牙控制器，并设置相互引用
        self.brush_controller.set_camera_widget(self.camera_widget)
        self.camera_widget.set_brush_controller(self.brush_controller)
        
        # 初始化位置监控器
        self.position_monitor = BrushPositionMonitor()
        self.position_monitor.position_status_changed.connect(self.on_position_status_changed)
        
        # 连接姿态检测信号
        self.camera_widget.pose_detected.connect(self.on_pose_detected)
        self.camera_widget.pose_detected.connect(self.position_monitor.update_pose_data)
        
        # 从配置加载姿态检测设置
        pose_enabled = self.config.get('camera.pose_detection.enabled', True)
        self.camera_widget.toggle_pose_detection(pose_enabled)
        
        confidence = self.config.get('camera.pose_detection.confidence_threshold', 0.5)
        self.camera_widget.set_pose_detection_confidence(confidence)
        
        print(f"姿态检测功能: {'启用' if pose_enabled else '禁用'}")
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle(self.config.get('app.name', '智能洗漱台系统'))
        # 设置更合适的窗口大小
        self.setGeometry(100, 100, 900, 600)
        self.setMinimumSize(900, 600)
        self.setMaximumSize(1100, 750)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # 创建顶部状态栏
        self.create_top_bar(main_layout)
        
        # 创建中央内容区域
        self.create_central_area(main_layout)
        
        # 创建底部控制面板
        self.create_bottom_panel(main_layout)
        
    def create_top_bar(self, parent_layout):
        """创建顶部状态栏"""
        top_frame = QFrame()
        top_frame.setFixedHeight(50)
        top_frame.setObjectName("topBar")
        
        top_layout = QHBoxLayout(top_frame)
        top_layout.setContentsMargins(15, 8, 15, 8)
        
        # 时间日期显示
        self.time_label = QLabel()
        self.time_label.setObjectName("timeLabel")
        self.update_time()
        
        # 定时器更新时间
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)
        
        # 天气信息
        self.weather_label = QLabel("获取天气中...")
        self.weather_label.setObjectName("weatherLabel")
        
        # 初始化天气API
        from src.utils.weather_api import WeatherAPI
        self.weather_api = WeatherAPI()
        
        # 启动天气更新定时器
        self.weather_timer = QTimer()
        self.weather_timer.timeout.connect(self.update_weather)
        self.weather_timer.start(300000)  # 每5分钟更新一次
        
        # 立即更新一次天气
        self.update_weather()
        
        # 设置按钮
        settings_btn = QPushButton("⚙️ 设置")
        settings_btn.setObjectName("settingsBtn")
        settings_btn.clicked.connect(self.show_settings)
        
        top_layout.addWidget(self.time_label)
        top_layout.addStretch()
        top_layout.addWidget(self.weather_label)
        top_layout.addWidget(settings_btn)
        
        parent_layout.addWidget(top_frame)
        
    def create_central_area(self, parent_layout):
        """创建中央内容区域"""
        central_frame = QFrame()
        central_frame.setObjectName("centralFrame")
        
        central_layout = QHBoxLayout(central_frame)
        central_layout.setContentsMargins(10, 10, 10, 10)
        central_layout.setSpacing(15)
        
        # 创建主要内容区域
        content_frame = QFrame()
        content_layout = QHBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)
        
        # 左侧：动画引导区域容器
        left_container = QFrame()
        left_container.setStyleSheet("""
            QFrame {
                border: 2px solid #4ECDC4;
                border-radius: 10px;
                background-color: #F8F9FA;
            }
        """)
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(5, 5, 5, 5)
        left_layout.setSpacing(0)
        
        self.animation_widget = BrushAnimationWidget()
        self.animation_widget.hide()  # 默认隐藏
        
        # 添加占位标签
        self.animation_placeholder = QLabel("开始刷牙引导\n\n请跟随动画指示进行刷牙")
        self.animation_placeholder.setAlignment(Qt.AlignCenter)
        self.animation_placeholder.setStyleSheet("""
            QLabel {
                border: none;
                color: #6C757D;
                font-size: 16px;
            }
        """)
        
        # 倒计时显示标签
        self.countdown_label = QLabel("")
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setStyleSheet("""
            QLabel {
                border: none;
                color: #007BFF;
                font-size: 24px;
                font-weight: bold;
                background-color: rgba(255, 255, 255, 0.8);
                border-radius: 15px;
                padding: 10px;
                margin: 10px;
            }
        """)
        self.countdown_label.hide()  # 默认隐藏
        
        # 使用堆叠布局，确保动画和占位标签占用相同空间
        left_layout.addWidget(self.animation_placeholder, 1)
        left_layout.addWidget(self.animation_widget, 1)
        left_layout.addWidget(self.countdown_label, 0, Qt.AlignTop | Qt.AlignCenter)
        
        # 右侧：摄像头显示区域容器
        right_container = QFrame()
        right_container.setStyleSheet("""
            QFrame {
                border: 2px solid #4ECDC4;
                border-radius: 10px;
                background-color: #F8F9FA;
            }
        """)
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(5, 5, 5, 5)
        right_layout.setSpacing(5)
        
        # 摄像头区域
        self.camera_widget = CameraWidget()
        right_layout.addWidget(self.camera_widget, 2)  # 占2/3空间
        
        # 位置状态显示组件
        self.position_status_widget = PositionStatusWidget()
        right_layout.addWidget(self.position_status_widget, 0)  # 固定高度
        
        # 分析结果显示区域
        self.create_analysis_display(right_layout)
        
        # 评分显示区域（覆盖整个内容区域）
        self.rating_widget = RatingWidget()
        self.rating_widget.setMinimumSize(490, 320)
        self.rating_widget.hide()  # 默认隐藏
        
        # 确保两个容器大小完全相同，各占50%
        content_layout.addWidget(left_container, 1)   # 50%
        content_layout.addWidget(right_container, 1)  # 50%
        
        # 侧边信息栏
        self.create_side_panel(central_layout)
        
        central_layout.addWidget(content_frame, 2)
        
        parent_layout.addWidget(central_frame, 1)
        
    def create_side_panel(self, parent_layout):
        """创建侧边信息栏"""
        side_frame = QFrame()
        side_frame.setFixedWidth(240)
        side_frame.setObjectName("sidePanel")
        
        side_layout = QVBoxLayout(side_frame)
        side_layout.setContentsMargins(10, 10, 10, 10)
        side_layout.setSpacing(8)
        
        # 刷牙步骤指示器 - 放在最上面
        self.create_step_indicators(side_layout)
        
        # 今日目标卡片
        target_card = self.create_card("今日目标", "早晚刷牙 2/2")
        
        # 进度显示
        progress_frame = QFrame()
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setContentsMargins(5, 5, 5, 5)
        progress_layout.setSpacing(3)
        
        progress_label = QLabel("刷牙进度")
        progress_label.setObjectName("progressLabel")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(12)
        
        progress_layout.addWidget(progress_label)
        progress_layout.addWidget(self.progress_bar)
        
        # 成就展示
        achievement_card = self.create_card("最近成就", "连续刷牙 7 天")
        
        # 健康小贴士
        tips_card = self.create_card("健康小贴士", "每次刷牙至少2分钟")
        
        # MQTT消息显示区域
        self.create_mqtt_display(side_layout)
        
        side_layout.addWidget(target_card)
        side_layout.addWidget(progress_frame)
        side_layout.addWidget(achievement_card)
        side_layout.addWidget(tips_card)
        side_layout.addStretch()
        
        parent_layout.addWidget(side_frame)
        
    def create_step_indicators(self, parent_layout):
        """创建刷牙步骤指示器"""
        steps_frame = QFrame()
        steps_frame.setObjectName("stepsFrame")
        steps_frame.setFixedHeight(65)
        
        steps_layout = QGridLayout(steps_frame)
        steps_layout.setContentsMargins(8, 8, 8, 8)
        steps_layout.setSpacing(4)
        
        self.step_indicators = {}
        steps = ["上左", "上中", "上右", "下左", "下中", "下右"]
        positions = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]
        
        for step, pos in zip(steps, positions):
            indicator = QLabel(step)
            indicator.setObjectName("stepIndicator")
            indicator.setAlignment(Qt.AlignCenter)
            indicator.setFixedSize(65, 22)
            self.step_indicators[step] = indicator
            steps_layout.addWidget(indicator, pos[0], pos[1])
        
        parent_layout.addWidget(steps_frame)
        
    def create_mqtt_display(self, parent_layout):
        """创建MQTT消息显示区域"""
        mqtt_frame = QFrame()
        mqtt_frame.setObjectName("mqttFrame")
        mqtt_frame.setFixedHeight(80)
        
        mqtt_layout = QVBoxLayout(mqtt_frame)
        mqtt_layout.setContentsMargins(8, 5, 8, 5)
        mqtt_layout.setSpacing(3)
        
        # MQTT标题
        mqtt_title = QLabel("MQTT消息")
        mqtt_title.setObjectName("mqttTitle")
        
        # MQTT消息显示
        self.mqtt_message_label = QLabel("等待MQTT消息...")
        self.mqtt_message_label.setObjectName("mqttMessage")
        self.mqtt_message_label.setWordWrap(True)
        self.mqtt_message_label.setAlignment(Qt.AlignTop)
        
        mqtt_layout.addWidget(mqtt_title)
        mqtt_layout.addWidget(self.mqtt_message_label, 1)
        
        parent_layout.addWidget(mqtt_frame)
        
        # 连接MQTT信号
        if hasattr(self.brush_controller, 'mqtt_client') and self.brush_controller.mqtt_client:
            self.brush_controller.mqtt_client.message_received.connect(self.on_mqtt_message_received)
            # 连接MQTT刷牙控制信号
            self.brush_controller.mqtt_client.start_brushing_requested.connect(self.on_mqtt_start_brushing)
            self.brush_controller.mqtt_client.stop_brushing_requested.connect(self.on_mqtt_stop_brushing)
            print("MQTT刷牙控制信号已连接")
    
    def create_analysis_display(self, parent_layout):
        """创建分析结果显示区域"""
        analysis_frame = QFrame()
        analysis_frame.setObjectName("analysisFrame")
        analysis_frame.setMinimumHeight(120)
        analysis_frame.setMaximumHeight(150)
        
        analysis_layout = QVBoxLayout(analysis_frame)
        analysis_layout.setContentsMargins(8, 5, 8, 5)
        analysis_layout.setSpacing(3)
        
        # 分析结果标题
        analysis_title = QLabel("🤖 AI分析结果")
        analysis_title.setObjectName("analysisTitle")
        
        # 分析状态显示
        self.analysis_status_label = QLabel("等待分析...")
        self.analysis_status_label.setObjectName("analysisStatus")
        
        # 评分显示
        score_layout = QHBoxLayout()
        score_layout.setContentsMargins(0, 0, 0, 0)
        score_layout.setSpacing(10)
        
        self.score_label = QLabel("得分: --")
        self.score_label.setObjectName("scoreLabel")
        
        self.accuracy_label = QLabel("准确度: --")
        self.accuracy_label.setObjectName("accuracyLabel")
        
        score_layout.addWidget(self.score_label)
        score_layout.addWidget(self.accuracy_label)
        score_layout.addStretch()
        
        # 反馈信息显示 - 分为两部分
        feedback_container = QFrame()
        feedback_layout = QVBoxLayout(feedback_container)
        feedback_layout.setContentsMargins(0, 0, 0, 0)
        feedback_layout.setSpacing(2)
        
        # 简要状态显示
        self.feedback_label = QLabel("开始刷牙后将显示AI分析反馈")
        self.feedback_label.setObjectName("feedbackLabel")
        self.feedback_label.setWordWrap(True)
        self.feedback_label.setAlignment(Qt.AlignTop)
        self.feedback_label.setMaximumHeight(40)
        
        # 详细反馈内容显示
        self.detailed_feedback_label = QLabel("详细分析结果将在这里显示")
        self.detailed_feedback_label.setObjectName("detailedFeedbackLabel")
        self.detailed_feedback_label.setWordWrap(True)
        self.detailed_feedback_label.setAlignment(Qt.AlignTop)
        self.detailed_feedback_label.setStyleSheet("""
            QLabel#detailedFeedbackLabel {
                background-color: #F8F9FA;
                border: 1px solid #DEE2E6;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
                color: #495057;
            }
        """)
        
        feedback_layout.addWidget(self.feedback_label)
        feedback_layout.addWidget(self.detailed_feedback_label, 1)
        
        analysis_layout.addWidget(analysis_title)
        analysis_layout.addWidget(self.analysis_status_label)
        analysis_layout.addLayout(score_layout)
        analysis_layout.addWidget(feedback_container, 1)
        
        parent_layout.addWidget(analysis_frame, 1)  # 占1/3空间
        
        # 连接分析结果信号
        if hasattr(self.brush_controller, 'analysis_completed'):
            self.brush_controller.analysis_completed.connect(self.on_analysis_completed)
        
    def create_bottom_panel(self, parent_layout):
        """创建底部控制面板"""
        bottom_frame = QFrame()
        bottom_frame.setFixedHeight(80)
        bottom_frame.setObjectName("bottomPanel")
        
        bottom_layout = QHBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(20, 12, 20, 12)
        bottom_layout.setSpacing(25)
        
        # 开始刷牙按钮
        self.start_btn = QPushButton("🦷 开始刷牙")
        self.start_btn.setObjectName("startBtn")
        self.start_btn.setFixedSize(140, 50)
        self.start_btn.clicked.connect(self.start_brushing)
        
        # 状态显示
        self.status_label = QLabel("准备就绪")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        # 记录查看按钮
        records_btn = QPushButton("📊 查看记录")
        records_btn.setObjectName("recordsBtn")
        records_btn.setFixedSize(110, 40)
        records_btn.clicked.connect(self.show_records)
        
        bottom_layout.addWidget(self.start_btn)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.status_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(records_btn)
        
        parent_layout.addWidget(bottom_frame)
        
    def create_card(self, title, content):
        """创建信息卡片"""
        card = QFrame()
        card.setObjectName("infoCard")
        card.setFixedHeight(55)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(8, 4, 8, 4)
        card_layout.setSpacing(2)
        
        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        
        content_label = QLabel(content)
        content_label.setObjectName("cardContent")
        content_label.setWordWrap(True)
        
        card_layout.addWidget(title_label)
        card_layout.addWidget(content_label)
        
        return card
        
    def setup_style(self):
        """设置样式"""
        self.setStyleSheet(MAIN_WINDOW_STYLE)
        
    def update_time(self):
        """更新时间显示"""
        from datetime import datetime
        now = datetime.now()
        time_str = now.strftime("%Y年%m月%d日 %H:%M:%S")
        self.time_label.setText(time_str)
        
    def update_weather(self):
        """更新天气显示"""
        try:
            weather_info = self.weather_api.get_weather_info()
            weather_text = f"{weather_info['icon']} {weather_info['weather']} {weather_info['temperature']}°C"
            self.weather_label.setText(weather_text)
            print(f"天气更新: {weather_text}")
        except Exception as e:
            print(f"天气更新失败: {e}")
            self.weather_label.setText("🌤️ 天气获取失败")
        
    def start_brushing(self):
        """开始刷牙"""
        if self.start_btn.text() == "🦷 开始刷牙":
            self.brush_controller.start_brushing()
            self.start_btn.setText("⏹️ 停止刷牙")
        else:
            self.brush_controller.stop_brushing()
            self.start_btn.setText("🦷 开始刷牙")
            # 停止时隐藏动画、评分和倒计时
            self.animation_widget.hide()
            self.rating_widget.hide()
            self.countdown_label.hide()
            self.animation_placeholder.show()
            
    def show_settings(self):
        """显示设置对话框"""
        dialog = SettingsDialog(self)
        dialog.exec_()
        
    def show_records(self):
        """显示记录窗口"""
        self.records_widget = RecordsWidget()
        self.records_widget.show()
        
    def on_status_changed(self, status):
        """状态改变处理"""
        self.status_label.setText(status)
        
    def on_progress_updated(self, progress):
        """进度更新处理"""
        # 将0-1的进度值转换为0-100的百分比
        if progress <= 1.0:
            progress_percent = int(progress * 100)
        else:
            progress_percent = int(progress)
        
        # 确保进度值在0-100范围内
        progress_percent = max(0, min(100, progress_percent))
        self.progress_bar.setValue(progress_percent)
        print(f"进度更新: {progress} -> {progress_percent}%")
        
    def update_step_indicator(self, step, active=False):
        """更新步骤指示器"""
        if step in self.step_indicators:
            indicator = self.step_indicators[step]
            indicator.setProperty("active", active)
            indicator.style().unpolish(indicator)
            indicator.style().polish(indicator)
    
    def on_brushing_started(self):
        """刷牙开始处理"""
        # 隐藏占位标签，显示动画引导
        self.animation_placeholder.hide()
        self.animation_widget.show()
        self.animation_widget.start_animation()
        
        # 显示倒计时标签
        self.countdown_label.show()
        
        # 隐藏评分组件
        self.rating_widget.hide()
        
        # 更新状态
        self.status_label.setText("正在刷牙...")
        
    def on_brushing_completed(self, score, stars):
        """刷牙完成处理"""
        print(f"刷牙完成处理: 得分={score}, 星级={stars}")
        
        # 停止并隐藏动画，显示占位标签
        self.animation_widget.stop_animation()
        self.animation_widget.hide()
        self.animation_placeholder.show()
        
        # 隐藏倒计时标签
        self.countdown_label.hide()
        
        # 确保评分组件存在并正确显示
        if hasattr(self, 'rating_widget') and self.rating_widget:
            print("显示评分界面")
            self.rating_widget.show()
            self.rating_widget.raise_()  # 确保在最前面
            self.rating_widget.show_rating(score, stars)
        else:
            print("评分组件不存在，创建新的")
            from src.ui.rating_widget import RatingWidget
            self.rating_widget = RatingWidget()
            self.rating_widget.setParent(self)
            self.rating_widget.show()
            self.rating_widget.show_rating(score, stars)
        
        # 更新状态
        self.status_label.setText(f"刷牙完成！得分: {score}分，{stars}星")
        
        # 重置按钮
        self.start_btn.setText("🦷 开始刷牙")
        
        # 延长显示时间到8秒，让用户有足够时间查看结果
        QTimer.singleShot(8000, self.reset_to_normal_view)
        
    def reset_to_normal_view(self):
        """重置到正常视图"""
        self.rating_widget.hide()
        # 确保显示占位标签
        self.animation_placeholder.show()
        
    def on_step_changed(self, step, is_active):
        """刷牙步骤改变处理"""
        print(f"步骤改变: {step}, 激活状态: {is_active}")
        
        if is_active:
            # 更新动画显示 - 直接调用update_step方法避免重复
            if hasattr(self.animation_widget, 'update_step'):
                self.animation_widget.update_step(step, is_active)
            
            # 更新步骤指示器 - 高亮当前步骤
            for step_name in self.step_indicators:
                self.update_step_indicator(step_name, step_name == step)
        else:
            # 步骤结束，取消高亮
            self.update_step_indicator(step, False)
            
    def on_countdown_updated(self, remaining_seconds, is_last_10_seconds):
        """倒计时更新处理"""
        if remaining_seconds > 0:
            # 显示倒计时
            self.countdown_label.setText(f"⏰ {remaining_seconds}秒")
            self.countdown_label.show()
            
            # 最后10秒时变大变红
            if is_last_10_seconds:
                self.countdown_label.setStyleSheet("""
                    QLabel {
                        border: none;
                        color: #FF4444;
                        font-size: 36px;
                        font-weight: bold;
                        background-color: rgba(255, 255, 255, 0.9);
                        border-radius: 20px;
                        padding: 15px;
                        margin: 10px;
                    }
                """)
            else:
                self.countdown_label.setStyleSheet("""
                    QLabel {
                        border: none;
                        color: #007BFF;
                        font-size: 24px;
                        font-weight: bold;
                        background-color: rgba(255, 255, 255, 0.8);
                        border-radius: 15px;
                        padding: 10px;
                        margin: 10px;
                    }
                """)
        else:
            # 倒计时结束，隐藏标签
            self.countdown_label.hide()
    
    def on_pose_detected(self, pose_analysis):
        """处理姿态检测结果"""
        try:
            print(f"收到姿态检测结果: {pose_analysis}")
            
            # 可以在这里添加姿态分析的逻辑
            # 例如：检测刷牙姿势是否正确，手臂位置等
            
            # 更新界面显示姿态信息（可选）
            if hasattr(self, 'pose_info_label'):
                pose_info = f"姿态: {pose_analysis.get('pose_type', '未知')}"
                self.pose_info_label.setText(pose_info)
                
        except Exception as e:
            print(f"姿态检测结果处理错误: {e}")
    
    def on_position_status_changed(self, is_correct_position, confidence, message):
    def on_position_status_changed(self, is_correct_position, confidence, message):
        """处理位置状态变化"""
        try:
            print(f"位置状态变化: 正确位置={is_correct_position}, 置信度={confidence:.2f}, 消息={message}")
            
            # 更新位置状态显示组件
            if hasattr(self, 'position_status_widget'):
                self.position_status_widget.update_status(is_correct_position, confidence, message)
                
        except Exception as e:
            print(f"位置状态处理错误: {e}")
    
    def on_mqtt_message_received(self, topic, message):
        """处理接收到的MQTT消息"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        display_text = f"[{timestamp}] {topic}: {message}"
        self.mqtt_message_label.setText(display_text)
        
    def on_mqtt_start_brushing(self):
        """MQTT控制开始刷牙"""
        print("收到MQTT开始刷牙指令")
        if self.start_btn.text() == "🦷 开始刷牙":
            self.start_brushing()
            
    def on_mqtt_stop_brushing(self):
        """MQTT控制停止刷牙"""
        print("收到MQTT停止刷牙指令")
        if self.start_btn.text() == "⏹️ 停止刷牙":
            self.start_brushing()  # 这会调用停止逻辑
        
    def on_analysis_completed(self, step_name, result):
        """处理分析结果"""
        print(f"收到分析结果: step_name={step_name}, result={result}")
        
        if result:
            # 更新分析状态
            self.analysis_status_label.setText("✅ 分析完成")
            
            # 简单处理分析结果
            try:
                if isinstance(result, str) and result in ["上左", "上中", "上右", "下左", "下中", "下右", "综合评价"]:
                    print(f"跳过步骤名称: {result}")
                    return
                
                # 设置默认值
                score = 0
                is_correct = False
                feedback = "动作分析完成"
                
                # 更新显示
                self.score_label.setText(f"得分: {score}")
                accuracy_text = "✅ 规范" if is_correct else "⚠️ 需改进"
                self.accuracy_label.setText(f"准确度: {accuracy_text}")
                
                # 显示简要状态
                status_text = f"✅ 动作分析完成"
                self.feedback_label.setText(status_text)
                
                # 显示详细反馈
                self.detailed_feedback_label.setText(feedback)
                
            except Exception as e:
                print(f"分析结果处理错误: {e}")
                self.feedback_label.setText("分析结果处理出错")
            
        else:
            self.analysis_status_label.setText("❌ 分析失败")
            self.feedback_label.setText("分析服务暂时不可用")
            
    def update_analysis_status(self, status):
        """更新分析状态"""
        self.analysis_status_label.setText(status)
    
    def toggle_pose_detection_ui(self):
        """切换姿态检测功能的UI控制"""
        if hasattr(self, 'camera_widget'):
            current_state = getattr(self.camera_widget, 'enable_pose_detection', False)
            self.camera_widget.toggle_pose_detection(not current_state)
            print(f"姿态检测已{'开启' if not current_state else '关闭'}")
