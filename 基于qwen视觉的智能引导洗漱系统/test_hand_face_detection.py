"""
手掌-脸部覆盖检测功能测试脚本
测试YOLO姿态检测和UI反馈系统
"""

import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap

# 添加项目路径
sys.path.append('.')

from src.core.yolo_pose_detector import YOLOPoseDetector
from src.ui.hand_face_coverage_widget import HandFaceCoverageWidget, draw_coverage_visualization_on_frame

class HandFaceDetectionTestWindow(QMainWindow):
    """手掌-脸部检测测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("手掌-脸部覆盖检测测试")
        self.setGeometry(100, 100, 1000, 700)
        
        # 初始化YOLO检测器
        self.pose_detector = YOLOPoseDetector()
        
        # 摄像头
        self.camera = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        
        self.init_ui()
        self.init_camera()
        
    def init_ui(self):
        """初始化用户界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        
        # 左侧：摄像头显示
        left_layout = QVBoxLayout()
        
        self.camera_label = QLabel("摄像头未启动")
        self.camera_label.setFixedSize(640, 480)
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setStyleSheet("border: 2px solid #ccc;")
        
        # 控制按钮
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("启动摄像头")
        self.start_btn.clicked.connect(self.toggle_camera)
        
        self.test_btn = QPushButton("测试检测")
        self.test_btn.clicked.connect(self.test_detection)
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.test_btn)
        
        left_layout.addWidget(self.camera_label)
        left_layout.addLayout(button_layout)
        
        # 右侧：检测结果显示
        right_layout = QVBoxLayout()
        
        # 覆盖检测UI组件
        self.coverage_widget = HandFaceCoverageWidget()
        self.coverage_widget.coverage_status_changed.connect(self.on_coverage_changed)
        
        # 检测信息显示
        self.info_label = QLabel("检测信息将在这里显示")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("""
            QLabel {
                border: 1px solid #ccc;
                padding: 10px;
                background-color: #f9f9f9;
                font-family: monospace;
            }
        """)
        self.info_label.setMinimumHeight(300)
        
        right_layout.addWidget(QLabel("实时检测状态:"))
        right_layout.addWidget(self.coverage_widget)
        right_layout.addWidget(QLabel("详细检测信息:"))
        right_layout.addWidget(self.info_label, 1)
        
        # 添加到主布局
        layout.addLayout(left_layout, 2)
        layout.addLayout(right_layout, 1)
        
    def init_camera(self):
        """初始化摄像头"""
        try:
            self.camera = cv2.VideoCapture(0)
            if self.camera.isOpened():
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                print("摄像头初始化成功")
            else:
                print("无法打开摄像头")
                self.camera = None
        except Exception as e:
            print(f"摄像头初始化失败: {e}")
            self.camera = None
    
    def toggle_camera(self):
        """切换摄像头状态"""
        if self.timer.isActive():
            self.timer.stop()
            self.start_btn.setText("启动摄像头")
            self.camera_label.setText("摄像头已停止")
        else:
            if self.camera and self.camera.isOpened():
                self.timer.start(33)  # 约30fps
                self.start_btn.setText("停止摄像头")
            else:
                self.camera_label.setText("摄像头启动失败")
    
    def update_frame(self):
        """更新摄像头帧"""
        if self.camera and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                # 进行姿态检测
                if self.pose_detector.is_available():
                    pose_results, annotated_frame = self.pose_detector.detect_pose(frame)
                    
                    if pose_results:
                        for pose_data in pose_results:
                            # 获取姿态分析
                            pose_analysis = self.pose_detector.get_pose_analysis(pose_data['keypoints'])
                            
                            # 更新UI
                            self.coverage_widget.update_coverage_status(pose_analysis)
                            
                            # 绘制可视化
                            annotated_frame = draw_coverage_visualization_on_frame(annotated_frame, pose_analysis)
                            
                            # 更新信息显示
                            self.update_info_display(pose_analysis)
                    
                    display_frame = annotated_frame
                else:
                    display_frame = frame
                
                # 转换为Qt格式显示
                qt_image = self.cv2_to_qt(display_frame)
                self.camera_label.setPixmap(qt_image)
    
    def cv2_to_qt(self, cv_img):
        """将OpenCV图像转换为Qt图像"""
        height, width, channel = cv_img.shape
        bytes_per_line = 3 * width
        cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        qt_image = QImage(cv_img.data, width, height, bytes_per_line, QImage.Format_RGB888)
        return QPixmap.fromImage(qt_image).scaled(640, 480, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    
    def update_info_display(self, pose_analysis):
        """更新检测信息显示"""
        info_text = "=== 姿态检测结果 ===\n"
        info_text += f"头部检测: {'✓' if pose_analysis.get('head_detected') else '✗'}\n"
        info_text += f"手部检测: {'✓' if pose_analysis.get('hands_detected') else '✗'}\n"
        info_text += f"整体置信度: {pose_analysis.get('overall_confidence', 0):.2f}\n\n"
        
        info_text += "=== 手掌位置 ===\n"
        hand_positions = pose_analysis.get('hand_positions', [])
        for i, hand in enumerate(hand_positions):
            info_text += f"手掌 {i+1} ({hand['side']}):\n"
            info_text += f"  位置: {hand['hand_position']}\n"
            info_text += f"  置信度: {hand['confidence']:.2f}\n"
        
        info_text += "\n=== 覆盖检测 ===\n"
        info_text += f"脸部覆盖: {'✓' if pose_analysis.get('hand_face_coverage') else '✗'}\n"
        info_text += f"覆盖置信度: {pose_analysis.get('coverage_confidence', 0):.2f}\n"
        
        coverage_details = pose_analysis.get('coverage_details', {})
        if 'covering_hands' in coverage_details:
            info_text += f"覆盖手掌: {', '.join(coverage_details['covering_hands'])}\n"
        
        if 'reason' in coverage_details:
            info_text += f"未覆盖原因: {coverage_details['reason']}\n"
        
        self.info_label.setText(info_text)
    
    def on_coverage_changed(self, is_covered, confidence, message):
        """处理覆盖状态变化"""
        status = "正确覆盖" if is_covered else "未正确覆盖"
        print(f"覆盖状态: {status}, 置信度: {confidence:.2f}, 消息: {message}")
    
    def test_detection(self):
        """测试检测功能"""
        if not self.pose_detector.is_available():
            print("YOLO检测器不可用，正在初始化...")
            if self.pose_detector.load_model():
                print("YOLO检测器初始化成功")
            else:
                print("YOLO检测器初始化失败")
        else:
            print("YOLO检测器可用")
    
    def closeEvent(self, event):
        """关闭事件"""
        if self.timer.isActive():
            self.timer.stop()
        if self.camera:
            self.camera.release()
        event.accept()

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("手掌-脸部覆盖检测测试")
    app.setApplicationVersion("1.0.0")
    
    # 创建测试窗口
    window = HandFaceDetectionTestWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()