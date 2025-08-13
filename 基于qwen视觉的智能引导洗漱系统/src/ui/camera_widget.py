"""
摄像头显示组件
"""

import cv2
import numpy as np
import os
import time
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor
from src.utils.config_manager import ConfigManager
from src.core.yolo_pose_detector import YOLOPoseDetector

class CameraWidget(QWidget):
    """摄像头显示组件"""
    
    frame_ready = pyqtSignal(np.ndarray)  # 帧准备就绪信号
    video_recorded = pyqtSignal(str)  # 视频录制完成信号
    pose_detected = pyqtSignal(dict)  # 姿态检测信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = ConfigManager()
        self.camera = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        
        self.current_frame = None
        self.detection_results = []
        
        # 初始化YOLO姿态检测器
        self.pose_detector = YOLOPoseDetector()
        self.enable_pose_detection = True  # 可通过配置控制
        self.pose_results = []
        
        # 视频录制相关
        self.is_recording = False
        self.video_writer = None
        self.recorded_frames = []
        self.recording_start_time = None
        self.recording_duration = 5  # 录制5秒
        
        # 刷牙控制器引用
        self.brush_controller = None
        
        self.init_ui()
        self.init_camera()
        
    def set_brush_controller(self, brush_controller):
        """设置刷牙控制器引用"""
        self.brush_controller = brush_controller
        print("摄像头组件已连接到刷牙控制器")
    
    def toggle_pose_detection(self, enabled):
        """切换姿态检测功能"""
        self.enable_pose_detection = enabled
        if enabled and not self.pose_detector.is_available():
            print("正在初始化YOLO姿态检测模型...")
            if self.pose_detector.load_model():
                print("YOLO姿态检测模型加载成功")
            else:
                print("YOLO姿态检测模型加载失败")
                self.enable_pose_detection = False
        print(f"姿态检测功能: {'开启' if self.enable_pose_detection else '关闭'}")
    
    def get_pose_results(self):
        """获取最新的姿态检测结果"""
        return getattr(self, 'pose_results', [])
    
    def set_pose_detection_confidence(self, confidence):
        """设置姿态检测置信度阈值"""
        if hasattr(self, 'pose_detector'):
            self.pose_detector.set_confidence_threshold(confidence)
        
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # 移除边距
        layout.setSpacing(0)  # 移除间距
        
        # 摄像头显示标签 - 完全填充容器
        self.camera_label = QLabel()
        self.camera_label.setStyleSheet("""
            QLabel {
                border: none;
                background-color: transparent;
            }
        """)
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setText("摄像头未启动")
        self.camera_label.setScaledContents(False)  # 不自动缩放内容
        
        # 只添加摄像头标签，移除按钮
        layout.addWidget(self.camera_label, 1)  # 完全填充容器
        
    def init_camera(self):
        """初始化摄像头"""
        camera_id = self.config.get('camera.device_id', 0)
        try:
            self.camera = cv2.VideoCapture(camera_id)
            if self.camera.isOpened():
                # 设置摄像头参数
                width = self.config.get('camera.width', 640)
                height = self.config.get('camera.height', 480)
                fps = self.config.get('camera.fps', 30)
                
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                self.camera.set(cv2.CAP_PROP_FPS, fps)
                
                print(f"摄像头初始化成功: {width}x{height}@{fps}fps")
                # 自动启动摄像头
                self.start_camera()
            else:
                print("无法打开摄像头")
                self.camera = None
        except Exception as e:
            print(f"摄像头初始化失败: {e}")
            self.camera = None
            
    def toggle_camera(self):
        """切换摄像头状态"""
        if self.timer.isActive():
            self.stop_camera()
        else:
            self.start_camera()
            
    def start_camera(self):
        """启动摄像头"""
        if self.camera is None:
            self.init_camera()
            
        if self.camera and self.camera.isOpened():
            self.timer.start(33)  # 约30fps
            print("摄像头已启动")
        else:
            self.camera_label.setText("摄像头启动失败")
            
    def stop_camera(self):
        """停止摄像头"""
        self.timer.stop()
        self.camera_label.setText("摄像头已停止")
        print("摄像头已停止")
        
    def start_recording(self, step_name, duration=5):
        """开始录制视频"""
        if not self.camera or not self.camera.isOpened():
            print("摄像头未启动，无法录制")
            return
            
        self.is_recording = True
        self.recorded_frames = []
        self.recording_start_time = time.time()
        self.recording_duration = duration
        
        print(f"开始录制 {step_name} 步骤视频，时长: {self.recording_duration}秒")
        
    def stop_recording(self, step_name):
        """停止录制并直接分析帧（优化版本，不保存MP4文件）"""
        if not self.is_recording:
            return
            
        self.is_recording = False
        
        if len(self.recorded_frames) == 0:
            print("没有录制到帧")
            return
            
        print(f"录制完成，共 {len(self.recorded_frames)} 帧，开始直接分析")
        
        try:
            # 直接使用内存中的帧进行分析，无需保存MP4文件
            if self.brush_controller and self.brush_controller.async_analyzer:
                print(f"开始异步分析 {step_name} 步骤视频帧")
                # 优化内存使用：只传递必要的帧，减少内存占用
                frame_count = len(self.recorded_frames)
                # 如果帧数太多，采样部分帧进行分析
                if frame_count > 60:  # 超过60帧时采样
                    step = frame_count // 30  # 采样30帧
                    sampled_frames = [self.recorded_frames[i].copy() for i in range(0, frame_count, step)][:30]
                    print(f"帧数过多({frame_count})，采样{len(sampled_frames)}帧进行分析")
                else:
                    sampled_frames = [frame.copy() for frame in self.recorded_frames]
                
                self.brush_controller.async_analyzer.analyze_frames(sampled_frames, step_name)
            
            # 可选：如果需要保存视频文件用于调试，可以启用以下代码
            # self._save_video_for_debug(step_name)
            
        except Exception as e:
            print(f"帧分析启动失败: {e}")
        finally:
            # 确保清理内存中的帧
            try:
                self.recorded_frames.clear()
                self.recorded_frames = []
                print("录制帧内存已清理")
            except Exception as e:
                print(f"清理录制帧内存时出错: {e}")
        
    def _save_video_for_debug(self, step_name):
        """可选：保存视频文件用于调试"""
        try:
            # 创建视频文件夹
            video_dir = "data/videos"
            os.makedirs(video_dir, exist_ok=True)
            
            # 生成视频文件名
            timestamp = int(time.time())
            video_filename = f"{video_dir}/brush_{step_name}_{timestamp}.mp4"
            
            # 获取视频参数
            height, width = self.recorded_frames[0].shape[:2]
            fps = 30
            
            # 创建视频写入器
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(video_filename, fourcc, fps, (width, height))
            
            # 写入所有帧
            for frame in self.recorded_frames:
                video_writer.write(frame)
                
            video_writer.release()
            print(f"调试视频保存成功: {video_filename}")
            
        except Exception as e:
            print(f"调试视频保存失败: {e}")
        
    def update_frame(self):
        """更新帧"""
        try:
            if self.camera and self.camera.isOpened():
                ret, frame = self.camera.read()
                if ret:
                    self.current_frame = frame.copy()
                    
                    # 如果正在录制，保存帧（添加异常处理和内存限制）
                    if self.is_recording:
                        try:
                            # 限制录制帧数，避免内存溢出
                            max_frames = self.recording_duration * 30  # 假设30fps
                            if len(self.recorded_frames) < max_frames:
                                self.recorded_frames.append(frame.copy())
                            
                            # 检查录制时长
                            if self.recording_start_time and time.time() - self.recording_start_time >= self.recording_duration:
                                # 自动停止录制（由控制器调用stop_recording）
                                pass
                        except Exception as e:
                            print(f"录制帧时出错: {e}")
                            # 如果录制出错，停止录制
                            self.is_recording = False
                    
                    # 进行姿态检测
                    display_frame = frame.copy()
                    if self.enable_pose_detection and self.pose_detector.is_available():
                        try:
                            pose_results, annotated_frame = self.pose_detector.detect_pose(frame)
                            self.pose_results = pose_results
                            display_frame = annotated_frame
                            
                            # 发送姿态检测信号
                            if pose_results:
                                for pose_data in pose_results:
                                    pose_analysis = self.pose_detector.get_pose_analysis(pose_data['keypoints'])
                                    self.pose_detected.emit(pose_analysis)
                        except Exception as e:
                            print(f"姿态检测出错: {e}")
                    
                    # 绘制其他检测结果（保持原有功能）
                    display_frame = self.draw_detections(display_frame)
                    
                    # 转换为Qt格式并显示
                    qt_image = self.cv2_to_qt(display_frame)
                    self.camera_label.setPixmap(qt_image)
                    
                    # 发送帧信号
                    self.frame_ready.emit(self.current_frame)
                else:
                    print("无法读取摄像头帧")
                    self.stop_camera()
        except KeyboardInterrupt:
            print("用户中断摄像头更新")
            self.stop_camera()
        except Exception as e:
            print(f"摄像头帧更新出错: {e}")
            # 不停止摄像头，继续尝试
                
    def cv2_to_qt(self, cv_img):
        """将OpenCV图像转换为Qt图像"""
        height, width, channel = cv_img.shape
        bytes_per_line = 3 * width
        
        # 转换颜色空间
        cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        
        # 创建QImage
        qt_image = QImage(cv_img.data, width, height, bytes_per_line, QImage.Format_RGB888)
        
        # 获取标签的完整尺寸
        label_size = self.camera_label.size()
        
        # 使用标签的完整尺寸，只减去少量边框空间
        available_width = max(label_size.width() - 6, 50)  # 减去边框，最小50
        available_height = max(label_size.height() - 6, 50)  # 减去边框，最小50
        
        # 按比例缩放，保持宽高比，尽可能填满可用空间
        scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
            available_width, available_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        return scaled_pixmap
        
    def draw_detections(self, frame):
        """绘制检测结果"""
        display_frame = frame.copy()
        
        # 绘制检测框和标签
        for detection in self.detection_results:
            x1, y1, x2, y2 = detection.get('bbox', [0, 0, 0, 0])
            label = detection.get('label', '')
            confidence = detection.get('confidence', 0.0)
            
            # 绘制边界框
            cv2.rectangle(display_frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            
            # 绘制标签
            label_text = f"{label}: {confidence:.2f}"
            cv2.putText(display_frame, label_text, (int(x1), int(y1-10)), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # 绘制录制状态
        if self.is_recording:
            cv2.putText(display_frame, "● 录制中", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            # 显示录制进度
            if self.recording_start_time:
                elapsed = time.time() - self.recording_start_time
                remaining = max(0, self.recording_duration - elapsed)
                cv2.putText(display_frame, f"剩余: {remaining:.1f}s", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # 绘制状态信息
        status_text = f"检测到 {len(self.detection_results)} 个目标"
        cv2.putText(display_frame, status_text, (10, display_frame.shape[0] - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return display_frame
        
    def update_detections(self, detections):
        """更新检测结果"""
        self.detection_results = detections
        
    def get_current_frame(self):
        """获取当前帧"""
        return self.current_frame
        
    def is_recording_active(self):
        """检查是否正在录制"""
        return self.is_recording
        
    def get_recording_progress(self):
        """获取录制进度"""
        if not self.is_recording or not self.recording_start_time:
            return 0
        elapsed = time.time() - self.recording_start_time
        return min(elapsed / self.recording_duration, 1.0)
        
    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)
        # 当窗口大小改变时，如果有当前帧，重新显示以适应新尺寸
        if hasattr(self, 'current_frame') and self.current_frame is not None:
            display_frame = self.draw_detections(self.current_frame)
            qt_image = self.cv2_to_qt(display_frame)
            self.camera_label.setPixmap(qt_image)
        
    def closeEvent(self, event):
        """关闭事件"""
        self.stop_camera()
        if self.camera:
            self.camera.release()
        event.accept()