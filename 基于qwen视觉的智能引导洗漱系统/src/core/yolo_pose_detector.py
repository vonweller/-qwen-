"""
YOLOV11姿态检测器 - 检测人体关键点并在画面中显示
"""

import cv2
import numpy as np
from ultralytics import YOLO
import os

class YOLOPoseDetector:
    """YOLO姿态检测器"""
    
    def __init__(self, model_path=None):
        """
        初始化YOLO姿态检测器
        
        Args:
            model_path: 模型路径，如果为None则使用预训练模型
        """
        self.confidence_threshold = 0.5  # 默认置信度阈值
        
        try:
            # 使用YOLO11姿态检测模型
            if model_path and os.path.exists(model_path):
                self.model = YOLO(model_path)
                print(f"加载自定义YOLO模型: {model_path}")
            else:
                # 使用预训练的姿态检测模型
                self.model = YOLO('yolo11n-pose.pt')  # nano版本，速度快
                print("加载YOLO11预训练姿态检测模型")
            
            self.is_initialized = True
            
            # 人体关键点连接线定义（COCO格式）
            self.skeleton = [
                [16, 14], [14, 12], [17, 15], [15, 13], [12, 13],  # 头部
                [6, 12], [7, 13], [6, 7], [6, 8], [7, 9],          # 躯干和手臂
                [8, 10], [9, 11], [12, 14], [13, 15], [14, 16], [15, 17]  # 手臂和腿部
            ]
            
            # 关键点颜色定义
            self.keypoint_colors = [
                (255, 0, 0),    # 鼻子 - 红色
                (255, 85, 0),   # 眼睛 - 橙色
                (255, 170, 0),  # 眼睛 - 黄橙色
                (255, 255, 0),  # 耳朵 - 黄色
                (170, 255, 0),  # 耳朵 - 黄绿色
                (85, 255, 0),   # 肩膀 - 绿色
                (0, 255, 0),    # 肩膀 - 纯绿色
                (0, 255, 85),   # 肘部 - 青绿色
                (0, 255, 170),  # 肘部 - 青色
                (0, 255, 255),  # 手腕 - 青色
                (0, 170, 255),  # 手腕 - 浅蓝色
                (0, 85, 255),   # 髋部 - 蓝色
                (0, 0, 255),    # 髋部 - 纯蓝色
                (85, 0, 255),   # 膝盖 - 紫蓝色
                (170, 0, 255),  # 膝盖 - 紫色
                (255, 0, 255),  # 脚踝 - 品红色
                (255, 0, 170),  # 脚踝 - 粉红色
            ]
            
            # 关键点名称
            self.keypoint_names = [
                'nose', 'left_eye', 'right_eye', 'left_ear', 'right_ear',
                'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
                'left_wrist', 'right_wrist', 'left_hip', 'right_hip',
                'left_knee', 'right_knee', 'left_ankle', 'right_ankle'
            ]
            
        except Exception as e:
            print(f"YOLO姿态检测器初始化失败: {e}")
            self.is_initialized = False
            self.model = None
    
    def detect_pose(self, frame):
        """
        检测人体姿态
        
        Args:
            frame: 输入图像帧
            
        Returns:
            tuple: (检测结果, 带关键点的图像)
        """
        if not self.is_initialized or self.model is None:
            return [], frame
        
        try:
            # 进行姿态检测
            results = self.model(frame, verbose=False)
            
            # 解析检测结果
            pose_results = []
            annotated_frame = frame.copy()
            
            for result in results:
                if result.keypoints is not None:
                    keypoints = result.keypoints.data.cpu().numpy()
                    
                    for person_keypoints in keypoints:
                        # 提取关键点信息
                        pose_data = {
                            'keypoints': person_keypoints,
                            'confidence': float(np.mean(person_keypoints[:, 2])),  # 平均置信度
                            'bbox': None
                        }
                        
                        # 如果有边界框信息
                        if result.boxes is not None and len(result.boxes) > 0:
                            bbox = result.boxes.xyxy[0].cpu().numpy()
                            pose_data['bbox'] = bbox
                        
                        pose_results.append(pose_data)
                        
                        # 在图像上绘制关键点和骨架
                        annotated_frame = self.draw_pose(annotated_frame, person_keypoints)
            
            return pose_results, annotated_frame
            
        except Exception as e:
            print(f"姿态检测失败: {e}")
            return [], frame
    
    def draw_pose(self, frame, keypoints, confidence_threshold=None):
        """
        在图像上绘制姿态关键点和骨架
        
        Args:
            frame: 输入图像
            keypoints: 关键点数据 (17, 3) - x, y, confidence
            confidence_threshold: 置信度阈值
            
        Returns:
            绘制后的图像
        """
        if confidence_threshold is None:
            confidence_threshold = self.confidence_threshold
            
        h, w = frame.shape[:2]
        
        # 绘制骨架连接线
        for connection in self.skeleton:
            if len(connection) == 2:
                pt1_idx, pt2_idx = connection[0] - 1, connection[1] - 1  # 转换为0索引
                
                if (pt1_idx < len(keypoints) and pt2_idx < len(keypoints) and
                    keypoints[pt1_idx][2] > confidence_threshold and 
                    keypoints[pt2_idx][2] > confidence_threshold):
                    
                    pt1 = (int(keypoints[pt1_idx][0]), int(keypoints[pt1_idx][1]))
                    pt2 = (int(keypoints[pt2_idx][0]), int(keypoints[pt2_idx][1]))
                    
                    # 绘制连接线
                    cv2.line(frame, pt1, pt2, (0, 255, 0), 2)
        
        # 绘制关键点
        for i, (x, y, conf) in enumerate(keypoints):
            if conf > confidence_threshold:
                x, y = int(x), int(y)
                
                # 确保坐标在图像范围内
                if 0 <= x < w and 0 <= y < h:
                    # 获取关键点颜色
                    color = self.keypoint_colors[i] if i < len(self.keypoint_colors) else (255, 255, 255)
                    
                    # 绘制关键点
                    cv2.circle(frame, (x, y), 4, color, -1)
                    cv2.circle(frame, (x, y), 6, (255, 255, 255), 2)
                    
                    # 绘制关键点标签（可选）
                    if i < len(self.keypoint_names):
                        label = f"{self.keypoint_names[i]}: {conf:.2f}"
                        cv2.putText(frame, label, (x + 10, y - 10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)
        
        return frame
    
    def get_pose_analysis(self, keypoints, confidence_threshold=None):
        """
        分析姿态信息，用于刷牙动作评估
        
        Args:
            keypoints: 关键点数据
            confidence_threshold: 置信度阈值
            
        Returns:
            dict: 姿态分析结果
        """
        if confidence_threshold is None:
            confidence_threshold = self.confidence_threshold
            
        if len(keypoints) == 0:
            return {
                'head_detected': False,
                'hands_detected': False,
                'head_angle': 0,
                'hand_positions': [],
                'overall_confidence': 0,
                'hand_face_coverage': False,
                'coverage_confidence': 0.0,
                'coverage_details': {}
            }
        
        analysis = {
            'head_detected': False,
            'hands_detected': False,
            'head_angle': 0,
            'hand_positions': [],
            'overall_confidence': float(np.mean(keypoints[:, 2])),
            'hand_face_coverage': False,
            'coverage_confidence': 0.0,
            'coverage_details': {}
        }
        
        # 检测头部关键点
        nose = keypoints[0] if keypoints[0][2] > confidence_threshold else None
        left_eye = keypoints[1] if keypoints[1][2] > confidence_threshold else None
        right_eye = keypoints[2] if keypoints[2][2] > confidence_threshold else None
        left_ear = keypoints[3] if keypoints[3][2] > confidence_threshold else None
        right_ear = keypoints[4] if keypoints[4][2] > confidence_threshold else None
        
        # 定义脸部区域
        face_keypoints = []
        if nose is not None:
            face_keypoints.append(nose)
        if left_eye is not None:
            face_keypoints.append(left_eye)
        if right_eye is not None:
            face_keypoints.append(right_eye)
        if left_ear is not None:
            face_keypoints.append(left_ear)
        if right_ear is not None:
            face_keypoints.append(right_ear)
        
        if len(face_keypoints) >= 2:
            analysis['head_detected'] = True
            
            # 计算头部角度
            if left_eye is not None and right_eye is not None:
                dx = right_eye[0] - left_eye[0]
                dy = right_eye[1] - left_eye[1]
                analysis['head_angle'] = np.degrees(np.arctan2(dy, dx))
        
        # 检测手部关键点（包含肘部和肩部用于更准确的手掌位置估算）
        left_shoulder = keypoints[5] if len(keypoints) > 5 and keypoints[5][2] > confidence_threshold else None
        right_shoulder = keypoints[6] if len(keypoints) > 6 and keypoints[6][2] > confidence_threshold else None
        left_elbow = keypoints[7] if len(keypoints) > 7 and keypoints[7][2] > confidence_threshold else None
        right_elbow = keypoints[8] if len(keypoints) > 8 and keypoints[8][2] > confidence_threshold else None
        left_wrist = keypoints[9] if len(keypoints) > 9 and keypoints[9][2] > confidence_threshold else None
        right_wrist = keypoints[10] if len(keypoints) > 10 and keypoints[10][2] > confidence_threshold else None
        
        # 估算手掌位置（基于手腕和肘部）
        hand_positions = []
        
        if left_wrist is not None:
            hand_pos = self._estimate_hand_position(left_wrist, left_elbow, 'left')
            hand_positions.append({
                'side': 'left',
                'wrist_position': (float(left_wrist[0]), float(left_wrist[1])),
                'hand_position': hand_pos,
                'confidence': float(left_wrist[2])
            })
        
        if right_wrist is not None:
            hand_pos = self._estimate_hand_position(right_wrist, right_elbow, 'right')
            hand_positions.append({
                'side': 'right',
                'wrist_position': (float(right_wrist[0]), float(right_wrist[1])),
                'hand_position': hand_pos,
                'confidence': float(right_wrist[2])
            })
        
        analysis['hand_positions'] = hand_positions
        analysis['hands_detected'] = len(hand_positions) > 0
        
        # 检查手掌是否覆盖脸部区域
        if analysis['head_detected'] and analysis['hands_detected']:
            coverage_result = self._check_hand_face_coverage(face_keypoints, hand_positions, keypoints, confidence_threshold)
            analysis.update(coverage_result)
        
        return analysis
    
    def _estimate_hand_position(self, wrist, elbow, side):
        """
        基于手腕位置估算手掌中心位置（简化版本）
        
        Args:
            wrist: 手腕关键点 (x, y, confidence)
            elbow: 肘部关键点 (x, y, confidence) 或 None
            side: 'left' 或 'right'
            
        Returns:
            tuple: 估算的手掌中心位置 (x, y)
        """
        # 简化处理：直接使用手腕位置作为手掌位置
        # 这样更准确，因为手腕就在手掌附近
        return (float(wrist[0]), float(wrist[1]))
    
    def _check_hand_face_coverage(self, face_keypoints, hand_positions, keypoints, confidence_threshold):
        """
        检查手掌是否覆盖脸部区域（基于手掌高于肩膀的判断）
        
        Args:
            face_keypoints: 脸部关键点列表
            hand_positions: 手部位置列表
            keypoints: 完整的关键点数组
            confidence_threshold: 置信度阈值
            
        Returns:
            dict: 覆盖检测结果
        """
        if not face_keypoints or not hand_positions:
            return {
                'hand_face_coverage': False,
                'coverage_confidence': 0.0,
                'coverage_details': {'reason': 'no_face_or_hands'}
            }
        
        # 计算脸部中心点（使用鼻子或眼睛）
        face_center_x = 0
        face_center_y = 0
        valid_points = 0
        
        for kp in face_keypoints:
            face_center_x += kp[0]
            face_center_y += kp[1]
            valid_points += 1
        
        if valid_points == 0:
            return {
                'hand_face_coverage': False,
                'coverage_confidence': 0.0,
                'coverage_details': {'reason': 'no_valid_face_points'}
            }
        
        face_center_x /= valid_points
        face_center_y /= valid_points
        
        # 获取肩膀关键点用于高度比较
        left_shoulder = keypoints[5] if len(keypoints) > 5 and keypoints[5][2] > confidence_threshold else None
        right_shoulder = keypoints[6] if len(keypoints) > 6 and keypoints[6][2] > confidence_threshold else None
        
        # 计算肩膀平均高度
        shoulder_y = None
        if left_shoulder is not None and right_shoulder is not None:
            shoulder_y = (left_shoulder[1] + right_shoulder[1]) / 2
        elif left_shoulder is not None:
            shoulder_y = left_shoulder[1]
        elif right_shoulder is not None:
            shoulder_y = right_shoulder[1]
        
        print(f"DEBUG: 脸部中心 ({face_center_x:.1f}, {face_center_y:.1f})")
        if shoulder_y is not None:
            print(f"DEBUG: 肩膀高度: {shoulder_y:.1f}")
        
        # 简化的覆盖检测：检查手掌是否高于肩膀
        max_confidence = 0.0
        covering_hands = []
        
        for hand in hand_positions:
            hand_x, hand_y = hand['hand_position']
            
            print(f"DEBUG: {hand['side']}手位置 ({hand_x:.1f}, {hand_y:.1f})")
            
            # 判断手掌是否高于肩膀（y坐标更小表示更高）
            if shoulder_y is not None and hand_y < shoulder_y:
                # 手掌高于肩膀，计算置信度
                height_diff = shoulder_y - hand_y
                # 基于高度差计算置信度，高度差越大置信度越高
                confidence = min(1.0, height_diff / 50.0)  # 50像素高度差为满分
                confidence = max(0.5, confidence)  # 最低0.5置信度
                
                print(f"DEBUG: {hand['side']}手高于肩膀 {height_diff:.1f}像素, 置信度: {confidence:.3f}")
                
                if confidence > max_confidence:
                    max_confidence = confidence
                
                covering_hands.append(hand['side'])
            else:
                print(f"DEBUG: {hand['side']}手未高于肩膀")
        
        # 判断是否满足覆盖条件
        is_covered = max_confidence > 0.4  # 设置合理阈值
        
        print(f"DEBUG: 最大置信度: {max_confidence:.3f}, 是否覆盖: {is_covered}")
        
        return {
            'hand_face_coverage': is_covered,
            'coverage_confidence': float(max_confidence),
            'coverage_details': {
                'covering_hands': covering_hands,
                'face_center': (float(face_center_x), float(face_center_y)),
                'shoulder_height': float(shoulder_y) if shoulder_y is not None else None,
                'max_confidence': float(max_confidence)
            }
        }
    
    def is_available(self):
        """检查检测器是否可用"""
        return self.is_initialized and self.model is not None
    
    def set_confidence_threshold(self, threshold):
        """设置置信度阈值"""
        self.confidence_threshold = max(0.0, min(1.0, threshold))
        print(f"YOLO姿态检测置信度阈值设置为: {self.confidence_threshold}")
    
    def load_model(self):
        """加载模型（如果尚未加载）"""
        if not self.is_initialized:
            try:
                self.model = YOLO('yolo11n-pose.pt')
                self.is_initialized = True
                print("YOLO姿态检测模型加载成功")
                return True
            except Exception as e:
                print(f"YOLO模型加载失败: {e}")
                return False
        return True