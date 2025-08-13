"""
刷牙控制器 - 管理刷牙流程和步骤
"""

from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from src.core.data_manager import DataManager
from src.core.audio_player import AudioPlayer
from src.core.qwen_analyzer import QwenAnalyzer
from src.core.async_analyzer import AsyncAnalyzer
import time

class BrushController(QObject):
    """刷牙控制器"""
    
    # 信号定义
    # 信号定义
    # 信号定义
    # 信号定义
    # 信号定义
    # 信号定义
    step_changed = pyqtSignal(str, bool)  # 步骤名称, 是否激活
    brushing_completed = pyqtSignal(int, int)  # 得分, 星级
    analysis_result = pyqtSignal(str, dict)  # 步骤名称, 分析结果
    countdown_updated = pyqtSignal(int, bool)  # 剩余秒数, 是否最后10秒
    status_changed = pyqtSignal(str)  # 状态变化信号
    progress_updated = pyqtSignal(float)  # 进度更新信号 (0.0-1.0)
    brushing_started = pyqtSignal()  # 刷牙开始信号
    analysis_completed = pyqtSignal(str, dict)  # 分析完成信号 (step_name, result)
    analysis_status_changed = pyqtSignal(str)  # 分析状态变化信号
    
    def __init__(self):
        super().__init__()
        
        # 从配置文件读取刷牙参数
        from src.utils.config_manager import ConfigManager
        self.config = ConfigManager()
        
        # 刷牙步骤定义 - 从配置读取，如果没有则使用默认值
        config_steps = self.config.get('brush_settings.brush_steps', [])
        if config_steps:
            # 如果配置中有步骤，使用配置的步骤
            self.brush_steps = config_steps
        else:
            # 使用默认的6步骤
            self.brush_steps = ["上左", "上中", "上右", "下左", "下中", "下右"]
        
        self.current_step = 0
        # 每个步骤时长 - 从配置读取
        self.step_duration = self.config.get('brush_settings.step_duration', 20)
        self.is_brushing = False
        self.start_time = None
        
        print(f"刷牙配置加载: 步骤={self.brush_steps}, 每步时长={self.step_duration}秒")
        
        # 倒计时相关
        self.remaining_time = 0
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown)
        
        # 步骤评分存储
        self.step_scores = []
        
        # 组件初始化
        self.data_manager = DataManager()
        self.audio_player = AudioPlayer()
        self.qwen_analyzer = QwenAnalyzer()
        self.async_analyzer = AsyncAnalyzer(self.qwen_analyzer)
        
        # 初始化MQTT客户端
        try:
            from src.core.mqtt_client import MQTTClient
            self.mqtt_client = MQTTClient()
            print("MQTT客户端初始化成功")
        except Exception as e:
            print(f"MQTT客户端初始化失败: {e}")
            self.mqtt_client = None
        
        # 连接异步分析器信号
        # 连接异步分析器信号
        self.async_analyzer.analysis_completed.connect(self.on_analysis_completed)
        self.async_analyzer.analysis_status_changed.connect(self.analysis_status_changed.emit)
        
        # 步骤定时器
        self.step_timer = QTimer()
        self.step_timer.timeout.connect(self.next_step)
        
        # 摄像头组件引用
        self.camera_widget = None
        
        print("刷牙控制器初始化完成")
        
    def set_camera_widget(self, camera_widget):
        """设置摄像头组件"""
        self.camera_widget = camera_widget
        print("摄像头组件已连接到刷牙控制器")
        
    def start_brushing(self):
        """开始刷牙"""
        if self.is_brushing:
            return
            
        self.is_brushing = True
        self.current_step = 0
        self.start_time = time.time()
        self.step_scores = []  # 重置评分数组
        
        # 发出刷牙开始信号
        self.brushing_started.emit()
        
        # 播放开始提示（包含天气信息）
        try:
            from src.utils.weather_api import WeatherAPI
            weather_api = WeatherAPI()
            weather_voice = weather_api.get_weather_voice_text()
            start_message = f"开始刷牙引导。{weather_voice}"
            self.audio_player.play_reminder(start_message)
        except Exception as e:
            print(f"天气播报失败: {e}")
            self.audio_player.play_reminder("开始刷牙引导")
        
        # 开始第一个步骤
        self.start_current_step()
        
        print("开始刷牙引导")
        
    def start_current_step(self):
        """开始当前步骤"""
        if self.current_step >= len(self.brush_steps):
            self.complete_brushing()
            return
            
        step_name = self.brush_steps[self.current_step]
        
        # 重置倒计时
        self.remaining_time = self.step_duration
        self.countdown_timer.start(1000)  # 每秒更新一次
        
        # 发出步骤改变信号
        self.step_changed.emit(step_name, True)
        
        # 发出进度更新信号 - 修复进度计算
        # 当前步骤开始时，进度应该反映已完成的步骤数
        progress = self.current_step / len(self.brush_steps)
        self.progress_updated.emit(progress)
        print(f"步骤 {self.current_step+1}/{len(self.brush_steps)} 开始，进度: {progress:.2f}")
        
        # 开始录制视频
        if self.camera_widget:
            self.camera_widget.start_recording(step_name, self.step_duration)
        
        # 播放步骤提示
        self.audio_player.play_reminder(f"现在刷{step_name}区域")
        
        # 启动步骤定时器
        self.step_timer.start(self.step_duration * 1000)  # 转换为毫秒
        
        print(f"开始步骤: {step_name}")
        
    def update_countdown(self):
        """更新倒计时"""
        if self.remaining_time > 0:
            self.remaining_time -= 1
            is_last_10_seconds = self.remaining_time <= 10
            self.countdown_updated.emit(self.remaining_time, is_last_10_seconds)
            
            # 更新精确进度 - 包含当前步骤内的进度
            step_progress = (self.step_duration - self.remaining_time) / self.step_duration
            total_progress = (self.current_step + step_progress) / len(self.brush_steps)
            self.progress_updated.emit(total_progress)
            
            # 最后10秒语音提醒
            if self.remaining_time == 10:
                self.audio_player.play_reminder("还有10秒")
            elif self.remaining_time == 5:
                self.audio_player.play_reminder("5秒")
            elif self.remaining_time <= 3 and self.remaining_time > 0:
                self.audio_player.play_reminder(str(self.remaining_time))
        
    def next_step(self):
        """进入下一步骤"""
        # 停止当前步骤
        self.step_timer.stop()
        self.countdown_timer.stop()
        
        # 停止录制
        if self.camera_widget and self.current_step < len(self.brush_steps):
            current_step_name = self.brush_steps[self.current_step]
            self.camera_widget.stop_recording(current_step_name)
        
        # 发出步骤结束信号
        if self.current_step < len(self.brush_steps):
            step_name = self.brush_steps[self.current_step]
            self.step_changed.emit(step_name, False)
        
        # 进入下一步骤
        self.current_step += 1
        
        if self.current_step < len(self.brush_steps):
            # 短暂延迟后开始下一步骤
            QTimer.singleShot(1000, self.start_current_step)
        else:
            self.complete_brushing()
            
    def on_analysis_completed(self, step_name, result):
        """分析完成处理"""
        print(f"{step_name} 步骤分析结果: {result}")
        
        # 收集AI评分
        if 'score' in result and isinstance(result['score'], (int, float)):
            self.step_scores.append(result['score'])
            print(f"收集到AI评分: {result['score']}, 当前评分列表: {self.step_scores}")
        
        # 发出分析结果信号
        # 发出分析结果信号
        self.analysis_result.emit(step_name, result)
        
        # 发出分析完成信号
        self.analysis_completed.emit(step_name, result)
        
        # 不在每个步骤播放详细的分析反馈，只在界面显示
        # 语音反馈将在最后的综合建议中统一播放
        pass
                
    def stop_brushing(self):
        """停止刷牙"""
        self.is_brushing = False
        self.step_timer.stop()
        self.countdown_timer.stop()
        
        # 停止录制
        if self.camera_widget and self.current_step < len(self.brush_steps):
            current_step_name = self.brush_steps[self.current_step]
            self.camera_widget.stop_recording(current_step_name)
        
        # 发出步骤结束信号
        if self.current_step < len(self.brush_steps):
            step_name = self.brush_steps[self.current_step]
            self.step_changed.emit(step_name, False)
        
        print("刷牙已停止")
        
    def complete_brushing(self):
        """完成刷牙"""
        print("开始完成刷牙流程...")
        
        self.is_brushing = False
        self.step_timer.stop()
        self.countdown_timer.stop()
        
        # 停止录制
        if self.camera_widget and self.current_step < len(self.brush_steps):
            current_step_name = self.brush_steps[self.current_step]
            self.camera_widget.stop_recording(current_step_name)
        
        # 计算总时长
        duration = time.time() - self.start_time if self.start_time else 0
        print(f"刷牙总时长: {duration:.1f}秒")
        
        # 立即计算得分，不等待所有分析完成
        score = self.calculate_score(duration)
        print(f"计算得分: {score}")
        
        # 计算星级 (1-5星)
        if score >= 90:
            stars = 5
        elif score >= 80:
            stars = 4
        elif score >= 70:
            stars = 3
        elif score >= 60:
            stars = 2
        else:
            stars = 1
        
        print(f"星级评定: {stars}星")
        
        # 生成综合建议和鼓励
        comprehensive_advice = self.generate_comprehensive_advice(score, stars, duration)
        print(f"综合建议: {comprehensive_advice}")
        
        # 立即发出完成信号，不等待
        self.brushing_completed.emit(score, stars)
        print("已发出刷牙完成信号")
        
        # 发出综合建议信号（用于界面显示）
        self.analysis_completed.emit("综合评价", {
            'score': score,
            'stars': stars,
            'feedback': comprehensive_advice,
            'is_correct': score >= 70,
            'detected_issues': [],
            'good_points': []
        })
        print("已发出综合评价信号")
        
        # 异步播放音频，避免阻塞UI
        def play_completion_audio():
            try:
                print("开始播放完成音频...")
                self.audio_player.play_congratulations()
                
                # 播放综合建议
                if comprehensive_advice:
                    print("播放综合建议...")
                    self.audio_player.play_text_to_speech(comprehensive_advice)
                print("音频播放完成")
            except Exception as e:
                print(f"音频播放失败: {e}")
        
        # 使用QTimer异步执行音频播放
        QTimer.singleShot(500, play_completion_audio)
        
        # 异步保存记录，避免阻塞
        def save_record():
            try:
                print("保存刷牙记录...")
                record = {
                    'duration': duration,
                    'score': score,
                    'stars': stars,
                    'steps_completed': self.current_step,
                    'step_scores': self.step_scores,
                    'comprehensive_advice': comprehensive_advice,
                    'timestamp': time.time()
                }
                self.data_manager.add_brush_record(record)
                print("记录保存完成")
            except Exception as e:
                print(f"保存记录失败: {e}")
        
        # 使用QTimer异步保存记录
        QTimer.singleShot(100, save_record)
        
        print(f"刷牙完成! 得分: {score}, 星级: {stars}")
    
    def generate_comprehensive_advice(self, score, stars, duration):
        """生成综合建议和鼓励"""
        try:
            # 基于得分生成不同的建议
            if score >= 90:
                base_msg = "太棒了！您的刷牙技巧非常出色"
                encouragement = "继续保持这样的好习惯，您的口腔健康会越来越好！"
            elif score >= 80:
                base_msg = "很好！您的刷牙动作基本规范"
                encouragement = "稍加改进就能达到完美水平，加油！"
            elif score >= 70:
                base_msg = "不错！您已经掌握了基本的刷牙要领"
                encouragement = "继续练习，注意细节，您会做得更好！"
            elif score >= 60:
                base_msg = "还可以！您的刷牙有一定基础"
                encouragement = "多注意角度和力度，相信您会进步很快！"
            else:
                base_msg = "需要加油！刷牙技巧还有提升空间"
                encouragement = "不要气馁，多练习就会有进步，坚持就是胜利！"
            
            # 基于时长的建议
            recommended_time = len(self.brush_steps) * self.step_duration
            if duration < recommended_time * 0.8:
                time_advice = "建议延长刷牙时间，每个区域至少刷20秒。"
            elif duration > recommended_time * 1.2:
                time_advice = "刷牙时间很充足，注意保持适中的力度。"
            else:
                time_advice = "刷牙时间控制得很好。"
            
            # 基于步骤完成情况的建议
            if self.current_step >= len(self.brush_steps):
                completion_advice = "您完成了所有刷牙步骤，很棒！"
            else:
                completion_advice = f"建议完成所有{len(self.brush_steps)}个步骤，确保全面清洁。"
            
            # 组合建议
            comprehensive_advice = f"{base_msg}。{time_advice}{completion_advice}{encouragement}"
            
            return comprehensive_advice
            
        except Exception as e:
            print(f"生成综合建议失败: {e}")
            return "刷牙完成！继续保持良好的口腔卫生习惯！"
        
    def calculate_score(self, duration):
        """计算刷牙得分"""
        # 如果有AI评分，使用AI评分的平均值作为主要得分
        if self.step_scores:
            ai_average_score = sum(self.step_scores) / len(self.step_scores)
            
            # 时长修正系数
            recommended_time = len(self.brush_steps) * self.step_duration
            time_factor = min(1.1, duration / recommended_time)  # 最多加10%
            
            # 完成度修正系数
            completion_factor = self.current_step / len(self.brush_steps)
            
            # 最终得分 = AI平均分 × 时长系数 × 完成度系数
            final_score = ai_average_score * time_factor * completion_factor
            print(f"AI评分计算: 平均分={ai_average_score:.1f}, 时长系数={time_factor:.2f}, 完成度={completion_factor:.2f}, 最终得分={final_score:.1f}")
            return int(min(100, max(0, final_score)))
        else:
            # 备用计算方法（如果没有AI评分）
            base_score = 60
            recommended_time = len(self.brush_steps) * self.step_duration
            if duration >= recommended_time * 0.8:
                time_bonus = min(30, int((duration / recommended_time) * 30))
            else:
                time_bonus = int((duration / (recommended_time * 0.8)) * 20)
            
            step_bonus = (self.current_step / len(self.brush_steps)) * 10
            total_score = min(100, base_score + time_bonus + step_bonus)
            return int(total_score)
            
    def get_current_step_name(self):
        """获取当前步骤名称"""
        if 0 <= self.current_step < len(self.brush_steps):
            return self.brush_steps[self.current_step]
        return None
        
    def get_progress(self):
        """获取刷牙进度"""
        if not self.is_brushing:
            return 0.0
        return self.current_step / len(self.brush_steps)
        
    def is_step_active(self, step_name):
        """检查步骤是否激活"""
        if not self.is_brushing:
            return False
        current_step_name = self.get_current_step_name()
        return current_step_name == step_name