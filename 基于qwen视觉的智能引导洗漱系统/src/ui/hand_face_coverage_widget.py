"""
手掌-脸部覆盖检测可视化组件
实现实时UI反馈：绿色表示正确覆盖，红色表示未正确覆盖
"""

import cv2
import numpy as np
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor

class HandFaceCoverageWidget(QWidget):
    """手掌-脸部覆盖检测UI组件"""
    
    # 信号定义
    coverage_status_changed = pyqtSignal(bool, float, str)  # 覆盖状态, 置信度, 消息
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_coverage_status = False
        self.current_confidence = 0.0
        self.response_time_threshold = 200  # 200ms响应时间要求
        
        # 状态闪烁定时器
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self.toggle_warning_blink)
        self.blink_state = True
        
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setFixedSize(320, 100)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(5)
        
        # 标题
        title_label = QLabel("🤖 刷牙动作检测")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2C3E50;
                margin-bottom: 5px;
            }
        """)
        
        # 状态显示区域
        status_layout = QHBoxLayout()
        
        # 状态图标
        self.status_icon = QLabel("⚪")
        self.status_icon.setAlignment(Qt.AlignCenter)
        self.status_icon.setFixedSize(40, 40)
        self.status_icon.setStyleSheet("""
            QLabel {
                font-size: 24px;
                border-radius: 20px;
                background-color: #F0F0F0;
                border: 2px solid #E0E0E0;
            }
        """)
        
        # 状态文本和置信度
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        self.status_text = QLabel("等待检测...")
        self.status_text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.status_text.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #666666;
            }
        """)
        
        self.confidence_text = QLabel("置信度: --")
        self.confidence_text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.confidence_text.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #888888;
            }
        """)
        
        text_layout.addWidget(self.status_text)
        text_layout.addWidget(self.confidence_text)
        
        status_layout.addWidget(self.status_icon)
        status_layout.addLayout(text_layout, 1)
        
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
                padding: 4px 8px;
                border-radius: 4px;
                margin: 2px 0px;
            }
        """)
        self.warning_label.hide()
        
        layout.addWidget(title_label)
        layout.addLayout(status_layout)
        layout.addWidget(self.warning_label)
        
        # 设置整体样式
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px solid #E0E0E0;
                border-radius: 10px;
            }
        """)
    
    def update_coverage_status(self, pose_analysis):
        """
        更新覆盖状态显示
        
        Args:
            pose_analysis: YOLO姿态分析结果
        """
        if not pose_analysis:
            self.reset_status()
            return
        
        is_covered = pose_analysis.get('hand_face_coverage', False)
        confidence = pose_analysis.get('coverage_confidence', 0.0)
        coverage_details = pose_analysis.get('coverage_details', {})
        
        # 更新当前状态
        self.current_coverage_status = is_covered
        self.current_confidence = confidence
        
        # 生成状态消息
        if is_covered:
            covering_hands = coverage_details.get('covering_hands', [])
            hands_text = "、".join(covering_hands) if covering_hands else "手掌"
            status_message = f"✅ {hands_text}位置正确"
            self.show_correct_position(status_message, confidence)
        else:
            reason = coverage_details.get('reason', 'unknown')
            if reason == 'no_face_or_hands':
                status_message = "⚠️ 未检测到脸部或手掌"
                self.show_warning(status_message)
            else:
                # 当检测到脸部和手掌但未覆盖时，显示红色警告
                status_message = "❌ 主掌未覆盖脸部区域"
                self.show_incorrect_position(status_message)
        
        # 发送状态变化信号
        self.coverage_status_changed.emit(is_covered, confidence, status_message)
    
    def show_correct_position(self, message, confidence):
        """显示正确位置状态（绿色）"""
        self.status_icon.setText("✅")
        self.status_icon.setStyleSheet("""
            QLabel {
                font-size: 24px;
                border-radius: 20px;
                background-color: #4CAF50;
                color: white;
                border: 2px solid #388E3C;
            }
        """)
        
        self.status_text.setText(message)
        self.status_text.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #2E7D32;
            }
        """)
        
        self.confidence_text.setText(f"置信度: {confidence:.1%}")
        self.confidence_text.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #4CAF50;
            }
        """)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #E8F5E8;
                border: 2px solid #4CAF50;
                border-radius: 10px;
            }
        """)
        
        # 停止警告闪烁
        self.stop_warning_blink()
    
    def show_incorrect_position(self, message):
        """显示错误位置状态（红色闪烁）"""
        self.status_icon.setText("❌")
        self.status_icon.setStyleSheet("""
            QLabel {
                font-size: 24px;
                border-radius: 20px;
                background-color: #F44336;
                color: white;
                border: 2px solid #D32F2F;
            }
        """)
        
        self.status_text.setText(message)
        self.status_text.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #C62828;
            }
        """)
        
        self.confidence_text.setText(f"置信度: {self.current_confidence:.1%}")
        self.confidence_text.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #F44336;
            }
        """)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #FFEBEE;
                border: 2px solid #F44336;
                border-radius: 10px;
            }
        """)
        
        # 显示红色警告并开始闪烁
        self.warning_label.setText("⚠️ 请调整手掌位置到脸部区域")
        self.warning_label.show()
        self.start_warning_blink()
    
    def show_warning(self, message):
        """显示警告状态（橙色）"""
        self.status_icon.setText("⚠️")
        self.status_icon.setStyleSheet("""
            QLabel {
                font-size: 24px;
                border-radius: 20px;
                background-color: #FF9800;
                color: white;
                border: 2px solid #F57C00;
            }
        """)
        
        self.status_text.setText(message)
        self.status_text.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #E65100;
            }
        """)
        
        self.confidence_text.setText(f"置信度: {self.current_confidence:.1%}")
        self.confidence_text.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #FF9800;
            }
        """)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #FFF3E0;
                border: 2px solid #FF9800;
                border-radius: 10px;
            }
        """)
        
        # 停止警告闪烁
        self.stop_warning_blink()
    
    def start_warning_blink(self):
        """开始红色警告闪烁效果"""
        self.blink_timer.start(400)  # 每400ms闪烁一次，确保响应时间<200ms
    
    def stop_warning_blink(self):
        """停止警告闪烁效果"""
        self.blink_timer.stop()
        self.warning_label.hide()
        self.blink_state = True
    
    def toggle_warning_blink(self):
        """切换警告闪烁状态"""
        self.blink_state = not self.blink_state
        if self.blink_state:
            self.warning_label.setStyleSheet("""
                QLabel {
                    background-color: #F44336;
                    color: white;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 4px 8px;
                    border-radius: 4px;
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
                    padding: 4px 8px;
                    border-radius: 4px;
                    margin: 2px 0px;
                }
            """)
    
    def reset_status(self):
        """重置状态显示"""
        self.status_icon.setText("⚪")
        self.status_icon.setStyleSheet("""
            QLabel {
                font-size: 24px;
                border-radius: 20px;
                background-color: #F0F0F0;
                border: 2px solid #E0E0E0;
            }
        """)
        
        self.status_text.setText("等待检测...")
        self.status_text.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #666666;
            }
        """)
        
        self.confidence_text.setText("置信度: --")
        self.confidence_text.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #888888;
            }
        """)
        
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px solid #E0E0E0;
                border-radius: 10px;
            }
        """)
        
        self.stop_warning_blink()
        self.current_coverage_status = False
        self.current_confidence = 0.0

def draw_coverage_visualization_on_frame(frame, pose_analysis):
    """
    在摄像头帧上绘制覆盖检测可视化
    
    Args:
        frame: OpenCV图像帧
        pose_analysis: 姿态分析结果
        
    Returns:
        绘制后的图像帧
    """
    if not pose_analysis:
        return frame
    
    display_frame = frame.copy()
    
    # 获取覆盖检测结果
    is_covered = pose_analysis.get('hand_face_coverage', False)
    confidence = pose_analysis.get('coverage_confidence', 0.0)
    coverage_details = pose_analysis.get('coverage_details', {})
    
    # 绘制脸部区域边界框
    face_bounds = coverage_details.get('face_bounds')
    extended_bounds = coverage_details.get('extended_bounds')
    
    if face_bounds and extended_bounds:
        # 绘制原始脸部区域（蓝色虚线）
        face_rect = (
            int(face_bounds['left']), int(face_bounds['top']),
            int(face_bounds['right'] - face_bounds['left']),
            int(face_bounds['bottom'] - face_bounds['top'])
        )
        cv2.rectangle(display_frame, 
                     (face_rect[0], face_rect[1]), 
                     (face_rect[0] + face_rect[2], face_rect[1] + face_rect[3]),
                     (255, 0, 0), 1, cv2.LINE_AA)
        
        # 绘制扩展检测区域
        extended_rect = (
            int(extended_bounds['left']), int(extended_bounds['top']),
            int(extended_bounds['right'] - extended_bounds['left']),
            int(extended_bounds['bottom'] - extended_bounds['top'])
        )
        
        # 根据覆盖状态选择颜色
        if is_covered:
            color = (0, 255, 0)  # 绿色 - 正确覆盖
            thickness = 3
        else:
            color = (0, 0, 255)  # 红色 - 未正确覆盖
            thickness = 2
        
        cv2.rectangle(display_frame,
                     (extended_rect[0], extended_rect[1]),
                     (extended_rect[0] + extended_rect[2], extended_rect[1] + extended_rect[3]),
                     color, thickness, cv2.LINE_AA)
    
    # 绘制手掌位置
    hand_positions = pose_analysis.get('hand_positions', [])
    for hand in hand_positions:
        hand_x, hand_y = hand['hand_position']
        hand_x, hand_y = int(hand_x), int(hand_y)
        
        # 根据覆盖状态选择手掌标记颜色
        if is_covered:
            hand_color = (0, 255, 0)  # 绿色
            marker = "✓"
        else:
            hand_color = (0, 0, 255)  # 红色
            marker = "✗"
        
        # 绘制手掌位置圆圈
        cv2.circle(display_frame, (hand_x, hand_y), 15, hand_color, 3)
        cv2.circle(display_frame, (hand_x, hand_y), 8, hand_color, -1)
        
        # 绘制手掌标记
        cv2.putText(display_frame, marker, (hand_x - 8, hand_y + 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # 绘制手掌标签
        label = f"{hand['side']} hand"
        cv2.putText(display_frame, label, (hand_x - 20, hand_y - 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, hand_color, 1)
    
    # 绘制状态信息
    status_text = "✅ 刷牙动作正确" if is_covered else "❌ 请调整手掌位置"
    status_color = (0, 255, 0) if is_covered else (0, 0, 255)
    
    # 绘制状态背景
    text_size = cv2.getTextSize(status_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
    cv2.rectangle(display_frame, (10, 10), (text_size[0] + 20, 50), (0, 0, 0), -1)
    cv2.rectangle(display_frame, (10, 10), (text_size[0] + 20, 50), status_color, 2)
    
    # 绘制状态文本
    cv2.putText(display_frame, status_text, (15, 35),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
    
    # 绘制置信度
    confidence_text = f"置信度: {confidence:.1%}"
    cv2.putText(display_frame, confidence_text, (15, display_frame.shape[0] - 15),
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    return display_frame