"""
评分显示组件
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QProgressBar, QFrame, QGridLayout)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont, QLinearGradient
from src.core.rating_system import RatingSystem

class RatingWidget(QWidget):
    """评分显示组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rating_system = RatingSystem()
        
        self.init_ui()
        self.update_display()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setFixedSize(480, 320)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # 评分结果标题
        self.title_label = QLabel("刷牙完成！")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setObjectName("ratingTitle")
        
        # 分数显示
        self.score_label = QLabel("0分")
        self.score_label.setAlignment(Qt.AlignCenter)
        self.score_label.setObjectName("scoreLabel")
        
        # 星级显示
        self.stars_label = QLabel("☆☆☆")
        self.stars_label.setAlignment(Qt.AlignCenter)
        self.stars_label.setObjectName("starsLabel")
        
        # 评价文本
        self.comment_label = QLabel("继续努力！")
        self.comment_label.setAlignment(Qt.AlignCenter)
        self.comment_label.setObjectName("commentLabel")
        self.comment_label.setWordWrap(True)
        
        # 段位信息
        self.rank_label = QLabel("当前段位：黑铁")
        self.rank_label.setAlignment(Qt.AlignCenter)
        self.rank_label.setObjectName("rankLabel")
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.score_label)
        layout.addWidget(self.stars_label)
        layout.addWidget(self.comment_label)
        layout.addWidget(self.rank_label)
        
        self.setup_style()
        
    def show_rating(self, score, stars):
        """显示评分结果"""
        # 更新分数显示
        self.score_label.setText(f"{score}分")
        
        # 更新星级显示
        star_display = "⭐" * stars + "☆" * (3 - stars)
        self.stars_label.setText(star_display)
        
        # 根据分数设置评价
        if score >= 85:
            comment = "太棒了！刷牙技术很专业！"
            score_color = "#4CAF50"
        elif score >= 70:
            comment = "不错！继续保持！"
            score_color = "#FF9800"
        elif score >= 50:
            comment = "还可以，需要多练习！"
            score_color = "#FF5722"
        else:
            comment = "需要改进刷牙方法哦！"
            score_color = "#F44336"
            
        self.comment_label.setText(comment)
        self.score_label.setStyleSheet(f"color: {score_color}; font-size: 36px; font-weight: bold;")
        
        # 更新评分系统
        # 更新评分系统 - 创建刷牙记录
        # 更新评分系统 - 创建刷牙记录
        from datetime import datetime
        brush_record = {
            'score': score,
            'duration': 120,  # 默认2分钟
            'completed_steps': 6,  # 默认完成所有步骤
            'total_steps': 6,
            'timestamp': datetime.now().isoformat()
        }
        rating_result = self.rating_system.update_user_rating(brush_record)
        
        # 更新段位显示
        rating_info = self.rating_system.get_current_rating()
        current_rank = rating_info['current_rank']
        self.rank_label.setText(f"当前段位：{current_rank['icon']} {current_rank['name']}")
        self.rank_label.setStyleSheet(f"color: {current_rank['color']}; font-weight: bold;")
        
    def update_display(self):
        """更新显示"""
        rating_info = self.rating_system.get_current_rating()
        
        # 更新段位信息
        current_rank = rating_info['current_rank']
        self.rank_label.setText(f"当前段位：{current_rank['icon']} {current_rank['name']}")
        self.rank_label.setStyleSheet(f"color: {current_rank['color']}; font-weight: bold;")
        
        # 更新最近评分
        last_score = rating_info['last_score']
        self.score_label.setText(f"{last_score}分")
        
        # 根据评分设置颜色
        if last_score >= 85:
            score_color = "#4CAF50"
        elif last_score >= 70:
            score_color = "#FF9800"
        else:
            score_color = "#F44336"
            
        self.score_label.setStyleSheet(f"color: {score_color}; font-size: 36px; font-weight: bold;")
        
        # 显示评分对应的星星
        stars = self.rating_system.calculate_stars(last_score)
        star_display = "⭐" * stars + "☆" * (3 - stars)
        self.stars_label.setText(star_display)
        
    def setup_style(self):
        """设置样式"""
        style = """
        QWidget {
            background-color: #F8F9FA;
            border-radius: 15px;
            border: 2px solid #4ECDC4;
        }
        
        #ratingTitle {
            font-size: 24px;
            font-weight: bold;
            color: #2C3E50;
            margin: 10px;
        }
        
        #scoreLabel {
            font-size: 36px;
            font-weight: bold;
            color: #4CAF50;
            margin: 10px;
        }
        
        #starsLabel {
            font-size: 32px;
            margin: 10px;
        }
        
        #commentLabel {
            font-size: 16px;
            color: #6C757D;
            margin: 10px;
        }
        
        #rankLabel {
            font-size: 14px;
            font-weight: bold;
            margin: 10px;
        }
        """
        
        self.setStyleSheet(style)