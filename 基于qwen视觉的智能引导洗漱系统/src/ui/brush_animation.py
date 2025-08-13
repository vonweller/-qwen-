"""
刷牙动画引导组件
"""

import math
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPixmap

class BrushAnimationWidget(QWidget):
    """刷牙动画引导组件"""
    
    animation_completed = pyqtSignal(str)  # 动画完成信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_step = "准备"
        self.animation_progress = 0
        self.brush_angle = 0
        self.brush_offset_y = 0
        self.is_animating = False
        
        # 动画步骤定义 - 科学刷牙方法
        self.brush_steps = {
            "上左": {
                "color": "#FF6B6B", 
                "description": "45度角向下轻刷上牙左侧外表面\n从牙龈向牙尖方向刷10次",
                "angle_base": 45,
                "movement": "vertical_down",
                "position": "upper_left"
            },
            "上中": {
                "color": "#FF8E53", 
                "description": "45度角向下轻刷上牙中间外表面\n从牙龈向牙尖方向刷10次",
                "angle_base": 45,
                "movement": "vertical_down", 
                "position": "upper_center"
            },
            "上右": {
                "color": "#FF9F40", 
                "description": "45度角向下轻刷上牙右侧外表面\n从牙龈向牙尖方向刷10次",
                "angle_base": 45,
                "movement": "vertical_down",
                "position": "upper_right"
            },
            "下左": {
                "color": "#4ECDC4", 
                "description": "45度角向上轻刷下牙左侧外表面\n从牙龈向牙尖方向刷10次",
                "angle_base": -45,
                "movement": "vertical_up",
                "position": "lower_left"
            },
            "下中": {
                "color": "#45B7D1", 
                "description": "45度角向上轻刷下牙中间外表面\n从牙龈向牙尖方向刷10次",
                "angle_base": -45,
                "movement": "vertical_up",
                "position": "lower_center"
            },
            "下右": {
                "color": "#96CEB4", 
                "description": "45度角向上轻刷下牙右侧外表面\n从牙龈向牙尖方向刷10次",
                "angle_base": -45,
                "movement": "vertical_up",
                "position": "lower_right"
            }
        }
        
        self.init_ui()
        self.setup_animation()
        
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 动画标题
        self.title_label = QLabel("准备开始刷牙")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setObjectName("animationTitle")
        
        # 动画描述
        self.desc_label = QLabel("请按照动画指示进行刷牙")
        self.desc_label.setAlignment(Qt.AlignCenter)
        self.desc_label.setObjectName("animationDesc")
        self.desc_label.setWordWrap(True)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.desc_label)
        
        # 添加弹性空间用于动画绘制
        layout.addStretch(1)
        
        self.setup_style()
        
    def setup_animation(self):
        """设置动画定时器"""
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        
    def start_animation(self):
        """开始动画"""
        self.is_animating = True
        # 不在这里设置默认步骤，等待控制器发送具体步骤
        self.animation_progress = 0
        self.brush_angle = 0
        
        # 更新UI显示
        self.title_label.setText("开始刷牙引导")
        self.desc_label.setText("请跟随动画指示进行刷牙")
        
        # 启动动画定时器
        self.animation_timer.start(50)  # 20fps
        
        # 立即更新显示
        self.update()
        
    def start_step_animation(self, step_name):
        """开始步骤动画"""
        if step_name not in self.brush_steps:
            return
            
        self.current_step = step_name
        self.is_animating = True
        self.animation_progress = 0
        
        step_info = self.brush_steps[step_name]
        self.title_label.setText(f"正在刷 {step_name}")
        self.desc_label.setText(step_info["description"])
        
        # 启动动画定时器
        self.animation_timer.start(50)  # 20fps
        
    def stop_animation(self):
        """停止动画"""
        self.is_animating = False
        self.animation_timer.stop()
        self.animation_completed.emit(self.current_step)
        
    def set_current_step(self, step_name):
        """设置当前步骤"""
        self.start_step_animation(step_name)
        
    def update_step(self, step_name, is_active):
        """更新步骤状态 - 接收控制器信号"""
        if is_active:
            # 激活步骤时开始对应动画
            self.start_step_animation(step_name)
        else:
            # 步骤结束时可以添加结束效果
            pass
        
    def update_animation(self):
        """更新动画"""
        if not self.is_animating:
            return
            
        self.animation_progress += 3
        
        # 根据当前步骤计算不同的动画效果
        step_info = self.brush_steps.get(self.current_step, {})
        movement = step_info.get("movement", "vertical_down")
        angle_base = step_info.get("angle_base", 0)
        
        if movement == "vertical_down":
            # 上牙：从牙龈向牙尖的刷牙动作（向下）
            self.brush_angle = angle_base + math.sin(self.animation_progress * 0.15) * 10
            self.brush_offset_y = math.sin(self.animation_progress * 0.12) * 5
        elif movement == "vertical_up":
            # 下牙：从牙龈向牙尖的刷牙动作（向上）
            self.brush_angle = angle_base + math.sin(self.animation_progress * 0.15) * 10
            self.brush_offset_y = -math.sin(self.animation_progress * 0.12) * 5
        else:
            # 默认动作
            self.brush_angle = math.sin(self.animation_progress * 0.1) * 20
            self.brush_offset_y = 0
        
        # 重绘整个组件
        self.update()
        
        # 动画循环
        if self.animation_progress >= 360:
            self.animation_progress = 0
            
    def paintEvent(self, event):
        """绘制动画"""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 获取widget的中心位置
        rect = self.rect()
        center_x = rect.width() // 2
        center_y = rect.height() // 2 + 50  # 向下偏移一点，避开标题
        
        # 绘制动画背景区域
        animation_rect = rect.adjusted(20, 80, -20, -20)  # 留出边距
        painter.fillRect(animation_rect, QColor("#F8F9FA"))
        painter.setPen(QPen(QColor("#4ECDC4"), 2))
        painter.drawRoundedRect(animation_rect, 15, 15)
        
        # 绘制牙齿轮廓
        self.draw_teeth(painter, center_x, center_y)
        
        # 绘制牙刷
        self.draw_brush(painter, center_x, center_y)
        
        # 绘制动作指示
        self.draw_action_indicator(painter, center_x, center_y)
        
    def draw_teeth(self, painter, center_x, center_y):
        """绘制牙齿"""
        painter.setPen(QPen(QColor("#2C3E50"), 3))
        painter.setBrush(QBrush(QColor("#FFFFFF")))
        
        # 上牙
        upper_teeth = []
        for i in range(8):
            x = center_x - 80 + i * 20
            y = center_y - 40
            upper_teeth.append((x, y, 15, 25))
            
        # 下牙  
        lower_teeth = []
        for i in range(8):
            x = center_x - 80 + i * 20
            y = center_y + 15
            lower_teeth.append((x, y, 15, 25))
            
        # 绘制牙齿
        all_teeth = upper_teeth + lower_teeth
        for x, y, w, h in all_teeth:
            painter.drawRoundedRect(x, y, w, h, 3, 3)
            
        # 高亮当前刷牙区域
        highlight_color = QColor(self.brush_steps.get(self.current_step, {}).get("color", "#4ECDC4"))
        highlight_color.setAlpha(100)
        painter.setBrush(QBrush(highlight_color))
        
        if self.current_step == "上左":
            for x, y, w, h in upper_teeth[:3]:  # 左侧3颗牙
                painter.drawRoundedRect(x, y, w, h, 3, 3)
        elif self.current_step == "上中":
            for x, y, w, h in upper_teeth[3:5]:  # 中间2颗牙
                painter.drawRoundedRect(x, y, w, h, 3, 3)
        elif self.current_step == "上右":
            for x, y, w, h in upper_teeth[5:]:  # 右侧3颗牙
                painter.drawRoundedRect(x, y, w, h, 3, 3)
        elif self.current_step == "下左":
            for x, y, w, h in lower_teeth[:3]:  # 左侧3颗牙
                painter.drawRoundedRect(x, y, w, h, 3, 3)
        elif self.current_step == "下中":
            for x, y, w, h in lower_teeth[3:5]:  # 中间2颗牙
                painter.drawRoundedRect(x, y, w, h, 3, 3)
        elif self.current_step == "下右":
            for x, y, w, h in lower_teeth[5:]:  # 右侧3颗牙
                painter.drawRoundedRect(x, y, w, h, 3, 3)
                
    def draw_brush(self, painter, center_x, center_y):
        """绘制牙刷"""
        brush_color = QColor(self.brush_steps.get(self.current_step, {}).get("color", "#4ECDC4"))
        painter.setPen(QPen(brush_color, 4))
        
        # 根据当前步骤获取科学的刷牙位置和角度
        step_info = self.brush_steps.get(self.current_step, {})
        angle_base = step_info.get("angle_base", 0)
        
        # 计算牙刷位置
        if self.current_step in ["上左", "上中", "上右"]:
            # 上牙区域
            if self.current_step == "上左":
                brush_x = center_x - 40
            elif self.current_step == "上中":
                brush_x = center_x
            else:  # 上右
                brush_x = center_x + 40
            brush_y = center_y - 30 + self.brush_offset_y
            angle = angle_base + self.brush_angle
        elif self.current_step in ["下左", "下中", "下右"]:
            # 下牙区域
            if self.current_step == "下左":
                brush_x = center_x - 40
            elif self.current_step == "下中":
                brush_x = center_x
            else:  # 下右
                brush_x = center_x + 40
            brush_y = center_y + 30 + self.brush_offset_y
            angle = angle_base + self.brush_angle
        else:
            # 默认位置
            brush_x = center_x
            brush_y = center_y
            angle = self.brush_angle
            
        # 绘制牙刷柄
        painter.save()
        painter.translate(brush_x, brush_y)
        painter.rotate(angle)
        
        # 刷柄
        painter.setPen(QPen(QColor("#8B4513"), 3))
        painter.drawLine(0, 0, 0, -40)
        
        # 刷头
        painter.setPen(QPen(brush_color, 6))
        painter.drawLine(-3, -40, 3, -40)
        painter.drawLine(-3, -45, 3, -45)
        
        painter.restore()
        
    def draw_action_indicator(self, painter, center_x, center_y):
        """绘制科学的动作指示"""
        step_info = self.brush_steps.get(self.current_step, {})
        movement = step_info.get("movement", "vertical_down")
        
        # 绘制运动轨迹箭头
        arrow_alpha = int(128 + 127 * math.sin(self.animation_progress * 0.2))
        arrow_color = QColor("#FF6B6B")
        arrow_color.setAlpha(arrow_alpha)
        painter.setPen(QPen(arrow_color, 3))
        
        if self.current_step in ["上左", "上中", "上右"]:
            # 上牙区域 - 向下的刷牙动作
            if self.current_step == "上左":
                arrow_x = center_x - 40
            elif self.current_step == "上中":
                arrow_x = center_x
            else:  # 上右
                arrow_x = center_x + 40
            
            # 绘制向下的箭头，表示从牙龈向牙尖刷
            y_start = center_y - 70
            y_end = center_y - 50
            painter.drawLine(arrow_x, y_start, arrow_x, y_end)
            # 箭头头部
            painter.drawLine(arrow_x - 3, y_end - 5, arrow_x, y_end)
            painter.drawLine(arrow_x + 3, y_end - 5, arrow_x, y_end)
            
            # 添加文字提示
            painter.setPen(QPen(QColor("#2C3E50"), 1))
            painter.drawText(arrow_x - 20, y_start - 10, "从牙龈向下刷")
            
        elif self.current_step in ["下左", "下中", "下右"]:
            # 下牙区域 - 向上的刷牙动作
            if self.current_step == "下左":
                arrow_x = center_x - 40
            elif self.current_step == "下中":
                arrow_x = center_x
            else:  # 下右
                arrow_x = center_x + 40
            
            # 绘制向上的箭头，表示从牙龈向牙尖刷
            y_start = center_y + 70
            y_end = center_y + 50
            painter.drawLine(arrow_x, y_start, arrow_x, y_end)
            # 箭头头部
            painter.drawLine(arrow_x - 3, y_end + 5, arrow_x, y_end)
            painter.drawLine(arrow_x + 3, y_end + 5, arrow_x, y_end)
            
            # 添加文字提示
            painter.setPen(QPen(QColor("#2C3E50"), 1))
            painter.drawText(arrow_x - 20, y_start + 20, "从牙龈向上刷")
            
    def setup_style(self):
        """设置样式"""
        style = """
        #animationTitle {
            font-size: 18px;
            font-weight: bold;
            color: #2C3E50;
            margin-bottom: 10px;
        }
        
        #animationDesc {
            font-size: 12px;
            color: #6C757D;
            margin-bottom: 15px;
        }
        """
        
        self.setStyleSheet(style)