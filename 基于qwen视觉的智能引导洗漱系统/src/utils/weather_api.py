"""
天气API工具类 - 获取东莞天气信息
"""

import requests
import json
from datetime import datetime

class WeatherAPI:
    """天气API类"""
    
    def __init__(self):
        # 使用免费的天气API服务
        self.api_key = "your_api_key_here"  # 可配置API密钥
        self.city = "东莞"
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        
        # 备用API - 使用免费的中国天气API
        self.backup_api_url = "http://wthrcdn.etouch.cn/weather_mini"
        
    def get_weather_info(self):
        """获取天气信息"""
        try:
            # 尝试使用备用API（免费，无需密钥）
            weather_data = self._get_weather_from_backup_api()
            if weather_data:
                return weather_data
                
            # 如果备用API失败，返回默认信息
            return self._get_default_weather()
            
        except Exception as e:
            print(f"获取天气信息失败: {e}")
            return self._get_default_weather()
    
    def _get_weather_from_backup_api(self):
        """从备用API获取天气"""
        try:
            params = {'city': self.city}
            response = requests.get(self.backup_api_url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 1000:  # 成功状态码
                    weather_info = data['data']
                    current = weather_info['forecast'][0]  # 今日天气
                    
                    return {
                        'city': weather_info['city'],
                        'temperature': current['high'].replace('高温 ', '').replace('℃', ''),
                        'low_temp': current['low'].replace('低温 ', '').replace('℃', ''),
                        'weather': current['type'],
                        'description': f"{current['type']}，{current['high']}，{current['low']}",
                        'icon': self._get_weather_icon(current['type']),
                        'update_time': datetime.now().strftime("%H:%M")
                    }
        except Exception as e:
            print(f"备用API获取天气失败: {e}")
            
        return None
    
    def _get_default_weather(self):
        """获取默认天气信息"""
        return {
            'city': '东莞',
            'temperature': '25',
            'low_temp': '18',
            'weather': '多云',
            'description': '多云，25℃，18℃',
            'icon': '☁️',
            'update_time': datetime.now().strftime("%H:%M")
        }
    
    def _get_weather_icon(self, weather_type):
        """根据天气类型获取图标"""
        weather_icons = {
            '晴': '☀️',
            '多云': '☁️',
            '阴': '☁️',
            '小雨': '🌦️',
            '中雨': '🌧️',
            '大雨': '🌧️',
            '雷阵雨': '⛈️',
            '雪': '❄️',
            '雾': '🌫️',
            '霾': '🌫️'
        }
        
        for key in weather_icons:
            if key in weather_type:
                return weather_icons[key]
        
        return '🌤️'  # 默认图标
    
    def get_weather_voice_text(self):
        """获取天气语音播报文本"""
        weather_info = self.get_weather_info()
        
        voice_text = f"今天{weather_info['city']}天气{weather_info['weather']}，"
        voice_text += f"最高温度{weather_info['temperature']}度，"
        voice_text += f"最低温度{weather_info['low_temp']}度。"
        
        # 根据天气给出建议
        weather = weather_info['weather']
        if '雨' in weather:
            voice_text += "今天有雨，记得带伞。"
        elif '晴' in weather:
            voice_text += "天气晴朗，适合外出。"
        elif '雪' in weather:
            voice_text += "今天下雪，注意保暖。"
        
        return voice_text