"""
数据管理器 - 处理刷牙记录的存储和检索
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any

class DataManager:
    """数据管理器"""
    
    def __init__(self):
        self.data_dir = "data"
        self.records_file = os.path.join(self.data_dir, "brush_records.json")
        
        # 创建数据目录
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 初始化记录文件
        if not os.path.exists(self.records_file):
            self.save_records([])
            
    def add_brush_record(self, record: Dict[str, Any]) -> None:
        """添加刷牙记录"""
        try:
            records = self.load_records()
            
            # 添加时间戳和ID
            record['id'] = len(records) + 1
            record['date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            records.append(record)
            self.save_records(records)
            
            print(f"刷牙记录已保存: 得分={record.get('score', 0)}, 星级={record.get('stars', 0)}")
            
        except Exception as e:
            print(f"保存刷牙记录失败: {e}")
            
    def load_records(self) -> List[Dict[str, Any]]:
        """加载刷牙记录"""
        try:
            if os.path.exists(self.records_file):
                with open(self.records_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"加载刷牙记录失败: {e}")
            return []
            
    def save_records(self, records: List[Dict[str, Any]]) -> None:
        """保存刷牙记录"""
        try:
            with open(self.records_file, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存记录文件失败: {e}")
            
    def get_recent_records(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近的刷牙记录"""
        records = self.load_records()
        return records[-limit:] if records else []
        
    def get_statistics(self) -> Dict[str, Any]:
        """获取刷牙统计信息"""
        records = self.load_records()
        
        if not records:
            return {
                'total_sessions': 0,
                'average_score': 0,
                'average_duration': 0,
                'total_duration': 0,
                'best_score': 0,
                'completion_rate': 0
            }
            
        total_sessions = len(records)
        scores = [r.get('score', 0) for r in records]
        durations = [r.get('duration', 0) for r in records]
        completed_sessions = len([r for r in records if r.get('steps_completed', 0) >= 6])
        
        return {
            'total_sessions': total_sessions,
            'average_score': sum(scores) / len(scores) if scores else 0,
            'average_duration': sum(durations) / len(durations) if durations else 0,
            'total_duration': sum(durations),
            'best_score': max(scores) if scores else 0,
            'completion_rate': (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
        }
        
    def clear_records(self) -> None:
        """清空所有记录"""
        try:
            self.save_records([])
            print("所有刷牙记录已清空")
        except Exception as e:
            print(f"清空记录失败: {e}")
            
    def export_records(self, filename: str = None) -> str:
        """导出记录到文件"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"brush_records_export_{timestamp}.json"
            
        try:
            records = self.load_records()
            export_path = os.path.join(self.data_dir, filename)
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
                
            print(f"记录已导出到: {export_path}")
            return export_path
            
        except Exception as e:
            print(f"导出记录失败: {e}")
            return ""