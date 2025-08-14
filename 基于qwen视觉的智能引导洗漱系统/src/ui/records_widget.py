"""
记录查看组件
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QFrame, QGridLayout, QProgressBar)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from datetime import datetime, timedelta
from src.utils.data_manager import DataManager

class RecordsWidget(QWidget):
    """记录查看组件"""
    
    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()
        
        self.init_ui()
        self.load_data()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("刷牙记录")
        self.setGeometry(200, 200, 800, 600)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建统计卡片
        self.create_stats_cards(layout)
        
        # 创建记录表格
        self.create_records_table(layout)
        
        # 创建成就展示
        self.create_achievements_section(layout)
        
        self.setup_style()
        
    def create_stats_cards(self, parent_layout):
        """创建统计卡片"""
        stats_frame = QFrame()
        stats_layout = QGridLayout(stats_frame)
        stats_layout.setSpacing(15)
        
        # 获取统计数据
        user_data = self.data_manager.get_user_data()
        achievements = user_data.get('achievements', {})
        
        # 总刷牙次数卡片
        total_card = self.create_stat_card(
            "总刷牙次数", 
            str(achievements.get('total_brushes', 0)), 
            "次"
        )
        
        # 连续天数卡片
        consecutive_card = self.create_stat_card(
            "连续天数", 
            str(achievements.get('consecutive_days', 0)), 
            "天"
        )
        
        # 完美刷牙卡片
        perfect_card = self.create_stat_card(
            "完美刷牙", 
            str(achievements.get('perfect_brushes', 0)), 
            "次"
        )
        
        # 获得徽章卡片
        badges_count = len(achievements.get('badges', []))
        badges_card = self.create_stat_card(
            "获得徽章", 
            str(badges_count), 
            "个"
        )
        
        stats_layout.addWidget(total_card, 0, 0)
        stats_layout.addWidget(consecutive_card, 0, 1)
        stats_layout.addWidget(perfect_card, 0, 2)
        stats_layout.addWidget(badges_card, 0, 3)
        
        parent_layout.addWidget(stats_frame)
        
    def create_stat_card(self, title, value, unit):
        """创建统计卡片"""
        card = QFrame()
        card.setObjectName("statCard")
        card.setFixedHeight(100)
        
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel(title)
        title_label.setObjectName("statTitle")
        title_label.setAlignment(Qt.AlignCenter)
        
        value_layout = QHBoxLayout()
        value_layout.setAlignment(Qt.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setObjectName("statValue")
        
        unit_label = QLabel(unit)
        unit_label.setObjectName("statUnit")
        
        value_layout.addWidget(value_label)
        value_layout.addWidget(unit_label)
        
        layout.addWidget(title_label)
        layout.addLayout(value_layout)
        
        return card
        
    def create_records_table(self, parent_layout):
        """创建记录表格"""
        table_frame = QFrame()
        table_layout = QVBoxLayout(table_frame)
        
        # 表格标题
        title_label = QLabel("最近刷牙记录")
        title_label.setObjectName("sectionTitle")
        table_layout.addWidget(title_label)
        
        # 创建表格
        self.records_table = QTableWidget()
        self.records_table.setColumnCount(6)
        self.records_table.setHorizontalHeaderLabels([
            "日期时间", "持续时长", "完成步骤", "评分", "状态", "QwenAI评价"
        ])
        
        # 设置表格属性
        header = self.records_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Stretch)  # QwenAI评价列可拉伸
        
        self.records_table.setAlternatingRowColors(True)
        self.records_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        table_layout.addWidget(self.records_table)
        parent_layout.addWidget(table_frame)
        
    def create_achievements_section(self, parent_layout):
        """创建成就展示区域"""
        achievements_frame = QFrame()
        achievements_layout = QVBoxLayout(achievements_frame)
        
        # 成就标题
        title_label = QLabel("获得的徽章")
        title_label.setObjectName("sectionTitle")
        achievements_layout.addWidget(title_label)
        
        # 徽章网格
        badges_grid = QGridLayout()
        badges_grid.setSpacing(10)
        
        # 获取徽章数据
        user_data = self.data_manager.get_user_data()
        earned_badges = user_data.get('achievements', {}).get('badges', [])
        
        # 所有可能的徽章
        all_badges = [
            "初学者", "坚持者", "专家", "大师",
            "连续一周", "连续一月", "完美主义者"
        ]
        
        row, col = 0, 0
        for badge in all_badges:
            badge_widget = self.create_badge_widget(badge, badge in earned_badges)
            badges_grid.addWidget(badge_widget, row, col)
            
            col += 1
            if col >= 4:
                col = 0
                row += 1
                
        achievements_layout.addLayout(badges_grid)
        parent_layout.addWidget(achievements_frame)
        
    def create_badge_widget(self, badge_name, earned=False):
        """创建徽章组件"""
        badge = QFrame()
        badge.setObjectName("badge")
        badge.setFixedSize(120, 80)
        
        if earned:
            badge.setProperty("earned", True)
        
        layout = QVBoxLayout(badge)
        layout.setAlignment(Qt.AlignCenter)
        
        # 徽章图标（使用emoji代替）
        icon_map = {
            "初学者": "🌱",
            "坚持者": "💪",
            "专家": "⭐",
            "大师": "👑",
            "连续一周": "📅",
            "连续一月": "🗓️",
            "完美主义者": "💎"
        }
        
        icon_label = QLabel(icon_map.get(badge_name, "🏆"))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 24px;")
        
        name_label = QLabel(badge_name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setObjectName("badgeName")
        
        layout.addWidget(icon_label)
        layout.addWidget(name_label)
        
        return badge
        
    def load_data(self):
        """加载数据"""
        records = self.data_manager.get_brush_records()
        
        # 按时间倒序排列，显示最近20条记录
        # 确保所有timestamp都是字符串类型，避免字符串和浮点数比较错误
        def safe_timestamp_key(record):
            timestamp = record.get('timestamp', '')
            # 如果是数字类型，转换为ISO格式字符串
            if isinstance(timestamp, (int, float)):
                try:
                    from datetime import datetime
                    return datetime.fromtimestamp(timestamp).isoformat()
                except:
                    return str(timestamp)
            return str(timestamp)
            
        records.sort(key=safe_timestamp_key, reverse=True)
        recent_records = records[:20]
        
        self.records_table.setRowCount(len(recent_records))
        
        for row, record in enumerate(recent_records):
            # 日期时间
            timestamp = record.get('timestamp', '')
            if timestamp:
                try:
                    # 处理不同类型的时间戳
                    if isinstance(timestamp, (int, float)):
                        # 数字类型时间戳转换为datetime对象
                        dt = datetime.fromtimestamp(timestamp)
                        date_str = dt.strftime('%Y-%m-%d %H:%M')
                    else:
                        # 字符串类型时间戳
                        dt = datetime.fromisoformat(str(timestamp).replace('Z', '+00:00'))
                        date_str = dt.strftime('%Y-%m-%d %H:%M')
                except Exception as e:
                    print(f"时间戳转换错误: {e}, 时间戳类型: {type(timestamp)}, 值: {timestamp}")
                    # 安全的备用方案
                    date_str = str(timestamp)[:16] if isinstance(timestamp, str) else "格式错误"
            else:
                date_str = "未知"
                
            self.records_table.setItem(row, 0, QTableWidgetItem(date_str))
            
            # 持续时长
            duration = record.get('duration', 0)
            duration_str = f"{int(duration)}秒"
            self.records_table.setItem(row, 1, QTableWidgetItem(duration_str))
            
            # 完成步骤
            completed_steps = record.get('completed_steps', 0)
            total_steps = record.get('total_steps', 4)
            steps_str = f"{completed_steps}/{total_steps}"
            self.records_table.setItem(row, 2, QTableWidgetItem(steps_str))
            
            # 评分
            score = record.get('score', 0)
            score_item = QTableWidgetItem(f"{score}分")
            
            # 根据评分设置颜色
            if score >= 90:
                score_item.setForeground(QColor(76, 175, 80))  # 绿色
            elif score >= 70:
                score_item.setForeground(QColor(255, 193, 7))  # 黄色
            else:
                score_item.setForeground(QColor(244, 67, 54))  # 红色
                
            self.records_table.setItem(row, 3, score_item)
            
            # 状态
            if completed_steps >= total_steps:
                status = "完成"
                status_color = QColor(76, 175, 80)
            else:
                status = "未完成"
                status_color = QColor(244, 67, 54)
                
            status_item = QTableWidgetItem(status)
            status_item.setForeground(status_color)
            self.records_table.setItem(row, 4, status_item)
            
            # QwenAI评价
            comprehensive_advice = record.get('comprehensive_advice', '暂无评价')
            advice_item = QTableWidgetItem(comprehensive_advice)
            advice_item.setToolTip(comprehensive_advice)  # 鼠标悬停显示完整内容
            
            # 根据评价内容设置颜色
            if '很好' in comprehensive_advice or '完美' in comprehensive_advice:
                advice_item.setForeground(QColor(76, 175, 80))  # 绿色
            elif '需要加油' in comprehensive_advice or '提升空间' in comprehensive_advice:
                advice_item.setForeground(QColor(244, 67, 54))  # 红色
            else:
                advice_item.setForeground(QColor(255, 193, 7))  # 黄色
                
            self.records_table.setItem(row, 5, advice_item)
            
    def setup_style(self):
        """设置样式"""
        style = """
        QWidget {
            background-color: #F8F9FA;
        }
        
        #statCard {
            background-color: white;
            border-radius: 10px;
            border: 1px solid #E9ECEF;
        }
        
        #statTitle {
            font-size: 14px;
            color: #6C757D;
            font-weight: bold;
        }
        
        #statValue {
            font-size: 28px;
            color: #2C3E50;
            font-weight: bold;
        }
        
        #statUnit {
            font-size: 14px;
            color: #6C757D;
            margin-left: 5px;
        }
        
        #sectionTitle {
            font-size: 18px;
            font-weight: bold;
            color: #2C3E50;
            margin-bottom: 10px;
        }
        
        QTableWidget {
            background-color: white;
            border-radius: 8px;
            border: 1px solid #E9ECEF;
            gridline-color: #E9ECEF;
        }
        
        QTableWidget::item {
            padding: 8px;
        }
        
        QHeaderView::section {
            background-color: #4ECDC4;
            color: white;
            padding: 8px;
            border: none;
            font-weight: bold;
        }
        
        #badge {
            background-color: #E9ECEF;
            border-radius: 8px;
            border: 2px solid #DEE2E6;
        }
        
        #badge[earned="true"] {
            background-color: #4ECDC4;
            border-color: #45B7B8;
        }
        
        #badgeName {
            font-size: 12px;
            font-weight: bold;
            color: #6C757D;
        }
        
        #badge[earned="true"] #badgeName {
            color: white;
        }
        """
        
        self.setStyleSheet(style)