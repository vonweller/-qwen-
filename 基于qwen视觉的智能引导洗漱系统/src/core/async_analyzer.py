"""
异步分析器 - 优化QwenAI流式接收和性能
"""

from PyQt5.QtCore import QThread, pyqtSignal
import time
import numpy as np

class AsyncAnalyzer(QThread):
    """异步分析线程"""
    
    analysis_completed = pyqtSignal(str, dict)  # step_name, result
    analysis_status_changed = pyqtSignal(str)
    
    def __init__(self, qwen_analyzer):
        super().__init__()
        self.qwen_analyzer = qwen_analyzer
        self.video_frames = None
        self.step_name = None
        
    def analyze_frames(self, frames, step_name):
        """设置分析参数并启动分析（使用内存中的帧）"""
        self.video_frames = frames
        self.step_name = step_name
        self.start()
        
    def analyze_video(self, video_path, step_name):
        """兼容旧接口：从视频文件分析"""
        self.video_path = video_path
        self.video_frames = None
        self.step_name = step_name
        self.start()
        
    def run(self):
        """运行分析"""
        try:
            # 发出分析开始状态
            self.analysis_status_changed.emit("🔄 正在分析...")
            
            # 执行分析（在后台线程中）
            if self.video_frames is not None:
                # 使用内存中的帧进行分析
                analysis_result = self.qwen_analyzer.analyze_brushing_frames(
                    self.video_frames, 
                    self.step_name
                )
            else:
                # 使用视频文件进行分析（兼容旧方式）
                analysis_result = self.qwen_analyzer.analyze_brushing_video(
                    self.video_path, 
                    self.step_name
                )
            
            if analysis_result:
                # 发出分析完成状态
                self.analysis_status_changed.emit("✅ 分析完成")
                
                # 发出分析结果（包含step_name）
                self.analysis_completed.emit(self.step_name, analysis_result)
                
                print(f"{self.step_name} 步骤分析结果: {analysis_result}")
            else:
                # 分析失败
                self.analysis_status_changed.emit("❌ 分析失败")
                self.analysis_completed.emit(self.step_name, {
                    'is_correct': False,
                    'score': 0,
                    'feedback': '分析服务暂时不可用，请检查网络连接后重试',
                    'detected_issues': ['分析服务不可用'],
                    'good_points': []
                })
                
        except Exception as e:
            print(f"异步分析错误: {e}")
            self.analysis_status_changed.emit("❌ 分析错误")
            self.analysis_completed.emit(self.step_name, {
                'is_correct': False,
                'score': 0,
                'feedback': f'分析出现错误，请重新开始: {str(e)[:30]}...',
                'detected_issues': ['系统异常'],
                'good_points': []
            })
