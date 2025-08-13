"""
游戏化评分系统
"""

from datetime import datetime, timedelta
from src.utils.data_manager import DataManager

class RatingSystem:
    """游戏化评分系统"""
    
    def __init__(self):
        self.data_manager = DataManager()
        
        # 段位系统定义
        self.ranks = [
            {"name": "黑铁", "min_stars": 0, "color": "#4A4A4A", "icon": "🔩"},
            {"name": "青铜", "min_stars": 50, "color": "#CD7F32", "icon": "🥉"},
            {"name": "白银", "min_stars": 150, "color": "#C0C0C0", "icon": "🥈"},
            {"name": "黄金", "min_stars": 300, "color": "#FFD700", "icon": "🥇"},
            {"name": "铂金", "min_stars": 500, "color": "#E5E4E2", "icon": "💎"},
            {"name": "钻石", "min_stars": 800, "color": "#B9F2FF", "icon": "💠"},
            {"name": "大师", "min_stars": 1200, "color": "#FF6B6B", "icon": "👑"},
            {"name": "王者", "min_stars": 2000, "color": "#9B59B6", "icon": "⭐"}
        ]
        
    def calculate_brush_score(self, duration, completed_steps, total_steps, qwen_feedback=None):
        """计算刷牙评分"""
        base_score = 60  # 基础分数
        
        # 完成度评分 (30分)
        completion_score = (completed_steps / total_steps) * 30
        
        # 时长评分 (20分)
        ideal_duration = 120  # 理想刷牙时长2分钟
        if duration >= ideal_duration:
            duration_score = 20
        else:
            duration_score = (duration / ideal_duration) * 20
            
        # AI反馈评分 (20分)
        ai_score = 0
        if qwen_feedback:
            ai_score = qwen_feedback.get('score', 80) * 0.2
            
        total_score = base_score + completion_score + duration_score + ai_score
        return min(int(total_score), 100)
        
    def calculate_stars(self, score):
        """根据评分计算星星数量"""
        if score >= 95:
            return 5
        elif score >= 85:
            return 4
        elif score >= 75:
            return 3
        elif score >= 65:
            return 2
        elif score >= 50:
            return 1
        else:
            return 0
            
    def get_star_penalty(self, score):
        """计算星星扣除"""
        if score < 50:
            return 1  # 表现不佳扣除1颗星
        return 0
        
    def calculate_daily_bonus(self, consecutive_days):
        """计算每日连续打卡奖励"""
        return consecutive_days  # 每天坚持打卡获得1*打卡天数的星星
        
    def update_user_rating(self, brush_record):
        """更新用户评级"""
        user_data = self.data_manager.get_user_data()
        
        # 计算本次刷牙得分
        score = self.calculate_brush_score(
            brush_record.get('duration', 0),
            brush_record.get('completed_steps', 0),
            brush_record.get('total_steps', 4),
            brush_record.get('qwen_feedback')
        )
        
        # 计算星星
        earned_stars = self.calculate_stars(score)
        penalty_stars = self.get_star_penalty(score)
        
        # 更新总星星数
        current_stars = user_data.get('rating', {}).get('total_stars', 0)
        new_stars = max(0, current_stars + earned_stars - penalty_stars)
        
        # 计算连续打卡奖励
        consecutive_days = self.get_consecutive_days()
        daily_bonus = self.calculate_daily_bonus(consecutive_days)
        new_stars += daily_bonus
        
        # 计算段位
        current_rank = self.get_rank_by_stars(new_stars)
        
        # 更新用户数据
        rating_data = {
            'total_stars': new_stars,
            'current_rank': current_rank,
            'consecutive_days': consecutive_days,
            'last_brush_date': datetime.now().date().isoformat(),
            'daily_bonus': daily_bonus,
            'last_score': score,
            'last_earned_stars': earned_stars,
            'last_penalty_stars': penalty_stars
        }
        
        user_data['rating'] = rating_data
        self.data_manager.save_user_data(user_data)
        
        return {
            'score': score,
            'earned_stars': earned_stars,
            'penalty_stars': penalty_stars,
            'daily_bonus': daily_bonus,
            'total_stars': new_stars,
            'rank': current_rank,
            'consecutive_days': consecutive_days
        }
        
    def get_consecutive_days(self):
        """计算连续打卡天数"""
        records = self.data_manager.get_brush_records()
        if not records:
            return 0
            
        # 按日期分组
        dates = set()
        for record in records:
            timestamp = record.get('timestamp', '')
            if timestamp:
                try:
                    date = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).date()
                    dates.add(date)
                except:
                    continue
                    
        if not dates:
            return 0
            
        # 计算连续天数
        sorted_dates = sorted(dates, reverse=True)
        consecutive = 0
        current_date = datetime.now().date()
        
        for date in sorted_dates:
            if date == current_date or date == current_date - timedelta(days=consecutive):
                consecutive += 1
                current_date = date
            else:
                break
                
        return consecutive
        
    def get_rank_by_stars(self, stars):
        """根据星星数获取段位"""
        for i in range(len(self.ranks) - 1, -1, -1):
            if stars >= self.ranks[i]['min_stars']:
                return self.ranks[i]
        return self.ranks[0]  # 默认黑铁
        
    def get_current_rating(self):
        """获取当前评级信息"""
        user_data = self.data_manager.get_user_data()
        rating_data = user_data.get('rating', {})
        
        total_stars = rating_data.get('total_stars', 0)
        current_rank = self.get_rank_by_stars(total_stars)
        
        # 计算到下一段位需要的星星
        next_rank = None
        stars_to_next = 0
        
        for rank in self.ranks:
            if rank['min_stars'] > total_stars:
                next_rank = rank
                stars_to_next = rank['min_stars'] - total_stars
                break
                
        return {
            'total_stars': total_stars,
            'current_rank': current_rank,
            'next_rank': next_rank,
            'stars_to_next': stars_to_next,
            'consecutive_days': rating_data.get('consecutive_days', 0),
            'last_score': rating_data.get('last_score', 0),
            'daily_bonus': rating_data.get('daily_bonus', 0)
        }
        
    def get_rank_progress(self):
        """获取段位进度"""
        rating = self.get_current_rating()
        current_rank = rating['current_rank']
        total_stars = rating['total_stars']
        
        # 计算当前段位的进度
        current_min = current_rank['min_stars']
        next_rank = rating['next_rank']
        
        if next_rank:
            next_min = next_rank['min_stars']
            progress = (total_stars - current_min) / (next_min - current_min)
        else:
            progress = 1.0  # 已达到最高段位
            
        return min(max(progress, 0.0), 1.0)
        
    def format_rating_display(self):
        """格式化评级显示信息"""
        rating = self.get_current_rating()
        
        rank_info = f"{rating['current_rank']['icon']} {rating['current_rank']['name']}"
        stars_info = f"⭐ {rating['total_stars']}"
        
        if rating['next_rank']:
            next_info = f"距离 {rating['next_rank']['name']} 还需 {rating['stars_to_next']} 颗星"
        else:
            next_info = "已达到最高段位！"
            
        consecutive_info = f"连续打卡 {rating['consecutive_days']} 天"
        
        return {
            'rank_display': rank_info,
            'stars_display': stars_info,
            'progress_display': next_info,
            'consecutive_display': consecutive_info,
            'last_score': rating['last_score'],
            'daily_bonus': rating['daily_bonus']
        }