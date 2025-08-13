"""
刷牙位置监控器 - 基于YOLO姿态检测判断刷牙位置是否正确
"""

import time
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal

class BrushPositionMonitor(QObject):
    """刷牙位置监控器"""
    
    # 信号定义
    position_status_changed = pyqtSignal(bool, str)  # (是否正确, 状态描述)
    warning_triggered = pyqtSignal(str)  # 警告信息
    
    def __init__(self):
        super().__init__()
        
        # 监控状态
        self.is_monitoring = False
        self.current_step = None
        self.last_check_time = 0
        self.check_interval = 0.5  # 每0.5秒检查一次
        
        # 位置状态
        self.is_position_correct = False
        self.incorrect_duration = 0  # 位置不正确的持续时间
        self.warning_threshold = 3.0  # 3秒后发出警告
        
        # 刷牙步骤对应的正确手部位置区域定义
        self.step_hand_regions = {
            "上左": {
                "target_region": {"x_min": 200, "x_max": 400, "y_min": 200, "y_max": 350},
                "description": "右手应在面部左上方区域"
            },
            "上中": {
                "target_region": {"x_min": 300, "x_max": 500, "y_min": 200, "y_max": 350},
                "description": "右手应在面部中上方区域"
            },
            "上右": {
                "target_region": {"x_min": 400, "x_max": 600, "y_min": 200, "y_max": 350},
                "description": "右手应在面部右上方区域"
            },
            "下左": {
                "target_region": {"x_min": 200, "x_max": 400, "y_min": 350, "y_max": 500},
                "description": "右手应在面部左下方区域"
            },
            "下中": {
                "target_region": {"x_min": 300, "x_max": 500, "y_min": 350, "y_max": 500},
                "description": "右手应在面部中下方区域"
            },
            "下右": {
                "target_region": {"x_min": 400, "x_max": 600, "y_min": 350, "y_max": 500},
                "description": "右手应在面部右下方区域"
            }
        }
        
        print("刷牙位置监控器初始化完成")
    
    def start_monitoring(self, step_name):
        """开始监控指定步骤的刷牙位置"""
        self.is_monitoring = True
        self.current_step = step_name
        self.last_check_time = time.time()
        self.incorrect_duration = 0
        self.is_position_correct = False
        
        print(f"开始监控 {step_name} 步骤的刷牙位置")
        
        # 发出初始状态
        if step_name in self.step_hand_regions:
            description = self.step_hand_regions[step_name]["description"]
            self.position_status_changed.emit(False, f"请将{description}")
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        self.current_step = None
        self.incorrect_duration = 0
        print("停止刷牙位置监控")
    
    def update_pose_data(self, pose_analysis):
        """更新姿态检测数据并检查位置"""
        if not self.is_monitoring or not self.current_step:
            return
        
        current_time = time.time()
        if current_time - self.last_check_time < self.check_interval:
            return
        
        self.last_check_time = current_time
        
        # 检查手部位置是否正确
        position_correct = self._check_hand_position(pose_analysis)
        
        # 更新位置状态
        if position_correct != self.is_position_correct:
            self.is_position_correct = position_correct
            self._emit_position_status()
        
        # 处理位置不正确的情况
        if not position_correct:
            self.incorrect_duration += self.check_interval
            
            # 超过警告阈值时发出警告
            if self.incorrect_duration >= self.warning_threshold:
                self._emit_warning()
                self.incorrect_duration = 0  # 重置计时器，避免频繁警告
        else:
            self.incorrect_duration = 0  # 位置正确时重置计时器
    
    def _check_hand_position(self, pose_analysis):
        """检查手部位置是否正确"""
        if not pose_analysis.get('hands_detected', False):
            return False
        
        if self.current_step not in self.step_hand_regions:
            return True  # 未定义的步骤默认为正确
        
        target_region = self.step_hand_regions[self.current_step]["target_region"]
        hand_positions = pose_analysis.get('hand_positions', [])
        
        # 检查是否有手在目标区域内
        for hand in hand_positions:
            if hand['side'] == 'right':  # 主要检查右手位置
                x, y = hand['position']
                confidence = hand['confidence']
                
                # 置信度足够高才进行位置判断
                if confidence > 0.6:
                    if (target_region["x_min"] <= x <= target_region["x_max"] and
                        target_region["y_min"] <= y <= target_region["y_max"]):
                        return True
        
        return False
    
    def _emit_position_status(self):
        """发出位置状态信号"""
        if self.current_step not in self.step_hand_regions:
            return
        
        description = self.step_hand_regions[self.current_step]["description"]
        
        if self.is_position_correct:
            status_text = f"✅ 位置正确 - {description}"
        else:
            status_text = f"⚠️ 请调整位置 - {description}"
        
        self.position_status_changed.emit(self.is_position_correct, status_text)
        print(f"位置状态更新: {status_text}")
    
    def _emit_warning(self):
        """发出警告信号"""
        if self.current_step not in self.step_hand_regions:
            return
        
        description = self.step_hand_regions[self.current_step]["description"]
        warning_text = f"❌ 位置不正确超过{self.warning_threshold}秒！{description}"
        
        self.warning_triggered.emit(warning_text)
        print(f"位置警告: {warning_text}")
    
    def get_current_status(self):
        """获取当前监控状态"""
        return {
            'is_monitoring': self.is_monitoring,
            'current_step': self.current_step,
            'is_position_correct': self.is_position_correct,
            'incorrect_duration': self.incorrect_duration
        }
    
    def update_step_regions(self, step_regions):
        """更新步骤区域定义（可用于自定义调整）"""
        self.step_hand_regions.update(step_regions)
        print("刷牙位置区域定义已更新")