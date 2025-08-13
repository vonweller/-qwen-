"""
音频播放器 - 处理语音提示和音效
"""

import pygame
import os
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from src.utils.config_manager import ConfigManager

class AudioPlayer(QObject):
    """音频播放器"""
    
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.volume = self.config.get('audio.volume', 0.8)
        
        # 初始化pygame音频
        try:
            pygame.mixer.init()
            print("音频系统初始化成功")
        except Exception as e:
            print(f"音频系统初始化失败: {e}")
            
        # 创建音频文件目录
        self.audio_dir = "assets/audio"
        os.makedirs(self.audio_dir, exist_ok=True)
        
        # TTS引擎不在初始化时创建，每次使用时创建
        self.tts_available = self._check_tts_availability()
        print(f"TTS引擎可用性: {'可用' if self.tts_available else '不可用'}")
    
    def _check_tts_availability(self):
        """检查TTS引擎可用性"""
        try:
            import pyttsx3
            # 测试创建引擎
            test_engine = pyttsx3.init()
            test_engine.stop()
            del test_engine
            return True
        except ImportError:
            print("pyttsx3未安装")
            return False
        except Exception as e:
            print(f"TTS引擎测试失败: {e}")
            return False
        
    def play_reminder(self, message):
        """播放提醒语音"""
        try:
            # 使用系统TTS或预录音频
            self.play_text_to_speech(message)
        except Exception as e:
            print(f"播放提醒失败: {e}")
            # 备用方案：使用系统提示音
            self.play_system_beep()
            
    def play_text_to_speech(self, text):
        """文本转语音播放 - 还原同步版本"""
        if not text or len(text.strip()) == 0:
            return
            
        print(f"TTS播放: {text}")
        
        # 方法1：尝试使用Windows SAPI
        if self._try_windows_sapi(text):
            return
            
        # 方法2：尝试使用pyttsx3
        if self._try_pyttsx3(text):
            return
            
        # 方法3：备用方案 - 系统提示音
        print(f"TTS播放失败，使用系统提示音: {text}")
        self.play_system_beep()
    
    def _try_windows_sapi(self, text):
        """尝试使用Windows SAPI"""
        try:
            import win32com.client
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            
            # 设置语音速度和音量
            speaker.Rate = 0  # 语速 (-10 到 10)
            speaker.Volume = 100  # 音量 (0 到 100)
            
            # 查找中文语音
            voices = speaker.GetVoices()
            for i in range(voices.Count):
                voice = voices.Item(i)
                if "chinese" in voice.GetDescription().lower() or "zh" in voice.GetDescription().lower():
                    speaker.Voice = voice
                    break
            
            speaker.Speak(text)
            print("Windows SAPI播放完成")
            return True
            
        except ImportError:
            print("win32com.client不可用")
            return False
        except Exception as e:
            print(f"Windows SAPI播放失败: {e}")
            return False
    
    def _try_pyttsx3(self, text):
        """尝试使用pyttsx3"""
        try:
            if not self.tts_available:
                return False
                
            import pyttsx3
            
            # 创建新的引擎实例
            engine = pyttsx3.init()
            
            # 设置属性
            engine.setProperty('rate', 150)  # 语速
            engine.setProperty('volume', 1.0)  # 音量
            
            # 设置中文语音
            voices = engine.getProperty('voices')
            for voice in voices:
                voice_name = voice.name.lower() if voice.name else ""
                voice_id = voice.id.lower() if voice.id else ""
                if 'chinese' in voice_name or 'zh' in voice_id or 'mandarin' in voice_name:
                    engine.setProperty('voice', voice.id)
                    break
            
            # 播放语音
            engine.say(text)
            engine.runAndWait()
            engine.stop()
            
            # 清理引擎
            del engine
            
            print("pyttsx3播放完成")
            return True
            
        except Exception as e:
            print(f"pyttsx3播放失败: {e}")
            return False
            
    def play_system_beep(self):
        """播放系统提示音"""
        try:
            import winsound
            # 播放系统提示音
            winsound.Beep(1000, 500)  # 频率1000Hz，持续500ms
        except ImportError:
            print("无法播放系统提示音")
            
    def play_congratulations(self):
        """播放庆祝音效"""
        try:
            # 播放庆祝音效
            congratulations_text = self.config.get('audio.voice_files.congratulations', '恭喜完成刷牙！')
            self.play_text_to_speech(congratulations_text)
            
            # 额外的庆祝音效
            self.play_celebration_sound()
            
        except Exception as e:
            print(f"播放庆祝音效失败: {e}")
            
    def play_celebration_sound(self):
        """播放庆祝音效序列"""
        try:
            import winsound
            # 播放一系列上升音调
            frequencies = [523, 659, 784, 1047]  # C, E, G, C (高八度)
            for freq in frequencies:
                winsound.Beep(freq, 200)
        except Exception as e:
            print(f"播放庆祝音效序列失败: {e}")
            
    def play_warning(self, message):
        """播放警告音"""
        try:
            # 播放警告音
            import winsound
            winsound.Beep(800, 300)  # 较低频率的警告音
            
            # 播放警告消息
            if message:
                self.play_text_to_speech(message)
                
        except Exception as e:
            print(f"播放警告音失败: {e}")
            
    def set_volume(self, volume):
        """设置音量"""
        self.volume = max(0.0, min(1.0, volume))
        self.config.set('audio.volume', self.volume)
        self.config.save()
        
        # 更新TTS引擎音量
        if self.tts_engine:
            try:
                self.tts_engine.setProperty('volume', self.volume)
            except Exception as e:
                print(f"设置TTS音量失败: {e}")
        
    def get_volume(self):
        """获取当前音量"""
        return self.volume