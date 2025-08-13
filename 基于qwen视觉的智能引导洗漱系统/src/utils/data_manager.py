"""
数据管理器 - 处理用户数据和刷牙记录
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

class DataManager:
    """数据管理器"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.user_data_file = os.path.join(data_dir, "user_data.json")
        self.brush_records_file = os.path.join(data_dir, "brush_records.json")
        
        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)
        
        # 初始化数据文件
        self._init_data_files()
    
    def _init_data_files(self):
        """初始化数据文件"""
        # 初始化用户数据
        if not os.path.exists(self.user_data_file):
            default_user_data = {
                "settings": {
                    "morning_time": "08:00",
                    "evening_time": "21:00",
                    "brush_duration": 120,
                    "volume": 0.8,
                    "difficulty": "normal"
                },
                "achievements": {
                    "total_brushes": 0,
                    "consecutive_days": 0,
                    "perfect_brushes": 0,
                    "badges": []
                }
            }
            self._save_json(self.user_data_file, default_user_data)
        
        # 初始化刷牙记录
        if not os.path.exists(self.brush_records_file):
            self._save_json(self.brush_records_file, [])
    
    def _load_json(self, file_path: str) -> Any:
        """加载JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    def _save_json(self, file_path: str, data: Any):
        """保存JSON文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存文件失败 {file_path}: {e}")
    
    def get_user_data(self) -> Dict[str, Any]:
        """获取用户数据"""
        return self._load_json(self.user_data_file) or {}
    
    def save_user_data(self, data: Dict[str, Any]):
        """保存用户数据"""
        self._save_json(self.user_data_file, data)
    
    def get_brush_records(self) -> List[Dict[str, Any]]:
        """获取刷牙记录"""
        return self._load_json(self.brush_records_file) or []
    
    def add_brush_record(self, record: Dict[str, Any]):
        """添加刷牙记录"""
        records = self.get_brush_records()
        record['timestamp'] = datetime.now().isoformat()
        records.append(record)
        self._save_json(self.brush_records_file, records)
        
        # 更新成就数据
        self._update_achievements(record)
    
    def _update_achievements(self, record: Dict[str, Any]):
        """更新成就数据"""
        user_data = self.get_user_data()
        achievements = user_data.get('achievements', {})
        
        # 更新总刷牙次数
        achievements['total_brushes'] = achievements.get('total_brushes', 0) + 1
        
        # 检查是否完美刷牙
        if record.get('score', 0) >= 90:
            achievements['perfect_brushes'] = achievements.get('perfect_brushes', 0) + 1
        
        # 更新连续天数（简化实现）
        today = datetime.now().date().isoformat()
        records = self.get_brush_records()
        today_records = [r for r in records if r.get('timestamp', '').startswith(today)]
        if len(today_records) >= 2:  # 早晚都刷牙
            achievements['consecutive_days'] = achievements.get('consecutive_days', 0) + 1
        
        # 检查新徽章
        self._check_new_badges(achievements)
        
        user_data['achievements'] = achievements
        self.save_user_data(user_data)
    
    def _check_new_badges(self, achievements: Dict[str, Any]):
        """检查新徽章"""
        badges = achievements.get('badges', [])
        total_brushes = achievements.get('total_brushes', 0)
        consecutive_days = achievements.get('consecutive_days', 0)
        perfect_brushes = achievements.get('perfect_brushes', 0)
        
        # 定义徽章条件
        badge_conditions = [
            ('初学者', total_brushes >= 1),
            ('坚持者', total_brushes >= 10),
            ('专家', total_brushes >= 50),
            ('大师', total_brushes >= 100),
            ('连续一周', consecutive_days >= 7),
            ('连续一月', consecutive_days >= 30),
            ('完美主义者', perfect_brushes >= 10)
        ]
        
        for badge_name, condition in badge_conditions:
            if condition and badge_name not in badges:
                badges.append(badge_name)
        
        achievements['badges'] = badges