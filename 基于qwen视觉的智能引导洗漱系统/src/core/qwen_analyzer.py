"""
QwenVLM视觉分析器
"""

import base64
import cv2
import numpy as np
from openai import OpenAI
from src.utils.config_manager import ConfigManager

class QwenAnalyzer:
    """QwenVLM视觉分析器"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.client = OpenAI(
            api_key=self.config.get('qwen.api_key'),
            base_url=self.config.get('qwen.base_url')
        )
        self.model = self.config.get('qwen.model', 'qwen-vl-max-latest')
        
    def encode_image(self, image):
        """将图像编码为base64"""
        try:
            # 如果是numpy数组，转换为字节
            if isinstance(image, np.ndarray):
                _, buffer = cv2.imencode('.jpg', image)
                image_bytes = buffer.tobytes()
            else:
                # 如果是文件路径
                with open(image, "rb") as image_file:
                    image_bytes = image_file.read()
                    
            return base64.b64encode(image_bytes).decode("utf-8")
        except Exception as e:
            print(f"图像编码失败: {e}")
            return None
            
    def analyze_brushing_action(self, frame):
        """分析刷牙动作"""
        try:
            base64_image = self.encode_image(frame)
            if not base64_image:
                return None
                
            # 构建提示词
            prompt = """
            请分析这张图片中的刷牙动作，重点关注以下几个方面：
            1. 是否正确握持牙刷
            2. 刷牙角度是否正确（45度角）
            3. 刷牙动作是否规范（上下或圆周运动）
            4. 是否覆盖了牙齿的各个部位
            
            请以JSON格式返回分析结果，包含：
            - is_correct: 布尔值，表示动作是否正确
            - score: 0-100的评分
            - warning: 如果动作不正确，给出具体的改进建议
            - detected_action: 检测到的具体动作描述
            """
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": [{"type": "text", "text": "你是一个专业的口腔健康助手，擅长分析刷牙动作的规范性。"}]
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            },
                            {"type": "text", "text": prompt}
                        ]
                    }
                ]
            )
            
            response_text = completion.choices[0].message.content
            
            # 尝试解析JSON响应
            import json
            try:
                result = json.loads(response_text)
                return result
            except json.JSONDecodeError:
                # 如果不是JSON格式，返回基本结果
                return {
                    "is_correct": True,
                    "score": 80,
                    "warning": "",
                    "detected_action": response_text[:100] + "..." if len(response_text) > 100 else response_text
                }
                
        except Exception as e:
            print(f"QwenVLM分析失败: {e}")
            return None
            
    def analyze_image(self, image_path, prompt="请描述这张图片的内容"):
        """通用图像分析"""
        try:
            base64_image = self.encode_image(image_path)
            if not base64_image:
                return None
                
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": [{"type": "text", "text": "You are a helpful assistant."}]
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            },
                            {"type": "text", "text": prompt}
                        ]
                    }
                ]
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            print(f"图像分析失败: {e}")
            return None
            
    def analyze_brushing_frames(self, frames, step_name):
        """直接分析内存中的视频帧（优化版本）"""
        try:
            if not frames or len(frames) == 0:
                print("没有可分析的帧")
                return {
                    "is_correct": False,
                    "score": 0,
                    "feedback": "没有检测到视频帧，请确保摄像头正常工作",
                    "detected_issues": ["无视频帧"],
                    "good_points": []
                }
            
            # 从帧列表中选择关键帧（开始、中间、结束）
            num_frames = len(frames)
            if num_frames >= 3:
                key_frames = [frames[0], frames[num_frames//2], frames[-1]]
            elif num_frames == 2:
                key_frames = [frames[0], frames[-1]]
            else:
                key_frames = frames
            
            # 将帧编码为base64
            encoded_frames = []
            for frame in key_frames:
                encoded_frame = self.encode_image(frame)
                if encoded_frame:
                    encoded_frames.append(encoded_frame)
            
            if not encoded_frames:
                print("帧编码失败")
                return {
                    "is_correct": False,
                    "score": 0,
                    "feedback": "视频帧处理失败，请重新开始",
                    "detected_issues": ["帧编码失败"],
                    "good_points": []
                }
            
            return self._analyze_encoded_frames(encoded_frames, step_name)
                
        except Exception as e:
            print(f"帧分析失败: {e}")
            return {
                "is_correct": False,
                "score": 0,
                "feedback": "视频分析出现错误，请重新开始刷牙",
                "detected_issues": ["分析异常"],
                "good_points": []
            }

    def analyze_brushing_video(self, video_path, step_name):
        """分析刷牙视频（兼容旧接口）"""
        try:
            # 从视频中提取关键帧
            frames = self.extract_video_frames(video_path, num_frames=3)
            if not frames:
                print(f"无法从视频提取帧: {video_path}")
                return {
                    "is_correct": False,
                    "score": 0,
                    "feedback": "无法读取视频文件，请重新录制",
                    "detected_issues": ["视频文件无效"],
                    "good_points": []
                }
            
            # 将帧编码为base64
            encoded_frames = []
            for frame in frames:
                encoded_frame = self.encode_image(frame)
                if encoded_frame:
                    encoded_frames.append(encoded_frame)
            
            if not encoded_frames:
                print("视频帧编码失败")
                return {
                    "is_correct": False,
                    "score": 0,
                    "feedback": "视频帧处理失败，请重新录制",
                    "detected_issues": ["帧编码失败"],
                    "good_points": []
                }
            
            return self._analyze_encoded_frames(encoded_frames, step_name)
                
        except Exception as e:
            print(f"视频分析失败: {e}")
            return {
                "is_correct": False,
                "score": 0,
                "feedback": "视频分析出现错误，请重新开始",
                "detected_issues": ["分析异常"],
                "good_points": []
            }
    
    def _analyze_encoded_frames(self, encoded_frames, step_name):
        """分析已编码的帧（内部方法）"""
        try:
            # 构建针对特定步骤的分析提示词
            step_prompts = {
                "上左": "分析上牙左侧的刷牙动作，检查是否45度角向下刷，是否覆盖牙龈线",
                "上中": "分析上牙中间的刷牙动作，检查是否垂直向下刷，动作是否轻柔",
                "上右": "分析上牙右侧的刷牙动作，检查是否45度角向下刷，是否覆盖牙龈线",
                "下左": "分析下牙左侧的刷牙动作，检查是否45度角向上刷，是否清洁到位",
                "下中": "分析下牙中间的刷牙动作，检查是否垂直向上刷，力度是否适中",
                "下右": "分析下牙右侧的刷牙动作，检查是否45度角向上刷，是否清洁到位"
            }
            
            specific_prompt = step_prompts.get(step_name, "分析刷牙动作的规范性")
            
            prompt = f"""请仔细分析这组刷牙视频帧，重点关注{step_name}区域的刷牙动作。

**重要：如果图片中没有看到牙刷或者没有刷牙动作，请给0分！**

具体要求：{specific_prompt}

评估标准：
1. **首先检查是否有牙刷存在** - 如果没有牙刷，直接给0分
2. 牙刷角度是否正确（45度角）
3. 刷牙方向是否正确（从牙龈向牙尖）
4. 动作幅度是否适中
5. 是否覆盖目标区域
6. 刷牙力度是否合适

评分规则：
- 没有牙刷或没有刷牙动作：0分
- 有牙刷但动作完全错误：10-30分
- 有牙刷动作基本正确：40-70分
- 动作规范标准：80-100分

请以JSON格式返回分析结果：
{{
    "is_correct": true/false,
    "score": 0-100的评分,
    "feedback": "具体的反馈建议",
    "detected_issues": ["检测到的问题列表"],
    "good_points": ["做得好的地方"]
}}"""
            
            # 构建消息内容
            content = []
            for encoded_frame in encoded_frames:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{encoded_frame}"}
                })
            content.append({"type": "text", "text": prompt})
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": [{"type": "text", "text": f"你是一个专业的口腔健康助手，正在严格分析{step_name}区域的刷牙动作规范性。如果没有看到牙刷，必须给0分。"}]
                    },
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                stream=False,  # 禁用流式接收以提高性能
                timeout=15,    # 增加到15秒超时，确保分析准确
                max_tokens=300  # 增加返回长度以获得更详细分析
            )
            
            response_text = completion.choices[0].message.content
            print(f"QwenVLM原始响应: {response_text}")
            
            # 尝试解析JSON响应
            import json
            try:
                result = json.loads(response_text)
                print(f"QwenVLM分析结果: {result}")
                
                # 验证结果的合理性
                score = result.get('score', 0)
                if score < 0:
                    result['score'] = 0
                elif score > 100:
                    result['score'] = 100
                    
                return result
            except json.JSONDecodeError:
                print("JSON解析失败，尝试提取关键信息")
                # 如果不是JSON格式，尝试从文本中提取信息
                score = 0
                is_correct = False
                
                # 查找分数
                import re
                score_match = re.search(r'(\d+)分', response_text)
                if score_match:
                    score = int(score_match.group(1))
                
                # 查找是否正确
                if any(word in response_text for word in ['正确', '规范', '标准', '很好']):
                    is_correct = True
                
                return {
                    "is_correct": is_correct,
                    "score": score,
                    "feedback": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                    "detected_issues": [],
                    "good_points": []
                }
                
        except Exception as e:
            print(f"帧分析失败: {e}")
            # 分析失败时返回0分，而不是默认分数
            return {
                "is_correct": False,
                "score": 0,
                "feedback": "视频分析失败，请确保摄像头正常工作并重新开始刷牙",
                "detected_issues": ["分析服务暂时不可用"],
                "good_points": []
            }
    
    def extract_video_frames(self, video_path, num_frames=3):
        """从视频中提取关键帧"""
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print(f"无法打开视频文件: {video_path}")
                return []
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames == 0:
                return []
            
            # 均匀提取帧
            frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
            frames = []
            
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if ret:
                    frames.append(frame)
            
            cap.release()
            return frames
            
        except Exception as e:
            print(f"视频帧提取失败: {e}")
            return []

    def get_weather_info(self, location="北京"):
        """获取天气信息（通过文本对话）"""
        try:
            prompt = f"请提供{location}今天的天气情况，包括温度、天气状况和穿衣建议。请用简洁的中文回答。"
            
            completion = self.client.chat.completions.create(
                model="qwen-max",  # 使用文本模型
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个天气助手，提供准确的天气信息和生活建议。"
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ]
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            print(f"天气查询失败: {e}")
            return "暂时无法获取天气信息"